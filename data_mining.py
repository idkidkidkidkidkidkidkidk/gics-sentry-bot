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
    end = 944 + first_user_id

    print("開始爬取資料：")
    groups = {}
    get_group_information(groups, start, end)

    print('\n')

    # 存檔
    with open('gics_winner.pickle', 'wb') as f:
        pickle.dump(groups, f)
    return


def top_50_brief():
    url = 'https://www.pagamo.org/api/rankings/ranking_data'
    resp = s.get(url, params={'name': 'contest_by_team', 'type': 'scoring'})
    top_50 = resp.json()['topten']
    return top_50


def scoreboard(limit: int = None):
    with open('gics_winner.pickle', 'rb') as f:
        loaded_data = pickle.load(f)

    # 按小組總分排名
    sorted_ranking = sorted(loaded_data.items(), key=lambda x: x[1]['group_score'], reverse=True)
    if limit:
        sorted_ranking = sorted_ranking[:limit]

    # 輸出排名結果
    print("目前分數排行")
    for rank, (index, info) in enumerate(sorted_ranking, start=1):
        print("第{:03d}隊: {:04d}分 - 第{}名".format(index, info['group_score'], rank))


if __name__ == '__main__':
    user = get_account()
    login(user)
    get_all_data(user)
    scoreboard()
