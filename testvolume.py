from time import sleep
import vlc

p = vlc.MediaPlayer("alarm.mp3")
p.play()
sleep(300)
