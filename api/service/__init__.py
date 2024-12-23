from fastapi import APIRouter
from . import account, app, auth, user, org, role

routers = APIRouter()
services = []


for api, tags, api_service in [
    (auth.api, ["认证服务"], None),
    (account.api, ["账号服务"], account.services),
    (app.api, ["应用服务"], app.services),
    (user.api, ["用户服务"], user.services),
    (org.api, ["组织服务"], org.services),
    (role.api, ["角色服务"], None),
]:
    routers.include_router(api, tags=tags)

    if api_service is None:
        continue
    for service_info in api_service.values():
        services.append(service_info)
