from typing import Generator, Any
from dataclasses import dataclass
from fastapi import Query, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.config import settings
from api.security import jwt_api

engine = create_engine(**settings.db_settings)
localSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

oauth2 = OAuth2PasswordBearer("/auth/docs_login")


@dataclass
class JwtPayload:
    """jwt的payload内容
    """
    user_uuid: str


@dataclass
class Pagination:
    page_idx: int = 1
    page_size: int = 10


@dataclass
class Rsp:
    """RESTFUL API请求返回结果
    """
    code: int = 0
    message: str = "Succeed"
    data: Any | None = None


@dataclass
class Actor:
    session: Session
    user_uuid: str


def db_session() -> Generator:
    """获取数据库会话Session
    """
    with localSession() as session:
        yield session


def page_info(page_idx: int = Query(default=1, description="页数", ge=0),
              page_size: int = Query(default=10, description="每页数量", ge=0)) -> Pagination:
    return Pagination(page_idx=page_idx, page_size=page_size)


def get_actor_info(token=Depends(oauth2), session=Depends(db_session)) -> Actor:
    try:
        payload = jwt_api.decode(token)
        actor = Actor(
            session=session,
            user_uuid=payload["user_uuid"]
        )
    except Exception as e:
        raise HTTPException(401, detail=f"{e}")

    return actor
