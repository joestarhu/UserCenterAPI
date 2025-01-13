from dataclasses import asdict
from sqlalchemy import select, update
from jhu.orm import ORM, Session
from api.deps import Pagination
from api.errcode import APIErr
from api.model.role import Role, OptRoleStatus


def check_role_unique(session: Session, role_name: str, role_org_uuid: str, role_id: int = None) -> APIErr:
    """判断角色是否唯一, 在同一个组织下,角色名必须唯一
    """
    stmt = select(Role.id).where(
        Role.is_deleted == False,
        Role.role_name == role_name,
        Role.role_org_uuid == role_org_uuid
    )

    if role_id:
        stmt = stmt.where(Role.id != role_id)

    if ORM.counts(session, stmt) > 0:
        return APIErr.ROLE_EXISTED

    return APIErr.NO_ERROR


class RoleAPI:
    @staticmethod
    def get_role_list(
        session: Session,
        pagination: Pagination,
        role_name: str = None,
        role_status: OptRoleStatus = None,
        select_fields: list = None
    ):
        select_fields = [
            Role.id,
            Role.role_name,
            Role.role_desc,
            Role.role_status,
            Role.created_at,
            Role.updated_at
        ] if not select_fields else select_fields

        expressions = [expression for condition, expression in (
            (role_name, Role.role_name.ilike(f"%{role_name}%")),
            (role_status is not None, Role.role_status == role_status),
        )if condition]

        stmt = select(
            *select_fields
        ).where(
            Role.is_deleted == False,
            Role.role_org_uuid == "",
            *expressions
        )

        return ORM.pagination(session, stmt, **asdict(pagination), order=[Role.updated_at.desc()])

    @staticmethod
    def get_role_detail(
        session: Session,
        role_id: int,
        role_org_uuid: str
    ) -> dict:
        """获取角色详情
        """
        stmt = select(
            Role.role_name,
            Role.role_desc,
            Role.role_status,
            Role.created_at,
            Role.updated_at
        ).where(
            Role.is_deleted == False,
            Role.id == role_id,
            Role.role_org_uuid == role_org_uuid
        )
        return ORM.one(session, stmt)

    @staticmethod
    def create_role(
        session: Session,
        role: Role
    ) -> APIErr:
        """创建角色
        """
        if (result := check_role_unique(session, role.role_name, role.role_org_uuid)) != APIErr.NO_ERROR:
            return result

        try:
            session.add(role)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR

    @staticmethod
    def update_role(
        session: Session,
        role_id: int,
        role_name: str,
        role_desc: str,
        role_status: OptRoleStatus,
        role_org_uuid: str = ""
    ) -> APIErr:
        """修改角色
        """
        if (result := check_role_unique(session, role_name, role_org_uuid, role_id)) != APIErr.NO_ERROR:
            return result

        try:
            stmt = update(Role).where(Role.id == role_id).values(
                role_name=role_name, role_desc=role_desc, role_status=role_status)
            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR

    @staticmethod
    def delete_role(
        session: Session,
        role_id: int
    ) -> APIErr:
        try:
            stmt = update(Role).where(
                Role.id == role_id).values(is_deleted=True)
            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        return APIErr.NO_ERROR
