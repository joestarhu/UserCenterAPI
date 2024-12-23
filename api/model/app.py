from sqlalchemy import String, BigInteger
from api.model.base import ModelBase, ModelPrimaryKeyID, ModelLogicDeleted, M, mc


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


class AppService(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_app_service"
    __table_args__ = (
        dict(comment="应用服务")
    )

    app_id: M[int] = mc(
        BigInteger,
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


class AppRole(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_app_role"
    __table_args__ = (
        dict(comment="应用角色表")
    )

    app_id: M[int] = mc(
        BigInteger,
        comment="应用ID"
    )

    role_id: M[int] = mc(
        BigInteger,
        comment="角色ID"
    )

    service_identify: M[str] = mc(
        String(64),
        comment="服务标识"
    )
