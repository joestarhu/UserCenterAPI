from dataclasses import asdict
from jhu.orm import ORM, ORMFormatRule
from sqlalchemy import select, update, or_
from sqlalchemy.orm import Session
from api.config import settings
from api.deps import Pagination
from api.errcode import APIErr
from api.security import server_aes_api, hash_api, create_uuid
from api.model.user import User, UserAuth, OptUserStatus, OptUserAuthType
from api.model.org import Org, OrgUser


fmt_rules = [
    ORMFormatRule("phone", server_aes_api.phone_decrypt),
]


def check_account_unique(session: Session, user_uuid: str, account: str = None, phone_enc: str = None, is_insert: bool = False) -> APIErr:
    r"""判断账号是否重复
    """
    if is_insert:
        stmt = select(User.user_uuid, User.account, User.phone_enc).where(
            User.is_deleted == False)
    else:
        stmt = select(User.account, User.phone_enc).where(
            User.is_deleted == False,
            User.user_uuid != user_uuid)

    # uuid,账号,手机号唯一
    expressions = [expression for condition, expression in (
        (account, User.account == account),
        (phone_enc, User.phone_enc == phone_enc),
        (is_insert, User.user_uuid == user_uuid),
    ) if condition]

    stmt = stmt.where(or_(*expressions))

    for row in ORM.mapping(session, stmt):
        if account and row["account"] == account:
            return APIErr.ACCOUNT_EXISTSED
        if phone_enc and row["phone_enc"] == phone_enc:
            return APIErr.PHONE_EXISTED
        if is_insert and row["user_uuid"] == user_uuid:
            return APIErr.USER_UUID_EXISTED

    return APIErr.NO_ERROR


def check_superadmin_account(session: Session, user_uuid: str) -> bool:
    r"""判断是否是超级管理员帐户
    """
    stmt = select(
        User.id
    ).join(
        Org, User.user_uuid == Org.org_owner
    ).where(
        Org.is_deleted == False,
        Org.is_admin == True,
        User.is_deleted == False,
        User.user_uuid == user_uuid
    )

    return ORM.counts(session, stmt) > 0


class UserAPI:
    @staticmethod
    def get_account_auth_info(
        session: Session,
        account: str,
        auth_type: OptUserAuthType = OptUserAuthType.PASSWORD,
        auth_identify: str = ""
    ) -> dict | None:
        r"""获取账号认证信息

        Parameters:
            session:数据库会话
            account:账号
            auth_type:认证类型,默认为密码
            auth_identify:认证类型标识,默认为空

        Returns:
            None:无数据
            Dict:用户认证信息{
                user_uuid:用户uuid
                user_status:用户状态
                auth_value:账号认证值
            }
        """
        stmt = select(
            User.user_uuid,
            User.user_status,
            UserAuth.auth_value
        ).join(
            UserAuth, User.user_uuid == UserAuth.user_uuid
        ).where(
            User.is_deleted == False,
            UserAuth.is_deleted == False,
            User.account == account,
            UserAuth.auth_type == auth_type.value,
            UserAuth.auth_identify == auth_identify
        )

        return ORM.one(session, stmt)

    @staticmethod
    def get_user_org_list(
        session: Session,
        user_uuid: str,
        select_fields: list = None,
    ) -> list[dict]:
        r"""获取用户的组织信息
        """
        select_fields = [
            OrgUser.org_uuid,
            OrgUser.org_user_status,
        ] if not select_fields else select_fields

        stmt = select(
            *select_fields
        ).join(
            Org, OrgUser.org_uuid == Org.org_uuid
        ).where(
            Org.is_deleted == False,
            OrgUser.is_deleted == False,
            OrgUser.user_uuid == user_uuid
        )

        return ORM.all(session, stmt)

    @staticmethod
    def get_account_list(
        session: Session,
        pagination: Pagination,
        account: str = None,
        nickname: str = None,
        user_status: OptUserStatus = None,
        select_fields: list = None
    ):
        select_fields = [
            User.user_uuid,
            User.account,
            User.nickname,
            User.phone_enc.label("phone"),
            User.user_status,
            User.created_at,
            User.updated_at
        ] if not select_fields else select_fields

        expresions = [expression for condition, expression in (
            (account is not None, User.account.ilike(f"%{account}%")),
            (nickname is not None, User.nickname.ilike(f"%{nickname}%")),
            (user_status is not None, User.user_status == user_status)
        ) if condition]

        stmt = select(
            *select_fields
        ).where(
            User.is_deleted == False,
            *expresions
        )

        return ORM.pagination(session,
                              stmt,
                              **asdict(pagination),
                              order=[User.created_at.desc()],
                              format_rules=fmt_rules)

    @staticmethod
    def get_account_detail(
        session: Session,
        user_uuid: str,
        select_fields: list = None
    ):
        r"""获取账户详情
        """

        select_fields = [
            User.account,
            User.nickname,
            User.phone_enc.label("phone"),
            User.user_status,
            User.avatar_url,
            User.created_at,
            User.updated_at
        ] if not select_fields else select_fields

        stmt = select(
            *select_fields
        ).where(
            User.is_deleted == False,
            User.user_uuid == user_uuid
        )

        return ORM.one(session, stmt, fmt_rules)

    @staticmethod
    def create_account(
            session: Session,
            user: User,
            user_auth: UserAuth = None
    ) -> APIErr:
        r"""创建账号,user_uuid会自动生成,不用输入
        """
        user_uuid = create_uuid()
        # 唯一性判断
        if (rsp := check_account_unique(session, user_uuid, user.account, user.phone_enc, is_insert=True)) != APIErr.NO_ERROR:
            return rsp
        user.user_uuid = user_uuid

        # 认证类型设定
        if user_auth:
            user_auth.user_uuid = user_uuid
        else:
            user_auth = UserAuth(user_uuid=user_uuid,
                                 auth_value=hash_api.hash(settings.default_passwd))

        try:
            session.add_all([user, user_auth])
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR

    @staticmethod
    def update_account(
        session: Session,
        user_uuid: str,
        nickname: str,
        user_status: OptUserStatus
    ) -> APIErr:
        r"""修改账号
        """

        # 超级管理员不允许修改
        if check_superadmin_account(session, user_uuid):
            return APIErr.SUPERADMIN_PROTECT

        stmt = update(User).where(User.user_uuid == user_uuid).values(
            nickname=nickname,
            user_status=user_status.value
        )

        try:
            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR

    @staticmethod
    def delete_account(
            session: Session,
            user_uuid: str
    ) -> APIErr:
        r"""删除账号
        """
        # 超级管理员不允许删除
        if check_superadmin_account(session, user_uuid):
            return APIErr.SUPERADMIN_PROTECT

        try:
            # 释放账号
            for stmt in (update(User).where(User.user_uuid == user_uuid).values(is_deleted=True, account=user_uuid),
                         update(UserAuth).where(UserAuth.user_uuid ==
                                                user_uuid).values(is_deleted=True)
                         ):
                session.execute(stmt)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR
