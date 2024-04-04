from time import sleep
import os

# 關掉 pygame 歡迎訊息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

print('正在播放音樂 (按 ctrl + c 可停止)...')
mixer.init()
mixer.music.load('./alarm.mp3')
mixer.music.play()
while mixer.music.get_busy():
    sleep(1)

print('播放完畢')