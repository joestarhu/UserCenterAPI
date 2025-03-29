# from pydantic import BaseModel, Field
# from fastapi import APIRouter, HTTPException, Security, Depends, Query, Body
# from api.deps import Rsp, Permission, get_actor_info, get_page_info
# from api.schema.role import RoleAPI
# from api.model.role import Role, OptRoleStatus

# api = APIRouter(prefix="/role")

# permission = [
#     API_LIST := Permission(path="/list", name="获取角色列表信息", scope="role:list"),
#     API_DETAIL := Permission(path="/detail", name="获取角色详情信息", scope="role:detail"),
#     API_CREATE := Permission(path="/create", name="创建角色", scope="role:create"),
#     API_UPDATE := Permission(path="/update", name="更新角色", scope="role:update"),
#     API_DELETE := Permission(path="/delete", name="删除角色", scope="role:delete"),
# ]


# class RoleCreate(BaseModel):
#     role_name: str = Field(description=Role.role_name.comment,
#                            min_length=1,
#                            max_length=Role.role_name.type.length),
#     role_desc: str = Field(description=Role.role_desc.comment,
#                            max_length=Role.role_desc.type.length)
#     role_status: OptRoleStatus = Field(description=Role.role_status.comment,
#                                        default=OptRoleStatus.ENABLE)


# class RoleUpdate(BaseModel):
#     role_id: int = Field(description=Role.id.comment)
#     role_name: str = Field(description=Role.role_name.comment,
#                            min_length=1,
#                            max_length=Role.role_name.type.length),
#     role_desc: str = Field(description=Role.role_desc.comment,
#                            max_length=Role.role_desc.type.length)
#     role_status: OptRoleStatus = Field(description=Role.role_status.comment)


# class RoleDelete(BaseModel):
#     role_id: int = Field(description=Role.id.comment)


# @api.get(API_LIST.path, summary=API_LIST.name)
# def get_role_list(
#     actor=Security(get_actor_info, scopes=[API_LIST.scope]),
#     pagination=Depends(get_page_info),
#     app_id: int = Query(description=Role.app_id.comment),
#     role_name: str = Query(default=None, description=Role.role_name.comment),
#     role_status: OptRoleStatus = Query(
#         default=None, description=Role.role_status.comment)
# ) -> Rsp:
#     try:
#         data = RoleAPI.get_role_list(
#             actor.session, pagination, app_id, role_name, role_status)
#     except Exception as e:
#         raise HTTPException(500, f"{e}")
#     return Rsp(data=data)


# @api.get(API_DETAIL.path, summary=API_DETAIL.name)
# def get_role_detail(
#     actor=Security(get_actor_info, scopes=[API_DETAIL.scope]),
#     role_id: int = Query(description=Role.id.comment)
# ) -> Rsp:
#     try:
#         data = RoleAPI.get_role_detail(actor.session, role_id, "")
#     except Exception as e:
#         raise HTTPException(500, f"{e}")
#     return Rsp(data=data)


# @api.post(API_CREATE.path, summary=API_CREATE.name)
# def create_role(
#     actor=Security(get_actor_info, scopes=[API_CREATE.scope]),
#     data: RoleCreate = Body()
# ) -> Rsp:
#     try:
#         role = Role(**data.model_dump(), role_org_uuid="")
#         result = RoleAPI.create_role(actor.session, role)
#     except Exception as e:
#         raise HTTPException(500, f"{e}")
#     return Rsp(**result)


# @api.post(API_UPDATE.path, summary=API_UPDATE.name)
# def update_role(
#     actor=Security(get_actor_info, scopes=[API_UPDATE.scope]),
#     data: RoleUpdate = Body()
# ) -> Rsp:
#     try:
#         result = RoleAPI.update_role(
#             actor.session, data.role_id, data.role_name, data.role_desc, data.role_status)
#     except Exception as e:
#         raise HTTPException(500, f"{e}")
#     return Rsp(**result)


# @api.post(API_DELETE.path, summary=API_DELETE.name)
# def delete_role(
#     actor=Security(get_actor_info, scopes=[API_DELETE.scope]),
#     data: RoleDelete = Body()
# ) -> Rsp:
#     try:
#         result = RoleAPI.delete_role(actor.session, data.role_id)
#     except Exception as e:
#         raise HTTPException(500, f"{e}")
#     return Rsp(**result)
