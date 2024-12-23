from dataclasses import asdict
from sqlalchemy import select
from jhu.orm import ORM, Session, ORMFormatRule
from api.deps import Pagination
from api.model.role import Role
from api.model.app import App, AppService, AppRole


class AppAPI:
    @staticmethod
    def get_app_list(session: Session, pagination: Pagination, app_name: str = None) -> list:

        expressions = [expression for condition, expression in [
            (app_name is not None, App.app_name.ilike(f"%{app_name}%")),
        ] if condition]

        stmt = select(
            App.id,
            App.app_name,
            App.app_desc,
            App.created_at,
            App.updated_at
        ).where(
            App.is_deleted == False,
            *expressions
        )

        data = ORM.pagination(
            session, stmt, **asdict(pagination), order=[App.updated_at.desc()])

        return data

    @staticmethod
    def get_app_permission(session: Session, pagination: Pagination, app_id: int) -> list:

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
    def get_app_role(session: Session, pagination: Pagination, role_name: str) -> list:

        stmt = select(
            AppRole.id,
            AppRole.role_id
        )
