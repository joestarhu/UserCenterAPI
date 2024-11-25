from dataclasses import asdict
from sqlalchemy import select, and_
from jhu.orm import ORM, Session, ORMFormatRule
from api.deps import Pagination
from api.security import client_aes_api
from api.model.user import User, UserAuth, OptUserStatus, OptUserAuthType

# 格式化规则
fmt_rules = [
    ORMFormatRule("phone", client_aes_api.phone_decrypt)
]


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
        ).where(and_(
            User.is_deleted == False,
            User.account == account,
            UserAuth.auth_type == auth_type.value,
            UserAuth.auth_identify == auth_identify
        ))

        return ORM.one(session, stmt)

    @staticmethod
    def get_user_list(session: Session,
                      pagination: Pagination,
                      account: str,
                      user_status: OptUserStatus
                      ) -> dict:

        expresions = [expression for condition, expression in [
            (account is not None, User.account.ilike(f"%{account}%")),
            (user_status is not None, User.user_status == user_status)
        ] if condition]

        stmt = select(
            User.user_uuid,
            User.account,
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
            order=[User.created_at],
            format_rules=fmt_rules,
            **asdict(pagination),
        )
