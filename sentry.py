import argparse
from datetime import datetime

from alarm import play_music
from utils import *

# 在 .env 中填入競賽用的帳號密碼


def sentry(members: list[Member], music_path: str, silent_on_error: bool):
    cooldown = 3  # 每三分鐘檢查一次, 請善待 PaGamO 伺服器, 不要把他調太低

    print()
    print(f'開始監視 (每 {cooldown} 分鐘檢查一次, 按 ctrl + c 可停止)')

    while True:
        try:
            attacked = False
            # 抓隊友各自的領土數
            for member in members:
                sleep(1)
                info_resp = s.post(info_url, data={'gc_id': member.gcid})
                land_count = info_resp.json()['data']['gamecharacter']['hexagons_count']
                member.current_land = land_count
                if member.current_land < member.last_seen_land:
                    attacked = True
                    member.under_attack = True

            # 記錄現在時間
            print(datetime.now().strftime('%m/%d %H:%M'), end=' ')

            if attacked:
                print('警告: 偵測到入侵!')
                print('遭到攻擊的帳號:')
                for member in members:
                    if member.under_attack:
                        print('{}, 原本土地數: {}, 現在土地數: {}'
                            .format(member.nickname, member.last_seen_land, member.current_land))
                send_message(members)
                play_music(music_path)
            else:
                print('哨兵監視中, 目前土地數: {}'.format(' '.join(str(m.current_land) for m in members)))
                sleep(cooldown * 60)  # 請善待 PaGamO 伺服器, 不要把他調太低

            for member in members:
                member.last_seen_land = member.current_land
                member.under_attack = False

        except Exception as e:
            print(datetime.now().strftime('%m/%d %H:%M'), end=' ')
            print(f'發生錯誤: {e}')

            if not silent_on_error:
                play_music(music_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='GiCS Sentry Bot')

    # 警報音樂路徑
    parser.add_argument('-m', '--music-path',
                        default='./alarm.mp3',
                        help='Path to the music used for alarm.')

    # 程式異常(例如網路斷掉)時, 要不要播音樂警告
    parser.add_argument('-s', '--silent-on-error',
                        action='store_true',
                        help='Toggle if the alarm will be played if the bot encounters an error.')

    args = parser.parse_args()
    music_path = args.music_path
    silent_on_error = args.silent_on_error

    user = get_account()
    login(user)
    teammates = get_team_member(user)
    sentry(teammates, music_path, silent_on_error)
