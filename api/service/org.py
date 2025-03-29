from fastapi import APIRouter, HTTPException, Depends, Security, Query, Body
from pydantic import BaseModel, Field
from api.deps import Rsp, Permission, Pagination, get_actor_info, get_page_info
from api.model.org import Org, OptOrgStatus
from api.model.user import User, OptAccountStatus
from api.schema.org import OrgAPI
from api.schema.user import UserAPI

api = APIRouter(prefix="/org")

permission = [
    API_LIST := Permission(path="/list", name="获取组织列表信息", scope="org:list"),
    API_DETAIL := Permission(path="/detail", name="获取组织详情信息", scope="org:detail"),
    API_USER_LIST := Permission(path="/user_list", name="获取组织用户列表信息", scope="org:user_list"),
    API_OWNER_LIST := Permission(path="/owner_list", name="获取可成为组织Owner的用户列表", scope="org:owner_list"),
    API_CREATE := Permission(path="/create", name="创建组织", scope="org:create"),
]


class OrgCreate(BaseModel):
    org_name: str = Field(description=Org.org_name.comment,
                          max_length=Org.org_name.type.length)
    org_owner_uuid: str = Field(description=Org.org_owner_uuid.comment,
                                max_length=Org.org_owner_uuid.type.length)
    org_status: OptOrgStatus = Field(description=Org.org_status.comment,
                                     default=OptOrgStatus.ENABLE)


@api.get(API_LIST.path, summary=API_LIST.name)
def get_org_list(
    actor=Security(get_actor_info, scopes=[API_LIST.scope]),
    pagination=Depends(get_page_info),
    org_name: str = Query(default=None, description=Org.org_name.comment),
    org_status: OptOrgStatus = Query(
        default=None, description=Org.org_status.comment)
) -> Rsp:
    try:
        data = OrgAPI.get_org_list(
            actor.session, pagination, org_name, org_status)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(API_DETAIL.path, summary=API_DETAIL.name)
def get_org_detail(
    actor=Security(get_actor_info, scopes=[API_DETAIL.scope]),
    org_uuid: str = Query(description=Org.org_uuid.comment)
) -> Rsp:
    try:
        data = OrgAPI.get_org_detail(actor.session, org_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(API_USER_LIST.path, summary=API_USER_LIST.name)
def get_user_list(
    actor=Security(get_actor_info, scopes=[API_USER_LIST.scope]),
    pagination=Depends(get_page_info),
    org_uuid: str = Query(description=Org.org_uuid.comment)
) -> Rsp:
    try:
        data = OrgAPI.get_org_user_list(actor.session, pagination, org_uuid)
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.get(API_OWNER_LIST.path, summary=API_OWNER_LIST.name)
def get_org_owner_list(
    actor=Security(get_actor_info, scopes=[API_OWNER_LIST.scope]),
    account: str = Query(default="", description=User.account.comment)
) -> Rsp:
    try:
        pagination = Pagination(page_idx=1, page_size=10)
        data = UserAPI.get_account_list(
            actor.session, pagination,
            account=account,
            account_status=OptAccountStatus.ENABLE,
            select_fields=[User.account, User.nickname, User.user_uuid]
        )
    except Exception as e:
        raise HTTPException(500, f"{e}")
    return Rsp(data=data)


@api.post(API_CREATE.path, summary=API_CREATE.name)
def create_org(
    actor=Security(get_actor_info, scopes=[API_CREATE.scope]),
    req_data: OrgCreate = Body()
) -> Rsp:
    try:
        org = Org(org_name=req_data.org_name,
                  org_owner_uuid=req_data.org_owner_uuid,
                  org_status=req_data.org_status)
        result = OrgAPI.create_org(actor.session, org)
    except Exception as e:
        raise HTTPException(500, f"{e}")

    return Rsp(**result)
