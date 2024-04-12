from datetime import datetime

from alarm import play_music
from utils import *

# 在 .env 中填入競賽用的帳號密碼
# alert_if_script_down: 程式異常(例如網路斷掉)時, 要不要播音樂警告
alert_if_script_down = True


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


if __name__ == '__main__':
    user = get_account()
    login(user)
    teammates = get_team_member(user)
    sentry(teammates)
