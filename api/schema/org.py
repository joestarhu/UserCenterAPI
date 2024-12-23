from dataclasses import asdict
from sqlalchemy import select, and_
from jhu.orm import ORM, Session
from api.deps import Pagination
from api.model.user import User
from api.model.org import Org, OrgUser, OptOrgStatus, OptOrgUserStatus


class OrgAPI:
    @staticmethod
    def get_user_org_list(session: Session, user_uuid: str, pagination: Pagination, *outputs_fields) -> list:
        """获取用户的组织信息, outputs_fields 仅允许输入 model.org下的Org和OrgUser字段
        """

        stmt = select(
            *outputs_fields
            # Org.org_uuid,
            # Org.org_owner
        ).join_from(
            Org, OrgUser, OrgUser.org_uuid == Org.org_uuid
        ).where(and_(
            Org.is_deleted == False,
            Org.org_status == OptOrgStatus.ENABLE,
            OrgUser.org_user_status == OptOrgUserStatus.ENABLE,
            OrgUser.user_uuid == user_uuid
        ))

        return ORM.pagination(session, stmt, **asdict(pagination))

    @staticmethod
    def get_org_list(session: Session, pagination: Pagination, org_name: str = None, org_status: OptOrgStatus = None) -> list:
        """
        """

        expressions = (expression for condition, expression in (
            (org_name is not None, Org.org_name.ilike(f"%{org_name}%")),
            (org_status is not None, Org.org_status == org_status),
        ) if condition)

        stmt = select(
            Org.org_uuid,
            Org.org_name,
            Org.org_status,
            Org.org_owner,
            User.nickname,
            Org.created_at,
            Org.updated_at
        ).join(
            User, Org.org_owner == User.user_uuid, isouter=True
        ).where(
            Org.is_deleted == False,
            *expressions
        )

        return ORM.pagination(session, stmt, **asdict(pagination), order=[Org.updated_at.desc()])

    @staticmethod
    def get_org_user_list(session: Session, pagination: Pagination, org_uuid: str) -> list:
        """
        """

        stmt = select(
            OrgUser.org_user_nickname,
            OrgUser.created_at,
            OrgUser.updated_at,
            OrgUser.org_user_status,
            User.account,
            User.user_status,
            User.is_deleted
        ).join(
            Org, Org.org_uuid == OrgUser.org_uuid
        ).join(
            User, User.user_uuid == OrgUser.user_uuid
        ).where(
            Org.is_deleted == False,
            # User.is_deleted == False,
            Org.org_uuid == org_uuid
        )

        return ORM.pagination(session, stmt, **asdict(pagination), order=[OrgUser.updated_at.desc()])
