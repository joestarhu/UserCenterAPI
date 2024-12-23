from dataclasses import asdict
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete, and_, or_
from jhu.orm import ORM, Session, ORMFormatRule
from api.deps import Pagination
from api.errcode import APIErr
from api.config import settings
from api.security import server_aes_api, hash_api, create_uuid
from api.model.user import User, UserAuth, OptUserStatus, OptUserAuthType
from api.model.org import Org


# 格式化规则
fmt_rules = [
    ORMFormatRule("phone", server_aes_api.phone_decrypt),
]


class AccountCreate(BaseModel):
    account: str = Field(description="账号",
                         pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
                         max_length=User.account.type.length)
    nickname: str = Field(description="昵称",
                          min_length=1,
                          max_length=User.nickname.type.length)
    phone: str = Field(default="",
                       description="手机号",
                       pattern=r"^1[3-9]\d{9}$|^$")
    user_status: OptUserStatus = Field(default=OptUserStatus.ENABLE,
                                       description="用户状态")


class AccountDelete(BaseModel):
    user_uuid: str = Field(description="用户UUID")


class AccountUpdate(BaseModel):
    user_uuid: str = Field(description="用户UUID")
    nickname: str = Field(description="昵称",
                          min_length=1,
                          max_length=User.nickname.type.length)
    user_status: OptUserStatus = Field(description="用户状态")


def check_superadmin_account(session: Session, user_uuid: str) -> bool:
    """判断是否是超级管理员帐户
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


def check_account_unique(session: Session, account: str = None, phone_enc: str = None, user_uuid: str = None) -> APIErr:
    """判断用户账户是否唯一
    """

    stmt = select(User.account, User.phone_enc).where(User.is_deleted == False)
    if user_uuid:
        stmt = stmt.where(User.user_uuid != user_uuid)

    expressions_gen = (expression for condition, expression in (
        (account, User.account == account),
        (phone_enc, User.phone_enc == phone_enc)
    ) if condition)

    stmt = stmt.where(or_(*expressions_gen))

    ds = ORM.all(session, stmt)
    for row in ds:
        if account and account == row["account"]:
            return APIErr.ACCOUNT_EXISTSED
        if phone_enc and phone_enc == row["phone_enc"]:
            return APIErr.PHONE_EXISTED

    return APIErr.NO_ERROR


class UserAPI:
    @staticmethod
    def get_user_auth_info(session: Session, account: str, auth_type: OptUserAuthType = OptUserAuthType.PASSWORD, auth_identify: str = "") -> dict:
        """获取用户认证信息
        """
        stmt = select(
            User.user_uuid,
            User.user_status,
            UserAuth.auth_value
        ).join(
            UserAuth, User.user_uuid == UserAuth.user_uuid
        ).where(
            User.is_deleted == False,
            User.account == account,
            UserAuth.auth_type == auth_type.value,
            UserAuth.auth_identify == auth_identify
        )

        return ORM.one(session, stmt)

    @staticmethod
    def get_account_list(session: Session, pagination: Pagination, account: str = None, nickname: str = None, user_status: OptUserStatus = None) -> dict:
        """获取账号列表
        """
        expresions = (expression for condition, expression in (
            (account is not None, User.account.ilike(f"%{account}%")),
            (nickname is not None, User.nickname.ilike(f"%{nickname}%")),
            (user_status is not None, User.user_status == user_status)
        ) if condition)

        stmt = select(
            User.user_uuid,
            User.account,
            User.nickname,
            User.phone_enc.label("phone"),
            User.user_status,
            User.created_at,
            User.updated_at
        ).where(
            User.is_deleted == False,
            *expresions
        )

        return ORM.pagination(
            session,
            stmt,
            **asdict(pagination),
            order=[User.created_at.desc()],
            format_rules=fmt_rules
        )

    @staticmethod
    def get_account_detail(session: Session, user_uuid: str) -> dict:
        """获取账户详情
        """
        stmt = select(
            User.account,
            User.nickname,
            User.phone_enc.label("phone"),
            User.user_status,
            User.avatar_url,
            User.created_at,
            User.updated_at
        ).where(
            User.is_deleted == False,
            User.user_uuid == user_uuid
        )

        return ORM.one(session, stmt, fmt_rules)

    @staticmethod
    def create_account(session: Session, data: AccountCreate) -> APIErr:
        """新建账号
        """

        # 手机号加密处理
        phone_enc = server_aes_api.phone_encrypt(
            data.phone) if data.phone else ""

        try:
            # 唯一性判断
            if (result := check_account_unique(session, data.account, phone_enc)) != APIErr.NO_ERROR:
                return result

            # 构建用户和用户认证
            user_uuid = create_uuid()

            user = User(
                user_uuid=user_uuid,
                phone_enc=phone_enc,
                **data.model_dump(exclude=["phone"])
            )

            user_auth = UserAuth(
                user_uuid=user_uuid,
                auth_value=hash_api.hash(settings.default_passwd),
            )

            session.add_all([user, user_auth])
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR

    @staticmethod
    def update_account(session: Session, data: AccountUpdate) -> APIErr:
        """更新账号信息
        """
        # 帐户如果是超级管理员则不允许被修改
        if check_superadmin_account(session, data.user_uuid):
            return APIErr.SUPERADMIN_PROTECT

        try:
            stmt = update(User).where(
                User.user_uuid == data.user_uuid
            ).values(
                nickname=data.nickname,
                user_status=data.user_status
            )

            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR

    @staticmethod
    def delete_account(session: Session, user_uuid: str) -> APIErr:
        """删除账户
        逻辑删除账号信息(释放账号名称,手机号)
        物理删除所有认证信息
        """

        # 判断数据是否存在,如果不存在,直接返回
        stmt = select(User.id).where(
            User.user_uuid == user_uuid,
            User.is_deleted == False
        )
        if ORM.counts(session, stmt) == 0:
            return APIErr.NO_ERROR

        # 帐户如果是超级管理员则不允许被删除
        if check_superadmin_account(session, user_uuid):
            return APIErr.SUPERADMIN_PROTECT

        try:
            stmt_gen = (
                update(User).where(
                    User.user_uuid == user_uuid).values(
                        is_deleted=True,
                        account=user_uuid,
                        phone_enc=user_uuid
                ),
                delete(UserAuth).where(UserAuth.user_uuid == user_uuid)
            )

            for stmt in stmt_gen:
                session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR
