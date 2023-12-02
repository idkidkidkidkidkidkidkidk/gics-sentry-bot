# GiCS 初賽哨兵 bot

這是一個被 2023 GiCS 長達五天的初賽催生出的小工具

每三分鐘檢查隊伍分數，分數掉的時候通知，讓你的隊伍可以安心睡覺 :sparkles:


## 需求
請用 [Python 3](https://www.python.org/downloads/) 以上

使用前先下 `pip install -r requirements.txt`

如果電腦上沒有裝 [VLC](https://www.videolan.org/vlc/index.zh_TW.html) 可以用 novlc 版本，但沒有 VLC 的版本應該只有 Windows 能用


## 使用
右上角 Code > Download ZIP，下載後解壓縮

在程式資料夾中，放入一個 alarm.mp3 音檔於告警時播放，由於版權問題先不附上我用的音檔


在 .env 中填入競賽用的帳號密碼


用 testvolume.py 測試音量，調一個會把你吵醒但不會吵到鄰居的音量。建議先測試後再執行 checkscore.py


checkscore.py 的參數:
- alert_if_script_down: 程式異常（例如網路斷掉）時，要不要播音樂警告
- competition_name: 競賽在 PaGamO 上的代號，例如 `2023gics_college`


建議檢查電腦在掛機一段時間後會不會休眠，休眠很可能導致哨兵 bot 停止運作


## Known Issues
1. 比賽中沒有找到直接獲取領地數或偵測有人攻擊的方法，隊伍中有任何一人正在答題時，會沒辦法偵測到攻擊
2. 偵測分數也不是個好方法，一定要等土地被打掉時才會告警


## Notes
歡迎 fork 成不用 VLC 也能支援其他作業系統的版本，我沒有 Mac QQ

這個 bot 在競賽後除了登入功能外沒有測試過，很可能會因為 PaGamo 改版而壞掉，出問題的話歡迎開 issue

## Credits
alarm.mp3 來源：Different Heaven - Nekozilla [NCS Release]
Music provided by NoCopyrightSounds
Free Download/Stream: http://ncs.io/nekozilla
Watch: http://youtu.be/6FNHe3kf8_s
