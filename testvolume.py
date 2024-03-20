from time import sleep
import os

# 關掉 pygame 歡迎訊息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from pygame import mixer
mixer.init()
mixer.music.load('./alarm.mp3')
mixer.music.play()
while mixer.music.get_busy():
    sleep(1)
