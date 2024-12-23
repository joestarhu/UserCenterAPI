from fastapi import APIRouter, HTTPException, Security, Depends, Query, Body
from api.deps import Rsp, page_info, get_actor_info
from api.model.user import OptUserStatus
from api.schema.user import UserAPI, AccountCreate, AccountDelete, AccountUpdate
from api.service.base import ServiceInfo

api = APIRouter(prefix="/account")


# url
URL_LIST = "/list"
URL_DETAIL = "/detail"
URL_CREATE = "/create"
URL_DELETE = "/delete"
URL_UPDATE = "/update"

services = {
    URL_LIST: ServiceInfo(name="获取账号列表", identify="account:list"),
    URL_DETAIL: ServiceInfo(name="获取账号详情", identify="account:detail"),
    URL_CREATE: ServiceInfo(name="创建账号", identify="account:create"),
    URL_DELETE: ServiceInfo(name="删除账号", identify="account:delete"),
    URL_UPDATE: ServiceInfo(name="更新账号", identify="account:update"),
}


@api.get(URL_LIST, response_model=Rsp, summary=services[URL_LIST].name)
async def get_account_list(
    actor=Security(get_actor_info,
                   scopes=[services[URL_LIST].identify]),
    pagination=Depends(page_info),
    account: str = Query(default=None, description="用户状态"),
    nickname: str = Query(default=None, description="用户昵称"),
    user_status: OptUserStatus = Query(default=None, description="用户状态"),
) -> Rsp:
    try:
        data = UserAPI.get_account_list(
            actor.session, pagination, account, nickname, user_status)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(URL_DETAIL, response_model=Rsp, summary=services[URL_DETAIL].name)
async def get_account_detail(
    actor=Security(get_actor_info,
                   scopes=[services[URL_DETAIL].identify]),
    user_uuid: str = Query(description="用户UUID")
) -> Rsp:
    try:
        data = UserAPI.get_account_detail(actor.session, user_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)


@api.post(URL_CREATE, response_model=Rsp, summary=services[URL_CREATE].name)
async def create_account(
    actor=Security(get_actor_info,
                   scopes=[services[URL_CREATE].identify]),
    data: AccountCreate = Body()
) -> Rsp:
    try:
        result = UserAPI.create_account(actor.session, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result)


@api.post(URL_DELETE, response_model=Rsp, summary=services[URL_DELETE].name)
async def delete_account(
    actor=Security(get_actor_info,
                   scopes=[services[URL_DELETE].identify]),
    data: AccountDelete = Body()
) -> Rsp:
    try:
        result = UserAPI.delete_account(actor.session, data.user_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result)


@api.post(URL_UPDATE, response_model=Rsp, summary=services[URL_UPDATE].name)
async def update_account(
    actor=Security(get_actor_info, scopes=[services[URL_UPDATE].identify]),
    data: AccountUpdate = Body()
) -> Rsp:
    try:
        result = UserAPI.update_account(actor.session, data)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result)
