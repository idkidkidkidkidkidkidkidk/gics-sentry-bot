import argparse
import os
from time import sleep

# 關掉 pygame 歡迎訊息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer


def play_music(music_path: str):
    # 最多播 30 秒音樂
    timer = 30
    
    mixer.init()
    mixer.music.load(music_path)
    mixer.music.play()
    while mixer.music.get_busy():
        timer -= 1
        sleep(1)  # 每次倒數一秒, 等待音樂結束撥放
        if timer <= 0:
            mixer.music.stop()


def test_volume(music_path: str):
    print('正在播放音樂 (按 ctrl + c 可停止)...')
    play_music(music_path)
    print('播放完畢')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Alarm volume test')

    # 警報音樂路徑
    parser.add_argument('-m', '--music-path',
                        default='./alarm.mp3',
                        help='Path to the music used for alarm.')
    
    args = parser.parse_args()
    music_path = args.music_path

    test_volume(music_path)