import pickle

from utils import *
from utils import calculate_first_player_id, s


def get_all_data(player: dict):
    # 修改方向: 第一次先抓所有人(935)的資訊，然後與自己組比較
    # 1. 剩餘題數多 + 土地多的 (打爛他)
    # 2. 剩餘題數少 + 土地多的 (待觀察)
    # 3. 剩餘題數多 + 土地少的 (待觀察)
    # 4. 剩餘題數少 + 土地少的 (安全)

    first_user_id = calculate_first_player_id(player)
    start = -2 + first_user_id
    end = 44 + first_user_id

    print("開始爬取資料：")
    groups = {}
    get_group_information(groups, start, end)

    print('\n')
    print(f"result: {groups}")

    # 存檔
    with open('gics_winner.pickle', 'wb') as f:
        pickle.dump(groups, f)
    return


def top_50_brief():
    url = 'https://www.pagamo.org/api/rankings/ranking_data'
    resp = s.get(url, params={'name': 'contest_by_team', 'type': 'scoring'})
    top_50 = resp.json()['topten']
    return top_50


if __name__ == '__main__':
    user = get_account()
    login(user)
    # print(top_50_full(user))
    get_all_data(user)
