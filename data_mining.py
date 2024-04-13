import pickle

from utils import *
from utils import calculate_first_player_id, s, info_url


def get_all_data(player: dict):
    # 修改方向: 第一次先抓所有人(935)的資訊，然後與自己組比較
    # 1. 剩餘題數多 + 土地多的 (打爛他)
    # 2. 剩餘題數少 + 土地多的 (待觀察)
    # 3. 剩餘題數多 + 土地少的 (待觀察)
    # 4. 剩餘題數少 + 土地少的 (安全)

    gics_winner = {}
    first_user_id = calculate_first_player_id(player)

    start = -2
    end = 45

    print("開始爬取資料：")
    for i in range(start, end):  # 範圍改成當前比賽人數
        progress_bar(i - start, end - 1 - start)
        sleep(1)

        info_resp = s.post(info_url, data={'gc_id': str(first_user_id + i)})  # 呼叫API

        try:
            info_json = info_resp.json()

            # 確認不要混到其他奇怪的東西進來
            if not info_json['data']['user']['nickname'] or len(info_json['data']['user']['nickname']) != 14:
                continue

            group_id = int(info_json['data']['gamecharacter']['group_name'][6:-1])

            if group_id not in gics_winner:
                gics_winner[group_id] = {'problem_solving': [], 'land_count': [],
                                         'total_correct': 0, 'total_land': 0, 'group_score': 0}

            # 檢查 484 GICS 的帳號
            # 把答題 / 土地 / 總分放入
            problem = info_json['data']['gamecharacter']['problem_solving']
            land = info_json['data']['gamecharacter']['hexagons_count']

            gics_winner[group_id]['problem_solving'].append(problem)
            gics_winner[group_id]['land_count'].append(land)

        except Exception as e:
            print(f'發生錯誤: {e}')
            exit(1)

    for group_id in gics_winner:
        total_correct = sum(gics_winner[group_id]['problem_solving'])
        total_land = sum(gics_winner[group_id]['land_count'])
        data = {'total_correct': total_correct, 'total_land': total_land,
                'group_score': total_correct * 7 + total_land * 3}

        gics_winner[group_id].update(data)

    print('\n')
    print(f"result: {gics_winner}")

    # 存檔
    with open('gics_winner.pickle', 'wb') as f:
        pickle.dump(gics_winner, f)
    return


if __name__ == '__main__':
    user = get_account()
    login(user)
    get_all_data(user)
