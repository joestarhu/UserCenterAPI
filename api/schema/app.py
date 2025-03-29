from dataclasses import asdict
from sqlalchemy import select, and_
from jhu.orm import ORM, Session, ORMFormatRule
from api.deps import Pagination
from api.model.role import Role
from api.model.app import App, AppService
from api.model.permission import AppRole


class AppAPI:
    @staticmethod
    def get_app_list(
        session: Session,
        pagination: Pagination,
        app_name: str = None,
        select_fields: list = None
    ) -> list:
        """获取应用列表信息
        """
        select_fields = [
            App.id,
            App.app_uuid,
            App.app_name,
            App.app_desc,
            App.created_at,
            App.updated_at
        ] if not select_fields else select_fields

        expressions = [expression for condition, expression in [
            (app_name is not None, App.app_name.ilike(f"%{app_name}%")),
        ] if condition]

        stmt = select(
            *select_fields
        ).where(
            App.is_deleted == False,
            *expressions
        )

        return ORM.pagination(
            session, stmt, **asdict(pagination), order=[App.updated_at.desc()])

    @staticmethod
    def get_app_detail(
        session: Session,
        app_uuid: str
    ) -> dict:
        """获取应用详情
        """
        stmt = select(
            App.app_name,
            App.app_desc,
            App.created_at,
            App.updated_at
        ).where(
            App.is_deleted == False,
            App.app_uuid == app_uuid
        )

        return ORM.one(session, stmt)

    @staticmethod
    def get_app_service(session: Session, app_uuid: int) -> list:
        """获取应用服务信息
        """
        stmt = select(
            AppService.service_identify,
            AppService.service_name,
            AppService.is_enable
        ).join(
            App, App.id == AppService.app_id
        ).where(
            App.is_deleted == False,
            AppService.is_deleted == False,
            App.app_uuid == app_uuid
        )

        return ORM.all(session, stmt)

    @staticmethod
    def get_app_permission(session: Session, pagination: Pagination, app_id: int) -> list:
        """获取应用权限
        """
        stmt = select(
            AppService.id,
            AppService.service_identify,
            AppService.service_name
        ).join(
            App, App.id == AppService.app_id
        ).where(
            App.is_deleted == False,
            App.id == app_id
        )

        return ORM.pagination(session, stmt, **asdict(pagination), order=[AppService.service_identify])

    @staticmethod
    def get_app_role_list(session: Session, app_id: int) -> list:
        stmt = select(
            AppRole.role_id,
            Role.role_name,
            Role.role_status,
        ).join(
            AppRole, Role.id == AppRole.role_id, isouter=True
        ).where(
            Role.is_deleted == False,
            AppRole.is_deleted == False,
            AppRole.app_id == app_id
        ).group_by(
            AppRole.role_id, Role.role_name, Role.role_status, Role.created_at
        )

        return ORM.all(session, stmt)

    @staticmethod
    def get_app_role_permission(session: Session, pagination: Pagination, app_id: int, role_id: int):
        stmt = select(
            AppRole.service_identify,
            AppService.service_name,
        ).join(
            AppService, and_(AppService.app_id == AppRole.app_id,
                             AppService.service_identify == AppRole.service_identify)
        ).where(
            AppService.is_deleted == False,
            AppRole.app_id == app_id,
            AppRole.role_id == role_id
        )

        return ORM.ALL(session, stmt, **asdict(pagination))
