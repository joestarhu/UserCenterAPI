# from fastapi import APIRouter, HTTPException, Query, Depends, Security
# from api.deps import Rsp, page_info, get_actor_info
# from api.model.user import OptUserStatus
# from api.schema.user import UserAPI
# from api.service.base import ServiceInfo

# api = APIRouter(prefix="/user")

# services = {
#     f"{api.prefix}/list": ServiceInfo(name="获取用户列表", identify="user:list")
# }


# @api.get("/list", response_model=Rsp, summary=services[f"{api.prefix}/list"].name)
# async def get_user_list(account: str = Query(default=None, description="用户账号"),
#                         user_status: OptUserStatus = Query(
#                             default=None, description="用户状态"),
#                         pagination=Depends(page_info),
#                         actor=Security(get_actor_info, scopes=[services[f"{api.prefix}/list"].identify])) -> Rsp:

#     try:
#         data = UserAPI.get_user_list(
#             actor.session, pagination, account, user_status)
#     except Exception as e:
#         raise HTTPException(500, detail=f"{e}")

#     return Rsp(data=data)

"""
@api.post("/create", response_model=Rsp, summary="新增用户")
async def create_user(actor=Security(get_actor_info, scopes=["user:create"])) -> Rsp:
    try:
        ...
    except Exception as e:
        raise HTTPException(500, detail=f"{e}")
    return Rsp()


@api.post("/update", response_model=Rsp, summary="更新用户")
async def update_user(actor=Security(get_actor_info, scopes=["user:update"])) -> Rsp:
    try:
        ...
    except Exception as e:
        raise HTTPException(500, detail=f"{e}")
    return Rsp()


@api.post("/delete", response_model=Rsp, summary="删除用户")
async def delete_user(actor=Security(get_actor_info, scopes=["user:delete"])) -> Rsp:
    try:
        ...
    except Exception as e:
        raise HTTPException(500, detail=f"{e}")
    return Rsp()
"""
