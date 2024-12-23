from uuid import uuid4
from jhu.security import AESAPI, HashAPI, JWTAPI
from api.config import settings


hash_api = HashAPI()
client_aes_api = AESAPI(settings.aes_key_32)
server_aes_api = AESAPI(settings.aes_key_16)
jwt_api = JWTAPI(settings.jwt_key, expire_min=settings.jwt_expire_min)


def create_uuid() -> str:
    """随机创建一个uuid
    """
    return "".join(str(uuid4()).split("-"))
