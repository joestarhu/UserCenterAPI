
# class OrgAPI:
#     @staticmethod
#     def get_user_org_list(session: Session, user_uuid: str, pagination: Pagination, *outputs_fields) -> list:
#         """获取用户的组织信息, outputs_fields 仅允许输入 model.org下的Org和OrgUser字段
#         """

#         stmt = select(
#             *outputs_fields
#             # Org.org_uuid,
#             # Org.org_owner
#         ).join_from(
#             Org, OrgUser, OrgUser.org_uuid == Org.org_uuid
#         ).where(and_(
#             Org.is_deleted == False,
#             Org.org_status == OptOrgStatus.ENABLE,
#             OrgUser.org_user_status == OptOrgUserStatus.ENABLE,
#             OrgUser.user_uuid == user_uuid
#         ))

#         return ORM.pagination(session, stmt, **asdict(pagination))

#     @staticmethod
#     def get_org_list(session: Session, pagination: Pagination, org_name: str = None, org_status: OptOrgStatus = None) -> list:
#         """
#         """

#         expressions = (expression for condition, expression in (
#             (org_name is not None, Org.org_name.ilike(f"%{org_name}%")),
#             (org_status is not None, Org.org_status == org_status),
#         ) if condition)

#         stmt = select(
#             Org.org_uuid,
#             Org.org_name,
#             Org.org_status,
#             Org.org_owner,
#             User.nickname,
#             Org.created_at,
#             Org.updated_at
#         ).join(
#             User, Org.org_owner == User.user_uuid, isouter=True
#         ).where(
#             Org.is_deleted == False,
#             *expressions
#         )

#         return ORM.pagination(session, stmt, **asdict(pagination), order=[Org.updated_at.desc()])

#     @staticmethod
#     def get_org_user_list(session: Session, pagination: Pagination, org_uuid: str) -> list:
#         """
#         """

#         stmt = select(
#             OrgUser.org_user_nickname,
#             OrgUser.created_at,
#             OrgUser.updated_at,
#             OrgUser.org_user_status,
#             User.account,
#             User.user_status,
#             User.is_deleted
#         ).join(
#             Org, Org.org_uuid == OrgUser.org_uuid
#         ).join(
#             User, User.user_uuid == OrgUser.user_uuid
#         ).where(
#             Org.is_deleted == False,
#             # User.is_deleted == False,
#             Org.org_uuid == org_uuid
#         )

#         return ORM.pagination(session, stmt, **asdict(pagination), order=[OrgUser.updated_at.desc()])

#     @staticmethod
#     def get_org_user_detial(session: Session, org_uuid: str, user_uuid: str) -> dict:
#         """获取组织用户详情
#         """

#         stmt = select(
#             OrgUser.org_user_nickname,
#             OrgUser.org_avatar_url,
#             User.phone_enc.label("phone")
#         ).join(
#             Org, Org.org_uuid == OrgUser.org_uuid
#         ).join(
#             User, OrgUser.user_uuid == User.user_uuid
#         ).where(
#             Org.is_deleted == False,
#             User.is_deleted == False,
#             OrgUser.org_uuid == org_uuid,
#             OrgUser.user_uuid == user_uuid
#         )

#         return ORM.one(session, stmt, fmt_rules)

from dataclasses import asdict
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from jhu.orm import ORM, ORMFormatRule
from api.deps import Pagination
from api.errcode import APIErr
from api.security import server_aes_api, create_org_uuid
from api.model.user import User
from api.model.org import Org, OrgUser, OptOrgStatus
from api.schema.user import UserAPI


fmt_rules = [
    ORMFormatRule("phone", server_aes_api.phone_decrypt),
]


def check_org_unique(session: Session, org_uuid: str, org_name: str = None, is_insert=False) -> APIErr:
    """判断组织的唯一性
    """
    check_rules = {
        Org.org_uuid.name: (is_insert, Org.org_uuid == org_uuid, APIErr.ORG_UUID_EXISTED),
        Org.org_name.name: (org_name, Org.org_name == org_name, APIErr.ORG_NAME_EXISTED),
    }

    if is_insert:
        stmt = select(Org.org_uuid, Org.org_name)
    else:
        stmt = select(Org.org_name).where(Org.org_uuid != org_uuid)

    stmt = stmt.where(Org.is_deleted == False)
    expressions = [expression for condition, expression,
                   _ in check_rules.values() if condition]
    stmt = stmt.where(or_(*expressions))

    for row in ORM.mapping(session, stmt):
        for field, (condition, _, err) in check_rules.items():
            if condition and row[field] == condition:
                return err
    return APIErr.NO_ERROR


class OrgAPI:
    @staticmethod
    def get_org_user_detail(
        session: Session,
        org_uuid: str,
        user_uuid: str,
        select_fields: list = None,
    ) -> dict:
        r"""获取组织用户详情
        """
        select_fields = [
            OrgUser.org_user_nickname,
            OrgUser.org_avatar_url,
            OrgUser.org_user_status,
            OrgUser.created_at,
            OrgUser.updated_at,
            User.account,
            User.phone_enc.label("phone"),
            User.user_status,
            Org.org_name,
            Org.org_status
        ] if not select_fields else select_fields

        stmt = select(
            *select_fields,
        ).join(
            Org, OrgUser.org_uuid == Org.org_uuid
        ).join(
            User, OrgUser.user_uuid == User.user_uuid
        ).where(
            Org.is_deleted == False,
            OrgUser.is_deleted == False,
            User.is_deleted == False,
            OrgUser.org_uuid == org_uuid,
            OrgUser.user_uuid == user_uuid
        )

        return ORM.one(session, stmt, fmt_rules)

    @staticmethod
    def get_org_list(
        session: Session,
        pagination: Pagination,
        org_name: str = None,
        org_status: OptOrgStatus = None,
        select_fields: list = None
    ):
        select_fields = [
            Org.org_uuid,
            Org.org_name,
            Org.org_owner_uuid,
            Org.org_status,
            Org.created_at,
            Org.updated_at,
            User.nickname,
        ] if not select_fields else select_fields

        expressions = [expression for condition, expression in (
            (org_name, Org.org_name.ilike(f"%{org_name}%")),
            (org_status is not None, Org.org_status == org_status),
        ) if condition]

        stmt = select(
            *select_fields
        ).join(
            User, Org.org_owner_uuid == User.user_uuid
        ).where(
            Org.is_deleted == False,
            *expressions
        )

        return ORM.pagination(session, stmt, **asdict(pagination), order=[Org.created_at.desc()])

    @staticmethod
    def get_org_detail(
        session: Session,
        org_uuid: str,
        select_fields: list = None
    ):
        select_fields = [
            Org.org_uuid,
            Org.org_name,
            Org.org_status,
            Org.created_at,
            Org.updated_at,
            User.nickname
        ] if not select_fields else select_fields

        stmt = select(
            *select_fields
        ).join(
            User, Org.org_owner_uuid == User.user_uuid
        ).where(
            Org.is_deleted == False,
            Org.org_uuid == org_uuid
        )

        return ORM.one(session, stmt)

    @staticmethod
    def get_org_user_list(
        session: Session,
        pagination: Pagination,
        org_uuid: str
    ):
        # 获取组织用户详情
        stmt = select(
            OrgUser.org_user_nickname,
            OrgUser.org_user_status,
            User.account,
            User.account_status
        ).join(
            User, OrgUser.user_uuid == User.user_uuid
        ).join(
            Org, OrgUser.org_uuid == Org.org_uuid
        ).where(
            OrgUser.is_deleted == False,
            OrgUser.org_uuid == org_uuid,
            User.is_deleted == False,
            Org.is_deleted == False
        )

        return ORM.pagination(session, stmt, **asdict(pagination))

    @staticmethod
    def create_org(session: Session, org: Org) -> APIErr:
        """创建组织
        """
        org_uuid = create_org_uuid()
        if (result := check_org_unique(session, org_uuid, org.org_name, True)) != APIErr.NO_ERROR:
            return result
        org.org_uuid = org_uuid

        owner_info = UserAPI.get_account_detail(
            session, org.org_owner_uuid,
            [User.id, User.nickname, User.avatar_url])

        if owner_info is None:
            return APIErr.ORG_OWNER_NOT_EXISTED

        try:
            session.add(org)
            session.flush()

            org_user = OrgUser(
                org_id=org.id,
                user_id=owner_info["id"],
                org_user_nickname=owner_info["nickname"],
                org_avatar_url=owner_info["avatar_url"]
            )

            session.add(org_user)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR
