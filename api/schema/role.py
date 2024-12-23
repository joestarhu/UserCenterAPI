from dataclasses import asdict
from sqlalchemy import select
from jhu.orm import ORM, Session
from api.deps import Pagination
from api.model.role import Role, OptRoleStatus


class RoleAPI:
    @staticmethod
    def get_role_list(session: Session, pagination: Pagination, role_name: str = None, role_status: OptRoleStatus = None) -> list:
        """获取角色列表
        """
        expressions = [expression for condition, expression in [
            (role_name is not None, Role.role_name.ilike(f"%{role_name}%")),
            (role_status is not None, Role.role_status == role_status)
        ] if condition]

        stmt = select(
            Role.id,
            Role.role_name,
            Role.role_desc,
            Role.created_at,
            Role.updated_at,
            Role.role_status
        ).where(
            Role.is_deleted == False,
            Role.role_org_uuid == "",
            *expressions
        )

        data = ORM.pagination(
            session, stmt, **asdict(pagination), order=[Role.updated_at.desc()])
        return data
