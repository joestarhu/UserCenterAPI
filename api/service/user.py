from fastapi import APIRouter, HTTPException, Query, Depends

from api.deps import Rsp, page_info, get_actor_info
from api.model.user import OptUserStatus
from api.schema.user import UserAPI

api = APIRouter(prefix="/user")


@api.get("/list", response_model=Rsp, summary="获取用户列表")
async def get_user_list(account: str = Query(default=None, description="用户账号"),
                        user_status: OptUserStatus = Query(
                            default=None, description="用户状态"),
                        pagination=Depends(page_info),
                        actor=Depends(get_actor_info)) -> Rsp:

    try:
        data = UserAPI.get_user_list(
            actor.session, pagination, account, user_status)
    except Exception as e:
        HTTPException(500, detail=f"{e}")

    return Rsp(data=data)
