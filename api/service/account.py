from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Security, Depends, Query, Body
from api.deps import Permission, Rsp, get_actor_info, get_page_info
from api.security import server_aes_api
from api.model.user import User, OptUserStatus
from api.schema.user import UserAPI

# 路由对象
api = APIRouter(prefix="/account")

# 权限对象
permission = [
    API_LIST := Permission(path="/list", name="获取账号列表信息", scope="account:list"),
    API_DETAIL := Permission(path="/detail", name="获取账号详情", scope="account:detail"),
    API_CREATE := Permission(path="/create", name="创建账号", scope="account:create"),
    API_UPDATE := Permission(path="/update", name="更新账号", scope="account:update"),
    API_DELETE := Permission(path="/delete", name="删除账号", scope="account:delete")
]


class AccountCreate(BaseModel):
    account: str = Field(description=User.account.comment,
                         pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
                         max_length=User.account.type.length)
    nickname: str = Field(description=User.nickname.comment,
                          min_length=1,
                          max_length=User.nickname.type.length)
    phone: str = Field(description="手机号",
                       default="",
                       pattern=r"^1[3-9]\d{9}$|^$")
    user_status: OptUserStatus = Field(description=User.user_status.comment,
                                       default=OptUserStatus.ENABLE)


class AccountUpdate(BaseModel):
    user_uuid: str = Field(description=User.user_uuid.comment)
    nickname: str = Field(description=User.nickname.comment,
                          min_length=1,
                          max_length=User.nickname.type.length)
    user_status: OptUserStatus = Field(description=User.user_status.comment)


class AccountDelete(BaseModel):
    user_uuid: str = Field(description=User.user_uuid.comment)


@api.get(API_LIST.path, summary=API_LIST.name)
def get_account_list(
        actor=Security(get_actor_info, scopes=[API_LIST.scope]),
        pagination=Depends(get_page_info),
        account: str = Query(default=None, description=User.account.comment),
        nickname: str = Query(default=None, description=User.nickname.comment),
        user_status: OptUserStatus = Query(
            default=None, description=User.user_status.comment)
) -> Rsp:
    try:
        data = UserAPI.get_account_list(
            actor.session, pagination, account, nickname, user_status)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(API_DETAIL.path, summary=API_DETAIL.name)
def get_account_detail(
    actor=Security(get_actor_info, scopes=[API_DETAIL.scope]),
    user_uuid: str = Query(description=User.user_uuid.comment)
) -> Rsp:
    try:
        data = UserAPI.get_account_detail(actor.session, user_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.post(API_CREATE.path, summary=API_CREATE.name)
def create_account(
    actor=Security(get_actor_info, scopes=[API_CREATE.scope]),
    req_data: AccountCreate = Body()
) -> Rsp:
    try:
        # 加密手机号(手机号内部均是加密处理的)
        phone_enc = server_aes_api.phone_encrypt(
            req_data.phone) if req_data.phone else ""

        user = User(account=req_data.account,
                    nickname=req_data.nickname,
                    user_status=req_data.user_status,
                    phone_enc=phone_enc)

        result = UserAPI.create_account(actor.session, user)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(**result)


@api.post(API_UPDATE.path, summary=API_UPDATE.name)
def update_account(
    actor=Security(get_actor_info, scopes=[API_UPDATE.scope]),
    req_data: AccountUpdate = Body()
) -> Rsp:
    try:
        result = UserAPI.update_account(
            actor.session, req_data.user_uuid, req_data.nickname, req_data.user_status)

    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(**result)


@api.post(API_DELETE.path, summary=API_DELETE.name)
def delete_account(
    actor=Security(get_actor_info, scopes=[API_UPDATE.scope]),
    req_data: AccountDelete = Body()
) -> Rsp:
    try:
        result = UserAPI.delete_account(actor.session, req_data.user_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(**result)
