from fastapi import APIRouter, HTTPException, Security, Depends, Query
from api.deps import Rsp, get_actor_info, page_info
from api.service.base import ServiceInfo
from api.schema.org import OrgAPI
from api.model.org import Org, OptOrgStatus


api = APIRouter(prefix="/org")
URL_LIST = "/list"
URL_USER_LIST = "/user_list"

services = {
    URL_LIST: ServiceInfo(name="获取组织信息", identify="org:list"),
    URL_USER_LIST: ServiceInfo(name="获取组织用户信息", identify="org:user_list"),
}


@api.get("/user_org_list", response_model=Rsp, summary="获取用户组织信息")
async def get_user_org_list(pagination=Depends(page_info),
                            actor=Security(get_actor_info, scopes=[])) -> Rsp:
    try:
        output_fileds = (Org.org_uuid, Org.org_name, Org.org_owner)
        data = OrgAPI.get_user_org_list(actor.session, actor.user_uuid, pagination,
                                        *output_fileds)
    except Exception as e:
        raise HTTPException(500, detail=f"{e}")

    return Rsp(data=data)


@api.get(URL_LIST, response_model=Rsp, summary=services[URL_LIST].name)
async def get_org_list(
    actor=Security(get_actor_info, scopes=[services[URL_LIST].identify]),
    pagination=Depends(page_info),
    org_name: str = Query(default=None, description="组织名"),
    org_status: OptOrgStatus = Query(default=None, description="组织状态")
) -> Rsp:
    try:
        data = OrgAPI.get_org_list(
            actor.session, pagination, org_name, org_status)
    except Exception as e:
        raise HTTPException(500, detail=f"{e}")
    return Rsp(data=data)


@api.get(URL_USER_LIST, response_model=Rsp, summary=services[URL_USER_LIST].name)
async def get_org_user_list(
    actor=Security(get_actor_info, scopes=[services[URL_USER_LIST].identify]),
    pagination=Depends(page_info)
) -> Rsp:
    try:
        data = OrgAPI.get_org_user_list(
            actor.session, pagination, actor.org_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(data=data)
