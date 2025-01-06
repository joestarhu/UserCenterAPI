from enum import Enum
from sqlalchemy import String, Integer, UniqueConstraint
from api.model.base import ModelBase, ModelPrimaryKeyID, ModelLogicDeleted, M, mc
from api.model.org import Org
from api.model.user import User


class OptRoleStatus(int, Enum):
    ENABLE: int = 0
    DISABLE: int = 1


class Role(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_role"
    __table_args__ = (
        UniqueConstraint("role_name", "role_org_uuid", name="uni_role"),
        dict(comment="角色信息")
    )

    role_name: M[str] = mc(
        String(64),
        default="",
        comment="角色名"
    )

    role_desc: M[str] = mc(
        String(256),
        default="",
        comment="角色描述"
    )

    role_status: M[int] = mc(
        Integer,
        default=OptRoleStatus.ENABLE.value,
        comment="角色状态"
    )

    role_org_uuid: M[str] = mc(
        Org.org_uuid.type,
        default="",
        comment="角色所属组织UUID"
    )


class OrgUserRole(ModelPrimaryKeyID, ModelBase):
    __tablename__ = "t_org_user_role"
    __table_args__ = (
        UniqueConstraint("org_uuid", "user_uuid", "role_id",
                         name="uni_org_user_role"),
        dict(comment="组织用户角色信息")
    )

    org_uuid: M[str] = mc(
        Org.org_uuid.type,
        comment="组织UUID"
    )

    user_uuid: M[str] = mc(
        User.user_uuid.type,
        comment="用户UUID"
    )

    role_id: M[int] = mc(
        Role.id.type,
        comment="角色ID"
    )
