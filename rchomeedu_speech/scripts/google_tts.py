#!/usr/bin/python2.7
import rospy
from std_msgs.msg import String
from gtts import gTTS
import os

def callback(data):
    rospy.loginfo("Speaking: %s", data.data)
    tts = gTTS(text=data.data, lang='en')
    tts.save("speech.mp3")
    # Play through the Unitek adapter
    os.system("mpg321 -q speech.mp3")
    if os.path.exists("speech.mp3"):
        os.remove("speech.mp3")

def googletts():
    rospy.init_node('googletts', anonymous=True)
    # Listen to the '/input' topic
    rospy.Subscriber("/start", String, callback)
    rospy.spin()

if __name__ == '__main__':
    googletts()