import os
from time import sleep

# 關掉 pygame 歡迎訊息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer


def play_music():
    # 播音樂
    mixer.init()
    mixer.music.load('./alarm.mp3')
    mixer.music.play()
    while mixer.music.get_busy():
        sleep(1)  # 等待音樂結束撥放


def test_volume():
    print('正在播放音樂 (按 ctrl + c 可停止)...')
    play_music()
    print('播放完畢')


if __name__ == '__main__':
    test_volume()
