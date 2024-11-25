from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    # 环境标签读取配置
    model_config = ConfigDict(
        # 环境变量文件名
        env_file=".env",
        # 忽略未定义的变量
        extra="ignore"
    )

    # 数据库相关配置
    db_url: str = "postgresql://username:passwowrd@host:port/database"
    db_echo: bool = False
    pool_recycle: int = 3600

    # 密钥
    jwt_key: str = "0123456789ABCDEF"
    jwt_expire_min: int = 1440
    aes_key_16: str = "0123456789ABCDEF"
    aes_key_32: str = "0123456789ABCDEF0123456789ABCDEF"

    # FastAPI应用配置
    docs_url: str = "/docs"
    redoc_url: str = ""
    title: str = "UserCenterAPI"
    version: str = "1.0.0"

    # FastAPI的CORS配置
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["GET", "POST"]
    allow_headers: list[str] = ["*"]

    @property
    def fastapi_settings(self) -> dict:
        return dict(
            docs_url=self.docs_url,
            redoc_url=self.redoc_url,
            title=self.title,
            version=self.version
        )

    @property
    def cors(self) -> dict:
        return dict(
            allow_origins=self.allow_origins,
            allow_credentials=self.allow_credentials,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers
        )

    @property
    def db_settings(self) -> dict:
        return dict(
            url=self.db_url,
            pool_recycle=self.pool_recycle,
            echo=self.db_echo
        )


settings = APISettings()
