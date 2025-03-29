#! /usr/bin/env python3
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker, Session
from jhu.orm import ORM

from api.model.user import User, UserAuth
from api.model.org import Org, OrgUser
from api.model.role import Role
from api.model.permission import App, AppService, AppRole
from api.schema.user import UserAPI
from api.schema.org import OrgAPI
from api.service import permissions
from api.security import create_usr_uuid, create_org_uuid, create_app_uuid
# import logging

# logger = logging.getLogger("ModelScript")
# logger.setLevel(logging.INFO)
# log_fmt = logging.Formatter(r"[%(asctime)s %(name)s]:%(message)s")
# ch = logging.StreamHandler()
# ch.setFormatter(log_fmt)
# logger.addHandler(ch)


def sql_exec(session: Session, select_params: list, where_params) -> dict | None:
    stmt = select(
        *select_params
    ).where(where_params)
    return ORM.one(session, stmt)


def init_user(session: Session, user: User) -> str:
    """初始化新建一个用户返回用户user_uuid
    """
    where_params = User.account == user.account

    info = sql_exec(session, [User.user_uuid], where_params)

    if info:
        user_uuid = info["user_uuid"]
    else:
        user_auth = UserAuth(
            auth_value="$2b$12$aMEyp5bE7XOCH6VJ2vWZKe0nn./Z/Z4wuQ31CNWwEia5tESbYuXwm"
        )
        UserAPI.create_account(session, user, user_auth)
        user_uuid = user.user_uuid

    return user_uuid


def init_org(session: Session, org: Org) -> str:
    """返回org_uuid
    """
    where_params = Org.org_name == org.org_name

    info = sql_exec(session, [Org.org_uuid], where_params)
    if info:
        org_uuid = info["org_uuid"]
    else:
        OrgAPI.create_org(session, org)
        org_uuid = org.org_uuid

    return org_uuid


def init_role(session: Session, role: Role) -> int:
    """返回Role的ID
    """
    where_params = Role.role_name == role.role_name

    info = sql_exec(session, [Role.id], where_params)
    if info:
        role_id = info["id"]
    else:
        try:
            session.add(role)
            session.commit()
            role_id = role.id
        except Exception as e:
            session.rollback()
            raise e

    return role_id


def init_app_ucadmin(session: Session, owner_org_uuid: str):
    app = App(app_uuid=create_app_uuid(),
              app_name="统一用户中心(管理端)",
              app_desc="统一用户中心用于管理用户,组织,应用以及权限",
              owner_org_uuid=owner_org_uuid,
              )
    app_info = sql_exec(session, [App.app_uuid],
                        App.app_name == app.app_name)
    if app_info:
        app_uuid = app_info["app_uuid"]
    else:
        try:
            session.add(app)
            session.commit()
            app_uuid = app.app_uuid
        except Exception as e:
            session.rollback()
            raise e

    appserv = [AppService(app_uuid=app_uuid, service_identify=s.scope, service_name=s.name) for s in permissions
               if not sql_exec(session, (AppService.id,),
                               and_(AppService.app_uuid == app_uuid,
                                    AppService.service_identify == s.scope,
                                    AppService.service_name == s.name
                                    ))]

    if appserv:
        try:
            session.add_all(appserv)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    return app_uuid


def init_app_role(session: Session, app_id: int, role_id: int, service_identify_list: list[str]):
    app_role_list = [AppRole(app_id=app_id, role_id=role_id, service_identify=service_identify)
                     for service_identify in service_identify_list]

    try:
        session.add_all(
            [app_role for app_role in app_role_list if not sql_exec(
                session, (AppRole.id,),
                and_(AppRole.app_id == app_id, AppRole.role_id == role_id,
                     AppRole.service_identify == app_role.service_identify)
            )]
        )
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def init_data(session: Session):
    """初始化脚本数据"""

    # 用户账号初始化
    user = User(account="eromod", nickname="超级管理员")
    # user = User(account="cantahu", nickname="胡")
    user_uuid = init_user(session, user)

    # 初始化组织
    org = Org(org_name="Eromod", org_owner_uuid=user_uuid, is_admin=True)
    org_uuid = init_org(session, org)

    # 30000个用户冲刺
    # for idx in range(30000):
    #     acct = f"demo_{idx}"
    #     nickname = f"demo_nick_{idx}"
    #     user = User(account=acct, nickname=nickname)
    #     user_uuid = init_user(session, user)
    #     org_user = OrgUser(org_uuid=org_uuid, user_uuid=user_uuid,
    #                        org_user_nickname=user.nickname)
    #     init_org_user(session, org_user)

    #     if idx % 10000 == 0:
    #         print(f"{idx}个数据完成")

    # 初始化应用(统一用户中心)
    # app_id = init_app_ucadmin(session, org_uuid)

    # 初始化角色
    # role_admin = Role(
    #     role_name="管理员", role_desc="拥有最高权限的角色,请谨慎授予用户", app_id=app_id)
    # role_admin_id = init_role(session, role_admin)

    # 管理员角色权限列表
    # admin_scopes = [s.scope for s in permissions]
    # 暂且不初始化角色权限
    # init_app_role(session, app_id, role_admin_id, admin_scopes)


if __name__ == "__main__":
    # url = "postgresql://postgres:qwe321@49.235.146.108:22094/ucapi"
    url = "postgresql://postgres:qwe321@localhost:22094/ucapi"
    engine = create_engine(url=url)

    # ModelBase.metadata.create_all(bind=engine)
    # ModelBase.metadata.drop_all(bind=engine)

    # metadata = ModelBase.metadata
    # metadata.reflect(bind=engine)

    localSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = localSession()
    init_data(session)
