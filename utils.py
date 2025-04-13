from base64 import b64decode, b64encode
from time import sleep

import requests
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.PublicKey import RSA
from dotenv import get_key

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


def login_check(res: dict):
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


def set_user(res: dict, user: dict):
    # 登入時會拿到上次進入的課程對應的 game character 資料
    # 提取 gc_id 拿 personal_information 中的組別名稱
    self_gcid = res['data']['gc']['id']

    self_info = s.post(info_url).json()  # 不帶參數預設為提取自己的資料
    self_nickname = self_info['data']['user']['nickname']
    self_group = self_info['data']['gamecharacter']['group_name']

    print(f'你的 id: {self_gcid}')
    print(f'你的名稱: {self_nickname}')
    print(f'你的組別: {self_group}')
    print()

    user['self_gcid'] = self_gcid
    user['self_nickname'] = self_nickname
    user['self_group'] = self_group


def login(user: dict):
    # 登入
    login_url = 'https://esports.pagamo.org/api/sign_in'
    login_data = {'account': user['account'], 'encrypted': True, 'password': user['password']}

    print('正在登入...')
    login_resp = s.post(login_url, data=login_data).json()

    login_check(login_resp)
    set_user(login_resp, user)


def print_team_members(gcids: list[int], nicknames: list[str]):
    if len(gcids) == 3:
        print('\n\n')
        print('搜尋成功')
        print('成員 id: {0}'.format(' '.join(str(gcid) for gcid in gcids)))
        print('成員暱稱: {0}'.format(' '.join(str(nick) for nick in nicknames)))
    else:
        print('搜尋失敗')
        exit(1)


def progress_bar(now, total, total_blocks=50, decimal_point=2, last_percent=1):
    if now == total or now / total >= last_percent:
        print(
            f'\r[{"█" * total_blocks}] {100:0.{decimal_point}f}%', end='')  # 輸出不換行的內容
    else:
        plus_block = "█" * (now * total_blocks // total)
        minus_block = " " * (total_blocks - (now * total_blocks // total))
        percentage = round(now * 100 / total, decimal_point)
        print(f'\r[{plus_block}{minus_block}] {percentage}%', end='')  # 輸出不換行的內容


def search_group(user: dict):
    self_gcid = user['self_gcid']
    self_group = user['self_group']

    search_range = 3
    gcids = list()
    nicknames = list()  # 順便拿隊友們的暱稱

    for offset in range(-search_range, search_range + 1):  # [-3, 4)
        sleep(0.7)  # 減緩請求頻率

        check_gcid = self_gcid + offset
        info_resp = s.post(info_url, data={'gc_id': check_gcid})

        try:
            check_data = info_resp.json()
            check_group = check_data['data']['gamecharacter']['group_name']

            if check_group == self_group:
                gcids.append(check_gcid)
                nicknames.append(check_data['data']['user']['nickname'])

            progress_bar(len(gcids), 3)

            if len(gcids) == 3:
                break

        except KeyError:
            pass

    return gcids, nicknames


def get_team_member(user: dict):
    # 找出隊友
    print('正在搜尋成員的 id (請耐心等候數秒)...')

    teammate_gcids, teammate_nicknames = search_group(user)
    print_team_members(teammate_gcids, teammate_nicknames)

    return {'gcid': teammate_gcids, 'nickname': teammate_nicknames}


# To be refactored into a class
def build_message(teammate_nicknames: list[str], last_seen_land: list[int], current_land: list[int]):
    message = '## ⚠️ 警告：偵測到入侵！\n'\

    attacked_template = '{}, 土地數 {} -> {} (<@{}>)\n'

    teammate_discord_ids = get_key('.env', 'TEAMMATE_IDS').split(',')

    for i in range(len(last_seen_land)):
        if current_land[i] < last_seen_land[i]:
            message += attacked_template.format(teammate_nicknames[i],
                                                last_seen_land[i],
                                                current_land[i],
                                                teammate_discord_ids[i])
    return message


def send_message(teammate_nicknames: list[str], last_seen_land: list[int], current_land: list[int]):
    webhook_url = get_key('.env', 'WEBHOOK_URL')
    payload = {'content': build_message(teammate_nicknames, last_seen_land, current_land)}
    requests.post(webhook_url, payload)
