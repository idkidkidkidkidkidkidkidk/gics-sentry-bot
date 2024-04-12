import os
from base64 import b64decode, b64encode
from datetime import datetime
from time import sleep

import requests
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.PublicKey import RSA
from dotenv import get_key

# 關掉 pygame 歡迎訊息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

info_url = 'https://www.pagamo.org/users/personal_information.json'
s = requests.Session()


def encrypt_password(password: str):
    public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7PIWyhn3rvv4B9UWMTriKb0J1HsAkoC25YYDoGmf019IxAgDdQZtu6fVeQIbfexQNN5qX+2hyiKUMnL+Bcllvxk1aGQVggKtNr9XAGdQjVsisLROi/VHuQoYGUxcF0TxxEgEW98uXn63Ub+uAsxadV0Tr2y5d1pFVUIVBQeXiDIS1pY1kzE0oGMN4l4/3xow973kmN6Lo3sIB8vIioeXbYUY2okZm54BpLSqtxOWp/WQlimOkZ0nJwvNr5g94PCRrBvDMCt7QlwA6VUzqPLZ0RVrWL2+JgQV/ujWFZKvOcXtoftYwjogiFPDDhQ5GQxjW/ZdswNMs0k7RPx3jmyJJwIDAQAB'
    rsa_key = RSA.importKey(b64decode(public_key))
    cipher_text = Cipher_PKCS1_v1_5.new(rsa_key).encrypt(password.encode())
    return b64encode(cipher_text)


def get_account():
    account = get_key('.env', 'ACCOUNT')
    password = get_key('.env', 'PASSWORD')

    if account == '你的帳號' or password == '你的密碼':
        print('帳密未填寫, 請在 .env 中填入競賽使用的帳號密碼')
        exit(1)

    return {'account': account, 'password': encrypt_password(password)}


def login_check(res: requests.models.Response):
    if not res['status'] == 'ok':
        print('登入失敗, 請檢查 .env 中的帳號密碼是否填寫正確！')
        sleep(7)  # 錯誤訊息停留幾秒再結束程式
        exit(1)

    # 看起來很蠢, 但分辨測試跟正式比賽世界最好的方式是看名稱有沒有組這個字
    if not res['data']['user']['current_course_info']['name'].endswith('組'):
        print('請使用比賽帳號登入')
        sleep(7)  # 錯誤訊息停留幾秒再結束程式
        exit(1)

    print('登入成功\n')


def set_user(res: requests.models.Response, user: dict):
    # 登入時會拿到上次進入的課程對應的 game character 資料
    # 提取 gc_id 拿 personal_information 中的組別名稱
    self_gcid = res['data']['gc']['id']

    self_info = s.post(info_url).json()  # 不帶參數預設為提取自己的資料
    self_group = self_info['data']['gamecharacter']['group_name']

    print(f'你的 id: {self_gcid}')
    print(f'你的組別: {self_group}')

    user['self_gcid'] = self_gcid
    user['self_group'] = self_group


def login(user: dict):
    # 登入
    login_url = 'https://esports.pagamo.org/api/sign_in'
    login_data = {'account': user['account'], 'encrypted': True, 'password': user['password']}

    print('正在登入...')
    login_resp = s.post(login_url, data=login_data).json()

    login_check(login_resp)
    set_user(login_resp, user)


def get_teammate(user: dict):
    self_gcid = user['self_gcid']
    self_group = user['self_group']

    # 找出隊友
    print('正在搜尋隊友的 id (請耐心等候數秒)...')
    team_id = (self_gcid - 1) // 3 + 1
    teammate_gcids = list()
    teammate_nicknames = list()  # 順便拿隊友們的暱稱

    for teammate_id in range((team_id - 1) * 3, team_id * 3):  # [3n, 3(n+1))
        sleep(2)  # 減緩請求頻率

        check_gcid = teammate_id + 1
        info_resp = s.post(info_url, data={'gc_id': check_gcid})

        try:
            check_data = info_resp.json()
            check_group = check_data['data']['gamecharacter']['group_name']
            if check_group == self_group:
                teammate_gcids.append(check_gcid)
                teammate_nicknames.append(check_data['data']['user']['nickname'])
        except KeyError:
            pass

    if len(teammate_gcids) == 3:
        print('搜尋成功')
        print('隊友 id: {0}'.format(' '.join(str(gcid) for gcid in teammate_gcids)))
        print('隊友暱稱: {0}'.format(' '.join(str(nick) for nick in teammate_nicknames)))
    else:
        print('搜尋失敗')
        exit(1)

    return {'gcid': teammate_gcids, 'nickname': teammate_nicknames}


def play_music():
    # 播音樂
    mixer.init()
    mixer.music.load('./alarm.mp3')
    mixer.music.play()
    while mixer.music.get_busy():
        sleep(1)  # 等待音樂結束撥放


def sentry(teammates: dict):
    teammate_gcids = teammates['gcid']
    teammate_nicknames = teammates['nickname']

    cooldown = 3  # 每三分鐘檢查一次, 請善待 PaGamO 伺服器, 不要把他調太低
    last_seen_land = [0] * len(teammate_gcids)

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

            attack = False
            for i in range(len(teammate_gcids)):
                if current_land[i] < last_seen_land[i]:
                    attack = True
                    print('警告: 偵測到入侵!')
                    print('遭到攻擊的帳號:')
                    print('{}, 原本土地數: {}, 現在土地數: {}'
                          .format(teammate_nicknames[i], last_seen_land[i], current_land[i]))

                    play_music()

            if not attack:
                print('哨兵監視中, 目前土地數: {}'.format(' '.join(str(i) for i in current_land)))
                sleep(cooldown * 60)  # 請善待 PaGamO 伺服器, 不要把他調太低

            last_seen_land = current_land.copy()

        except Exception as e:
            print(datetime.now().strftime('%m/%d %H:%M'), end=' ')
            print(f'發生錯誤: {e}')

            if int(get_key('.env', 'ALERT_IF_SCRIPT_DOWN')):
                play_music()
