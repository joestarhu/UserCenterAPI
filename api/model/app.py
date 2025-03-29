from sqlalchemy import String, Boolean, UniqueConstraint
from api.model.base import ModelBase, ModelPrimaryKeyID,  M, mc
from api.model.org import Org


class App(ModelPrimaryKeyID,  ModelBase):
    __tablename__ = "t_app"
    __table_args__ = (
        dict(comment="应用信息")
    )

    app_uuid: M[str] = mc(
        String(36),
        default="",
        comment="应用UUID"
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

    owner_org_uuid: M[str] = mc(
        Org.org_uuid.type,
        default="",
        comment="应用所属组织uuid"
    )


class AppService(ModelPrimaryKeyID, ModelBase):
    __tablename__ = "t_app_service"
    __table_args__ = (
        UniqueConstraint("app_uuid", "service_identify",
                         name="uni_app_service"),
        dict(comment="应用服务")
    )

    app_uuid: M[str] = mc(
        App.app_uuid.type,
        comment="应用UUID"
    )

    service_identify: M[str] = mc(
        String(64),
        comment="服务标识"
    )

    service_name: M[str] = mc(
        String(64),
        comment="服务名称"
    )

    is_enable: M[bool] = mc(
        Boolean,
        default=True,
        comment="服务是否有效"
    )
