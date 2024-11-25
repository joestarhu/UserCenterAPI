from jhu.security import AESAPI, HashAPI, JWTAPI
from api.config import settings


client_aes_api = AESAPI(settings.aes_key_32)
server_aes_api = AESAPI(settings.aes_key_16)
hash_api = HashAPI()
jwt_api = JWTAPI(settings.jwt_key, expire_min=settings.jwt_expire_min)
