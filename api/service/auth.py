from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from api.deps import Rsp, JwtPayload, Pagination, db_session
from api.errcode import APIErr
from api.security import client_aes_api, hash_api, jwt_api
from api.schema.user import UserAPI, OptUserStatus
from api.schema.org import OrgAPI
from api.model.org import Org

api = APIRouter(prefix="/auth")


class PasswordLogin(BaseModel):
    account: str = Field(description="用户账号")
    password_enc: str = Field(description="密码,加密传输")
    client_id: str = Field(default="")
    client_secret: str = Field(default="")


def password_login(session: Session, account: str, password: str) -> Rsp:
    """密码登录
    """

    user_auth = UserAPI.get_user_auth_info(session, account)

    if user_auth is None or hash_api.verify(password, user_auth["auth_value"]) == False:
        return Rsp(**APIErr.WRONG_ACCOUNT_PASSWD)

    if user_auth["user_status"] == OptUserStatus.DISABLE.value:
        return Rsp(**APIErr.ACCOUNT_STATUS_DISABLE)

    user_uuid = user_auth["user_uuid"]
    payload = JwtPayload(user_uuid=user_uuid)

    org_list = OrgAPI.get_user_org_list(session, user_uuid, Pagination(),
                                        Org.org_uuid, Org.org_owner)

    if org_list and len(org_list["records"]) == 1:
        payload.org_uuid = org_list["records"][0]["org_uuid"]
        payload.is_admin = True if org_list["records"][0]["org_owner"] == user_uuid else False
    data = jwt_api.encode(**asdict(payload))

    return Rsp(data=data)


@api.post("/docs_login")
async def docs_login(
    req_data=Depends(OAuth2PasswordRequestForm),
    session=Depends(db_session)
) -> dict:
    try:
        rsp = password_login(session, req_data.username, req_data.password)
    except Exception as e:
        raise HTTPException(500, detail=f"{e}")

    return {"access_token": rsp.data, "token_type": "bearer"}


@api.post("/login", response_model=Rsp, summary="登录")
async def login(
    req_data: PasswordLogin,
    session=Depends(db_session)
) -> Rsp:
    try:
        password = client_aes_api.decrypt(req_data.password_enc)
        rsp = password_login(session, req_data.account, password)
    except Exception as e:
        raise HTTPException(500, detail=f"{e}")

    return rsp
