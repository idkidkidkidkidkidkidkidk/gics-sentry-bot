# GiCS 初賽哨兵 bot

這是一個被 2023 GiCS 長達五天的初賽催生出的小工具

每三分鐘檢查隊伍分數，分數掉的時候通知，讓你的隊伍可以安心睡覺 :sparkles:


## 需求
請用 [Python 3](https://www.python.org/downloads/) 以上

執行前用 `pip install -r requirements.txt` 安裝需要的套件


## 使用
```
git clone https://github.com/idkidkidkidkidkidkidkidk/gics-sentry-bot.git
cd gics-sentry-bot
pip install -r requirements.txt

# 測試音量
python testvolume.py

# 在 .env 中填入競賽用的帳號密碼後再執行哨兵 bot
python sentry.py
```

可以用其他 mp3 檔案替換掉 alarm.mp3，這個音檔會在告警時播放

建議先用 testvolume.py 測試音量，調一個會把你吵醒但不會吵到鄰居的音量，測試後再執行 sentry.py

建議檢查電腦在掛機一段時間後會不會休眠，休眠很可能導致哨兵 bot 停止運作

sentry.py 的參數:
- alert_if_script_down: 程式異常（例如網路斷掉）時，要不要播音樂警告
- competition_name: 競賽在 PaGamO 上的代號，例如 `2024gics_college`
    - 這個資訊可以在競賽世界的網址中找到


## Known Issues
1. 機器人讀取的是隊伍分數，若隊伍中有人正在答題、提高分數，會無法偵測到隊友被攻擊
2. 土地被打掉時才會告警，如果能遇到攻擊就告警就好了但是相關資料實在很難拿


## Notes
2024/03 更新：已確認登入功能能夠正常運作，但競賽模式的 API 有沒有更新還要等比賽開始後確認。

預計在初賽開始後一天內 release，出問題的話歡迎開 issue


## Todo
- 擴展到非競賽（一般模式）也能用


## Credits
alarm.mp3 來源：Different Heaven - Nekozilla [NCS Release]

Music provided by NoCopyrightSounds

Free Download/Stream: http://ncs.io/nekozilla

Watch: http://youtu.be/6FNHe3kf8_s
