from enum import Enum
from sqlalchemy import Integer, UniqueConstraint
from api.model.app import App, AppService
from api.model.base import ModelBase, ModelPrimaryKeyID,  M, mc
from api.model.org import Org
from api.model.role import Role


class PermissionType(int, Enum):
    # 部门数据权限
    DATA_PERMISSION_DEPT: int = 1


class DataPermissionDept(int, Enum):
    """部门数据权限策略
    """
    # 本人
    SELF: int = 1
    # 所有
    ALL: int = 99


class AppRole(ModelPrimaryKeyID, ModelBase):
    __tablename__ = "t_app_role"
    __table_args__ = (
        UniqueConstraint("app_id", "role_id", name="uni_app_role"),
        dict(comment="应用角色表")
    )

    app_id: M[int] = mc(
        App.id.type,
        comment="应用ID"
    )

    role_id: M[int] = mc(
        Role.id.type,
        comment="角色ID"
    )


class AppPermission(ModelPrimaryKeyID, ModelBase):
    __tablename__ = "t_app_permission"
    __table_args__ = (
        UniqueConstraint("app_role_id", "permission_type",
                         name="uni_app_permission"),
        dict(comment="应用权限表")
    )

    app_role_id: M[int] = mc(
        AppRole.id.type,
        comment="应用角色ID"
    )

    permission_type: M[int] = mc(
        Integer,
        comment="权限类型"
    )

    permission_value: M[int] = mc(
        Integer,
        comment="权限策略"
    )


class OrgAppService(ModelPrimaryKeyID, ModelBase):
    __tablename__ = "t_org_app_service"
    __table_args__ = (
        UniqueConstraint("org_uuid", "app_service_id",
                         name="uni_org_app_service"),
        dict(comment="组织用户角色信息")
    )

    org_uuid: M[str] = mc(
        Org.org_uuid.type,
        comment="组织UUID"
    )

    app_service_id: M[int] = mc(
        AppService.id.type,
        comment="应用服务ID"
    )
