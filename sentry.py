import argparse
from datetime import datetime

from alarm import play_music
from utils import *

def sentry(members: list[Member], args):
    cooldown = 3  # 每三分鐘檢查一次, 請善待 PaGamO 伺服器, 不要把他調太低
    last_reported_hour = None # 每小時就算沒有被入侵，也傳一次訊息到 Discord

    print()
    print(f'開始監視 (每 {cooldown} 分鐘檢查一次, 按 ctrl + c 可停止)')

    while True:
        try:
            now = datetime.now()

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
            print(now.strftime('%m/%d %H:%M'), end=' ')

            if attacked:
                print('警告: 偵測到入侵!')
                print('遭到攻擊的帳號:')
                for member in members:
                    if member.under_attack:
                        print('{}, 原本土地數: {}, 現在土地數: {}'
                            .format(member.nickname, member.last_seen_land, member.current_land))
                send_report(members, attacked=True)
                play_music(args.music_path)
            else:
                print('哨兵監視中, 目前土地數: {}'.format(' '.join(str(m.current_land) for m in members)))
                if args.use_discord and not args.no_hourly_report:
                    if now.hour != last_reported_hour:
                        last_reported_hour = now.hour
                        send_report(members, attacked=False)
                sleep(cooldown * 60)  # 請善待 PaGamO 伺服器, 不要把他調太低


            for member in members:
                member.last_seen_land = member.current_land
                member.under_attack = False

        except Exception as e:
            print(datetime.now().strftime('%m/%d %H:%M'), end=' ')
            print(f'發生錯誤: {e}')

            if not args.silent_on_error:
                play_music(args.music_path)
                if args.use_discord:
                    send_error(error_message=str(e))
                


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='GiCS Sentry Bot')

    # 警報音樂路徑
    parser.add_argument('-m', '--music-path',
                        default='./alarm.mp3',
                        help='Path to the music used for alarm')

    # 程式異常(例如網路斷掉)時, 要不要播音樂警告
    parser.add_argument('-s', '--silent-on-error',
                        action='store_true',
                        help='Whether or not the alarm will sound if the bot encounters an error')

    # 是否使用 discord webhook 發送訊息
    parser.add_argument('-d', '--use-discord',
                        action='store_true',
                        help='Whether or not the bot will send messages to Discord via webhook')
    
    # 是否停用 discord webhook 每小時報時
    parser.add_argument('-n', '--no-hourly-report',
                        action='store_true',
                        help='Whether or not the bot will send a message every hour, even when no attack is detected')
    
    args = parser.parse_args()


    # 開始程式前先檢查 .env 有沒有填好
    if args.use_discord and get_key('.env', 'WEBHOOK_URL').endswith('.'):
        print('Webhook URL 未填寫, 請在 .env 中填入 Discord webhook URL')
        exit(1)

    account = get_key('.env', 'ACCOUNT')
    password = get_key('.env', 'PASSWORD')

    if account == '2025gics-c0000' or password == 'abcd1234':
        print('帳密未填寫, 請在 .env 中填入競賽使用的帳號密碼')
        exit(1)
    
    user = {'account': account, 'password': encrypt_password(password)}
    login(user)
    teammates = get_team_member(user)
    sentry(teammates, args)
