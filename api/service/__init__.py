from fastapi import APIRouter
from . import auth, user

routers = APIRouter()


for api, tags in [
    (auth.api, ["认证服务"]),
    (user.api, ["用户服务"]),
]:
    routers.include_router(api, tags=tags)
