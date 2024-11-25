
class APIErr:
    NO_ERROR = dict(code=0, message="Succeed")
    WRONG_ACCOUNT_PASSWD = dict(code=1, message="账号或密码不正确")
    ACCOUNT_STATUS_DISABLE = dict(code=2, message="账号被停用")
