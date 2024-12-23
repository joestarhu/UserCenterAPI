from fastapi import APIRouter, HTTPException, Security, Depends, Query
from api.deps import Rsp, get_actor_info, page_info
from api.service.base import ServiceInfo
from api.schema.app import AppAPI


api = APIRouter(prefix="/app")
URL_LIST = "/list"
URL_PERMISSION = "/permission"
URL_ROLE = "/role"
services = {
    URL_LIST: ServiceInfo(name="获取应用信息", identify="app:list"),
    URL_PERMISSION: ServiceInfo(name="获取应用权限信息", identify="app:permission"),
    URL_ROLE: ServiceInfo(name="获取应用角色信息", identify="app:role"),
}


@api.get(URL_LIST, response_model=Rsp, summary=services[URL_LIST].name)
async def get_app_list(
    actor=Security(get_actor_info, scopes=[services[URL_LIST].identify]),
    pagination=Depends(page_info),
    app_name: str = Query(default=None, description="应用名称"),
) -> Rsp:
    try:
        data = AppAPI.get_app_list(actor.session, pagination, app_name)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)


@api.get(URL_PERMISSION, response_model=Rsp, summary=services[URL_PERMISSION].name)
async def get_app_permission(
    actor=Security(get_actor_info, scopes=[services[URL_PERMISSION].identify]),
    pagination=Depends(page_info),
    app_id: int = Query(description="应用ID")
) -> Rsp:
    try:
        data = AppAPI.get_app_permission(actor.session, pagination, app_id)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)


@api.get(URL_ROLE, response_model=Rsp, summary=services[URL_ROLE].name)
async def get_app_role(
    actor=Security(get_actor_info, scopes=[services[URL_ROLE].identify]),
    pagination=Depends(page_info)
) -> Rsp:
    try:
        ...
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp()
