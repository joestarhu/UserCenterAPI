from fastapi import APIRouter, HTTPException, Security, Depends, Query
from api.deps import Rsp, get_actor_info, page_info
from api.service.base import ServiceInfo
from api.schema.role import RoleAPI
from api.model.role import OptRoleStatus

api = APIRouter(prefix="/role")
URL_LIST = "/list"


services = {
    URL_LIST: ServiceInfo(name="获取角色信息", identify="role:list")
}


@api.get(URL_LIST, response_model=Rsp, summary=services[URL_LIST].name)
async def get_role_list(
    actor=Security(get_actor_info, scopes=[services[URL_LIST].identify]),
    pagination=Depends(page_info),
    role_name: str = Query(default=None, description="角色名"),
    role_status: OptRoleStatus = Query(default=None, description="角色状态")
) -> Rsp:

    try:
        data = RoleAPI.get_role_list(
            actor.session, pagination, role_name, role_status)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)
