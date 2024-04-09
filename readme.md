# GiCS 初賽哨兵 bot
<p align="center">
    2024 已更新，請見 Release 頁面
</p>

這是一個被資安女婕思長達五天的初賽催生出的小工具

每三分鐘檢查隊伍每個人的土地數量，地數掉的時候播音樂通知，讓你的隊友可以安心睡覺 :sparkles:

![哨兵 bot 執行畫面](./screenshot.png)

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
- alert_if_script_down: 程式異常（例如網路斷線）時，要不要播音樂警告


## Known Issues

1. 土地被打掉時才會告警，被攻擊但土地還沒被打掉時不會發出警報
2. 警報音樂播放時不會同時偵測攻擊


## Notes

預計在初賽開始後一天內 release，出問題的話歡迎開 issue


## Todo

- 警報音樂改成只播一分鐘，避免影響偵測
- 替換警報時的動作，無縫接軌 Discord bot 等等


## Credits

alarm.mp3 來源：Different Heaven - Nekozilla [NCS Release]

Music provided by NoCopyrightSounds

Free Download/Stream: http://ncs.io/nekozilla

Watch: http://youtu.be/6FNHe3kf8_s
