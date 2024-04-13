import os
from base64 import b64decode, b64encode
from time import sleep

import requests
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.PublicKey import RSA
from dotenv import get_key

# 關掉 pygame 歡迎訊息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

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


def print_user(gcids: list[int], nicknames: list[str]):
    if len(gcids) == 3:
        print('搜尋成功')
        print('成員 id: {0}'.format(' '.join(str(gcid) for gcid in gcids)))
        print('成員暱稱: {0}'.format(' '.join(str(nick) for nick in nicknames)))
    else:
        print('搜尋失敗')
        exit(1)


def search_group(team_id: int, offset: int):
    search_range = 3
    gcids = list()
    nicknames = list()  # 順便拿隊友們的暱稱

    for teammate_id in range((team_id - 1) * 3 - search_range, team_id * 3 + search_range):  # [3n - 3, 3(n+1) + 4)
        sleep(0.7)  # 減緩請求頻率

        check_gcid = teammate_id + 1 + offset
        info_resp = s.post(info_url, data={'gc_id': check_gcid})

        try:
            check_data = info_resp.json()
            check_group = check_data['data']['gamecharacter']['group_name']

            if check_group == f'資安女婕思第{team_id}隊':
                gcids.append(check_gcid)
                nicknames.append(check_data['data']['user']['nickname'])

                if len(gcids) == 3:
                    break

        except KeyError:
            pass

    return gcids, nicknames


def calculate_first_player_id(user: dict):
    self_gcid = user['self_gcid']
    self_nickname = user['self_nickname']

    return self_gcid - int(self_nickname[-4:])


def get_team_member(user: dict, team_id: int = None):
    first_user_id = calculate_first_player_id(user)

    if team_id is None:
        self_group = user['self_group']
        team_id = int(self_group[6:-1])

    # 找出隊友
    print('正在搜尋成員的 id (請耐心等候數秒)...')

    teammate_gcids, teammate_nicknames = search_group(team_id, first_user_id)
    print_user(teammate_gcids, teammate_nicknames)

    return {'gcid': teammate_gcids, 'nickname': teammate_nicknames}


def progress_bar(now, total, total_blocks=50, decimal_point=2, last_percent=1):
    if now == total or now / total >= last_percent:
        print(
            f'\r[{"█" * total_blocks}] {100}%', end='')  # 輸出不換行的內容
    else:
        plus_block = "█" * (now * total_blocks // total)
        minus_block = " " * (total_blocks - (now * total_blocks // total))
        percentage = round(now * 100 / total, decimal_point)
        print(f'\r[{plus_block}{minus_block}] {percentage}%', end='')  # 輸出不換行的內容


def resolve_group_information(groups: dict, res: requests.models.Response):
    info_json = res.json()

    # 確認不要混到其他奇怪的東西進來
    if not info_json['data']['user']['nickname'] or len(info_json['data']['user']['nickname']) != 14:
        return

    group_id = int(info_json['data']['gamecharacter']['group_name'][6:-1])

    if group_id not in groups:
        groups[group_id] = {'problem_solving': [], 'land_count': [],
                            'total_correct': 0, 'total_land': 0, 'group_score': 0}

    # 把答題/土地放入
    problem = info_json['data']['gamecharacter']['problem_solving']
    land = info_json['data']['gamecharacter']['hexagons_count']

    groups[group_id]['problem_solving'].append(problem)
    groups[group_id]['land_count'].append(land)
    groups[group_id]['total_correct'] += problem
    groups[group_id]['total_land'] += land
    groups[group_id]['group_score'] += 7 * problem + 3 * land


def get_group_information(groups: dict, gcid_start: int, gcid_end: int, progress: bool = True):
    for i in range(gcid_start, gcid_end + 1):  # 範圍改成當前比賽人數
        if progress:
            progress_bar(i - gcid_start, gcid_end - 1 - gcid_start)

        sleep(0.5)

        info_resp = s.post(info_url, data={'gc_id': str(i)})  # 呼叫API

        try:
            resolve_group_information(groups, info_resp)

        except Exception as e:
            print(f'發生錯誤: {e}')
            exit(1)
