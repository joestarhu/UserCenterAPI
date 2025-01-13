from enum import Enum
from sqlalchemy import String, Integer, UniqueConstraint
from api.model.base import ModelBase, ModelPrimaryKeyID, ModelLogicDeleted, M, mc


class OptUserStatus(int, Enum):
    ENABLE: int = 0
    DISABLE: int = 1


class OptUserAuthType(int, Enum):
    PASSWORD: int = 0
    DINGTALK: int = 1


class User(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_user"
    __table_args__ = (
        dict(comment="用户信息")
    )

    user_uuid: M[str] = mc(
        String(32),
        default="",
        unique=True,
        comment="用户UUID"
    )

    account: M[str] = mc(
        String(64),
        unique=True,
        comment="用户账号"
    )

    nickname: M[str] = mc(
        String(64),
        default="",
        comment="用户昵称",
    )

    phone_enc: M[str] = mc(
        String(256),
        default="",
        comment="用户手机号(加密)"
    )

    avatar_url: M[str] = mc(
        String(2048),
        default="",
        comment="用户头像URL"
    )

    user_status: M[int] = mc(
        Integer,
        default=OptUserStatus.ENABLE.value,
        comment="用户状态"
    )


class UserAuth(ModelPrimaryKeyID, ModelLogicDeleted, ModelBase):
    __tablename__ = "t_user_auth"
    __table_args__ = (
        UniqueConstraint("user_uuid", "auth_type",
                         "auth_identify", name="uni_user_auth"),
        dict(comment="用户认证信息")
    )

    user_uuid: M[str] = mc(
        User.user_uuid.type,
        default="",
        comment="用户UUID"
    )

    auth_type: M[int] = mc(
        Integer,
        default=OptUserAuthType.PASSWORD.value,
        comment="认证类型,如密码,钉钉等"
    )

    auth_identify: M[str] = mc(
        String(256),
        default="",
        comment="认证类型标识,如APPID"
    )

    auth_value: M[str] = mc(
        String(256),
        default="",
        comment="认证值,如密码或三方unionID等"
    )
