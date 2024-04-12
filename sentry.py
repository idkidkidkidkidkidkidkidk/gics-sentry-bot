import os

from utils import *

# 在 .env 中填入競賽用的帳號密碼
# alert_if_script_down: 程式異常(例如網路斷掉)時, 要不要播音樂警告
alert_if_script_down = True

if __name__ == '__main__':
    user = get_account()
    login(user)
    teammates = get_teammate(user)
    sentry(teammates)
