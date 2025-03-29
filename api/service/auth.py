from dataclasses import asdict
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from api.config import settings
from api.deps import Rsp, JwtPayload, get_db_session
from api.errcode import APIErr
from api.security import client_aes_api, hash_api, jwt_api
from api.model.user import User, UserAuth, OptAccountStatus
from api.model.org import Org, OrgUser, OptOrgUserStatus
from api.schema.user import UserAPI
from api.schema.org import OrgAPI


api = APIRouter(prefix="/auth")


class PasswordLogin(BaseModel):
    account: str = Field(description=User.account.comment,
                         max_length=User.account.type.length)
    password_enc: str = Field(description="密码(需加密)",
                              max_length=UserAuth.auth_value.type.length)


def check_org_owner(target, src) -> bool:
    return target == src


def password_login(session: Session, account: str, password: str, org_uuid: str = None) -> Rsp:
    r"""通过密码完成认证

    Parameters:
        session:数据库会话
        account:账号
        password:密码
        org_uuid:指定登录的组织UUID

    Returns:
        Rsp{
            code: 业务返回码
            message: 业务返回信息
            data:jwt的token字符
        }
    """
    # 获取账号认证信息
    account_auth = UserAPI.get_account_auth_info(session, account)

    # 无数据或密码对不上
    if not account_auth or not hash_api.verify(password, account_auth["auth_value"]):
        return Rsp(**APIErr.WRONG_ACCOUNT_PASSWD)

    # 如果账号状态不可用
    if OptAccountStatus.DISABLE.value == account_auth["account_status"]:
        return Rsp(**APIErr.ACCOUNT_STATUS_DISABLE)

    user_uuid = account_auth["user_uuid"]
    is_org_owner = False

    if org_uuid:
        # 如果指定了登录的组织UUID
        select_fields = [OrgUser.org_user_status, Org.org_owner_uuid]
        org_user = OrgAPI.get_org_user_detail(
            session, org_uuid, user_uuid, select_fields)
        if not org_user:
            # 组织下无该用户
            return Rsp(**APIErr.WRONG_ACCOUNT_PASSWD)
        if OptOrgUserStatus.DISABLE.value == org_user["org_user_status"]:
            # 组织下该用户账号被停用
            return Rsp(**APIErr.ORG_USER_STATUS_DISABLE)
        is_org_owner = check_org_owner(org_user["org_owner_uuid"], user_uuid)
    else:
        select_fields = [Org.org_uuid,
                         OrgUser.org_user_status, Org.org_owner_uuid]
        user_org_list = UserAPI.get_user_org_list(
            session, user_uuid, select_fields)

        if len(user_org_list) == 1 and OptOrgUserStatus.ENABLE.value == user_org_list[0]["org_user_status"]:
            # 仅有一个组织,且账户未被组织停用
            org_uuid = user_org_list[0]["org_uuid"]
            is_org_owner = check_org_owner(
                user_uuid, user_org_list[0]["org_owner_uuid"])

    payload = JwtPayload(user_uuid=user_uuid,
                         org_uuid=org_uuid,
                         is_org_owner=is_org_owner)
    data = jwt_api.encode(**asdict(payload))
    return Rsp(data=data)


@api.post("/login", summary="登录")
def login(
    session=Depends(get_db_session),
    req_data: PasswordLogin = Body()
) -> Rsp:
    try:
        # 客户端过来的是加密的密码,需要先解密
        password = client_aes_api.decrypt(req_data.password_enc)
        rsp = password_login(session, req_data.account, password)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return rsp


@api.post("/docs_login", summary="网页登录(仅限测试环境)")
async def docs_login(
    session=Depends(get_db_session),
    req_data=Depends(OAuth2PasswordRequestForm)
) -> dict:
    # 如果没有设置swaggerUI,则该功能不启用,默认直接返回{}
    if not settings.docs_url:
        return {}

    try:
        rsp = password_login(session, req_data.username, req_data.password)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return {"access_token": rsp.data, "token_type": "bearer"}
