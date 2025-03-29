from fastapi import APIRouter, HTTPException, Security, Depends, Query, Body
from api.deps import Permission, Rsp, get_actor_info, get_page_info
from api.model.app import App
from api.model.permission import AppRole
from api.schema.app import AppAPI

api = APIRouter(prefix="/app")

permission = [
    API_LIST := Permission(path="/list", name="获取应用列表", scope="app:list"),
    API_DETAIL := Permission(path="/detail", name="获取应用详情", scope="app:detail"),
    API_SERIVCE := Permission(path="/service", name="获取应用服务", scope="app:service"),
    API_ROLE_LIST := Permission(path="/role_list", name="获取应用角色列表", scope="app:role_list"),
    API_ROLE_PERMISSION := Permission(path="/role_permission", name="获取应用角色权限", scope="app:role_permission"),
]


@api.get(API_LIST.path, summary=API_LIST.name)
def get_app_list(
    actor=Security(get_actor_info, scopes=[API_LIST.scope]),
    pagination=Depends(get_page_info),
    app_name: str = Query(default=None, description=App.app_name.comment)
) -> Rsp:
    try:
        data = AppAPI.get_app_list(actor.session, pagination, app_name)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(API_DETAIL.path, summary=API_DETAIL.name)
def get_app_detail(
    actor=Security(get_actor_info, scopes=[API_DETAIL.scope]),
    app_uuid: str = Query(description=App.app_uuid.comment)
) -> Rsp:
    try:
        data = AppAPI.get_app_detail(actor.session, app_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(API_SERIVCE.path, summary=API_SERIVCE.name)
def get_app_service(
    actor=Security(get_actor_info, scopes=[API_SERIVCE.scope]),
    app_uuid: str = Query(description=App.app_uuid.comment)
) -> Rsp:
    try:
        data = AppAPI.get_app_service(actor.session, app_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(API_ROLE_LIST.path, summary=API_ROLE_LIST.name)
def get_app_role_list(
    actor=Security(get_actor_info, scopes=[API_ROLE_LIST.scope]),
    app_id: int = Query(description=AppRole.app_id.comment)
) -> Rsp:
    try:
        data = AppAPI.get_app_role_list(actor.session, app_id)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(API_ROLE_PERMISSION.path, summary=API_ROLE_PERMISSION.name)
def get_app_role_permission(
    actor=Security(get_actor_info, scopes=[API_ROLE_PERMISSION.scope]),
    pagination=Depends(get_page_info),
    app_id: int = Query(description=AppRole.app_id.comment),
    role_id: int = Query(description=AppRole.role_id.comment)
) -> Rsp:
    try:
        data = AppAPI.get_app_role_permission(
            actor.session, pagination, app_id, role_id)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)
