from enum import Enum
from sqlalchemy import String, Integer
from api.model.base import ModelBase, ModelPrimaryKeyID, ModelLogicDeleted, M, mc


class OptRoleStatus(int, Enum):
    ENABLE: int = 0
    DISABLE: int = 1


class Role(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_role"
    __table_args__ = (
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
        String(32),
        default="",
        comment="角色所属组织UUID"
    )
