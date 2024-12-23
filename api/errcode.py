
class APIErr:
    NO_ERROR = dict(code=0, message="Succeed")
    WRONG_ACCOUNT_PASSWD = dict(code=1, message="账号或密码不正确")
    ACCOUNT_STATUS_DISABLE = dict(code=2, message="账号被停用")
    SUPERADMIN_PROTECT = dict(code=3, message="不能操作超级管理员账号")
    ACCOUNT_EXISTSED = dict(code=4, message="账号已存在")
    PHONE_EXISTED = dict(code=5, message="手机号已存在")
