from enum import Enum
from sqlalchemy import String, Integer, UniqueConstraint
from api.model.base import ModelBase, ModelPrimaryKeyID, ModelLogicDeleted, M, mc
from api.model.org import Org


class OptAppStatus(int, Enum):
    ENABLE: int = 0
    DISABLE: int = 1


class App(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_app"
    __table_args__ = (
        dict(comment="应用信息")
    )

    app_name: M[str] = mc(
        String(64),
        default="",
        comment="应用名称"
    )

    app_desc: M[str] = mc(
        String(256),
        default="",
        comment="应用描述"
    )

    app_status: M[int] = mc(
        Integer,
        default=OptAppStatus.ENABLE.value,
        comment="应用状态"
    )

    org_uuid: M[str] = mc(
        Org.org_uuid.type,
        default="",
        comment="应用所属组织UUID"
    )


class AppService(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_app_service"
    __table_args__ = (
        UniqueConstraint("app_id", "service_identify", name="uni_app_service"),
        dict(comment="应用服务")
    )

    app_id: M[int] = mc(
        App.id.type,
        comment="应用ID"
    )

    service_identify: M[str] = mc(
        String(64),
        comment="服务标识"
    )

    service_name: M[str] = mc(
        String(64),
        comment="服务名称"
    )
