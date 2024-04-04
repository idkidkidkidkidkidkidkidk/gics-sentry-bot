import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # 關掉 pygame 歡迎訊息
from pygame import mixer
import requests
from dotenv import get_key
from time import sleep
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from base64 import b64decode, b64encode


# 在 .env 中填入競賽用的帳號密碼
# alert_if_script_down: 程式異常(例如網路斷掉)時, 要不要播音樂警告
alert_if_script_down = True
account = get_key('.env', 'ACCOUNT')
password = get_key('.env', 'PASSWORD')

if account == '你的帳號' or password == '你的密碼':
    print('帳密未填寫, 請在 .env 中填入競賽使用的帳號密碼')

s = requests.Session()

# 登入
public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7PIWyhn3rvv4B9UWMTriKb0J1HsAkoC25YYDoGmf019IxAgDdQZtu6fVeQIbfexQNN5qX+2hyiKUMnL+Bcllvxk1aGQVggKtNr9XAGdQjVsisLROi/VHuQoYGUxcF0TxxEgEW98uXn63Ub+uAsxadV0Tr2y5d1pFVUIVBQeXiDIS1pY1kzE0oGMN4l4/3xow973kmN6Lo3sIB8vIioeXbYUY2okZm54BpLSqtxOWp/WQlimOkZ0nJwvNr5g94PCRrBvDMCt7QlwA6VUzqPLZ0RVrWL2+JgQV/ujWFZKvOcXtoftYwjogiFPDDhQ5GQxjW/ZdswNMs0k7RPx3jmyJJwIDAQAB'
rsa_key = RSA.importKey(b64decode(public_key))
cipher_text = Cipher_PKCS1_v1_5.new(rsa_key).encrypt(password.encode())
e_pw = b64encode(cipher_text)
login_url = 'https://esports.pagamo.org/api/sign_in'
login_data = {'account': account, 'encrypted': True, 'password': e_pw}

print('正在登入...')
login_resp = s.post(login_url, data=login_data).json()
if not login_resp['status'] == 'ok':
    print('登入失敗, 請檢查 .env 中的帳號密碼是否填寫正確！')
    sleep(7) # 錯誤訊息停留幾秒再結束程式
    exit(1)
# 看起來很蠢, 但分辨測試跟正式比賽世界最好的方式是看名稱有沒有組這個字
elif not login_resp['data']['user']['current_course_info']['name'].endswith('組'):
    print('請使用比賽帳號登入')
    sleep(7) # 錯誤訊息停留幾秒再結束程式
    exit(1)
else:
    print('登入成功')
    print()

# 登入時會拿到上次進入的課程對應的 game character 資料
# 提取 gc_id 拿 personal_information 中的組別名稱
self_gcid = login_resp['data']['gc']['id']
info_url = 'https://www.pagamo.org/users/personal_information.json'
self_info = s.post(info_url).json() # 不帶參數預設為提取自己的資料
self_group = self_info['data']['gamecharacter']['group_name']

print(f'你的 id: {self_gcid}')
print(f'你的組別: {self_group}')

# 自動探索前後各3格的id, 找出隊友
# 如果發生錯誤請自行將 search_range 的數字改大
print('正在搜尋隊友的 id (請耐心等候數秒)...')
search_range = 3
teammate_gcids = list()
teammate_nicknames = list() # 順便拿隊友們的暱稱
for offset in range(-search_range, search_range + 1): # [-3, 4)
    sleep(2) # 減緩請求頻率
    check_gcid = self_gcid + offset
    info_resp = s.post(info_url, data={'gc_id': check_gcid})
    try:
        check_data = info_resp.json()
        check_group = check_data['data']['gamecharacter']['group_name']
        if check_group == self_group:
            teammate_gcids.append(check_gcid)
            teammate_nicknames.append(check_data['data']['user']['nickname'])
            if len(teammate_gcids) >= 3: # 一組三人
                break
    except KeyError:
        # 附近的帳號不是這次競賽的, 跳過
        pass


if len(teammate_gcids) == 3:
    print('搜尋成功')
    print('隊友 id: {0}'.format(' '.join(str(gcid) for gcid in teammate_gcids)))
    print('隊友暱稱: {0}'.format(' '.join(str(nick) for nick in teammate_nicknames)))
else:
    print('搜尋失敗, 請擴大搜尋範圍')
    exit(1)
    

cooldown = 3 # 每三分鐘檢查一次, 請善待 PaGamO 伺服器, 不要把他調太低
last_seen_land = [0, 0, 0]
print()
print(f'開始監視 (每 {cooldown} 分鐘檢查一次, 按 ctrl + c 可停止)')


while True:
    try:
        # 抓隊友各自的領土數
        current_land = list()
        for gcid in teammate_gcids:
            sleep(1)
            info_resp = s.post(info_url, data={'gc_id': gcid})
            land_count = info_resp.json()['data']['gamecharacter']['hexagons_count']
            current_land.append(land_count)
        
        # 記錄現在時間
        print(datetime.now().strftime('%m/%d %H:%M'), end=' ')

        if any(current < last for last, current in zip(last_seen_land, current_land)):
            print('警告: 偵測到入侵!')
            print('遭到攻擊的帳號:')
            for i in range(len(last_seen_land)):
                if current_land[i] < last_seen_land[i]:
                    print('{}, 原本土地數: {}, 現在土地數: {}'
                          .format(teammate_nicknames[i], last_seen_land[i], current_land[i]))
            # 播音樂
            mixer.init()
            mixer.music.load('./alarm.mp3')
            mixer.music.play()
            while mixer.music.get_busy():
                sleep(1) # 等待音樂結束撥放
        else:
            print('哨兵監視中, 目前土地數: {}'.format(' '.join(str(i) for i in current_land)))
            sleep(cooldown * 60) # 請善待 PaGamO 伺服器, 不要把他調太低
        last_seen_land = current_land.copy()
        
    except Exception as e:
        print(datetime.now().strftime('%m/%d %H:%M'), end=' ')
        print(f'發生錯誤: {e}')
        if alert_if_script_down:
            mixer.init()
            mixer.music.load('./alarm.mp3')
            mixer.music.play()
            while mixer.music.get_busy():
                sleep(1)
