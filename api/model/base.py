from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped as M, mapped_column as mc


class ModelPrimaryKeyID:
    id: M[int] = mc(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID"
    )


class ModelLogicDeleted:
    is_deleted: M[bool] = mc(
        Boolean,
        default=False,
        comment="数据逻辑删除标识"
    )


class ModelBase(DeclarativeBase):
    created_at: M[datetime] = mc(
        DateTime,
        default=func.now(),
        comment="数据创建时间"
    )

    updated_at: M[datetime] = mc(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        comment="数据更新时间"
    )
