from enum import Enum
from sqlalchemy import String, Integer, UniqueConstraint, Boolean
from api.model.base import ModelBase, ModelPrimaryKeyID, ModelLogicDeleted, M, mc
from api.model.user import User


class OptOrgStatus(int, Enum):
    ENABLE: int = 0
    DISABLE: int = 1


class OptOrgUserStatus(int, Enum):
    ENABLE: int = 0
    DISABLE: int = 1


class Org(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_org"
    __table_args__ = (
        dict(comment="组织信息")
    )

    org_uuid: M[str] = mc(
        String(32),
        default="",
        unique=True,
        comment="组织UUID"
    )

    org_name: M[str] = mc(
        String(64),
        default="",
        comment="组织名称"
    )

    org_owner: M[str] = mc(
        User.user_uuid.type,
        default="",
        comment="组织所有者UUID"
    )

    org_status: M[int] = mc(
        Integer,
        default=OptOrgStatus.ENABLE.value,
        comment="组织状态"
    )

    is_admin: M[bool] = mc(
        Boolean,
        default=False,
        comment="是否为管理者组织"
    )


class OrgUser(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_org_user"
    __table_args__ = (
        UniqueConstraint("org_uuid", "user_uuid", name="uni_org_user"),
        dict(comment="组织用户信息")
    )

    org_uuid: M[str] = mc(
        Org.org_uuid.type,
        default="",
        comment="组织UUID"
    )

    user_uuid: M[str] = mc(
        User.user_uuid.type,
        default="",
        comment="用户UUID"
    )

    org_user_nickname: M[str] = mc(
        String(64),
        default="",
        comment="组织用户昵称"
    )

    org_avatar_url: M[str] = mc(
        String(2048),
        default="",
        comment="组织用户头像URL"
    )

    org_user_status: M[int] = mc(
        Integer,
        default=OptOrgUserStatus.ENABLE.value,
        comment="组织用户状态"
    )
