from fastapi import APIRouter
from . import account, app, auth, user, org, role

routers = APIRouter()
permissions = []


for api, tags, api_permission in [
    (auth.api, ["认证服务"], None),
    (account.api, ["账号服务"], account.permission),
    (app.api, ["应用服务"], app.permission),
    (org.api, ["组织服务"], org.permission),
    (role.api, ["角色服务"], role.permission),
]:
    routers.include_router(api, tags=tags)

    if api_permission is None:
        continue
    for permission in api_permission:
        permissions.append(permission)
