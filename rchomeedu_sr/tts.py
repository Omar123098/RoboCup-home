#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from sound_play.libsoundplay import SoundClient

soundhandle = None
wait_for_name = False

# Trigger listening mode
def start_callback(data):
    global wait_for_name
    rospy.loginfo("Received on /start")
    wait_for_name = True

# Speak anything from /talk
def talk_callback(data):
    text = data.data
    rospy.loginfo("Speaking from /talk: %s", text)
    soundhandle.stopAll()
    soundhandle.say(text)

# Handle name response
def name_callback(data):
    global wait_for_name

    if not wait_for_name:
        return

    name = data.data
    rospy.loginfo("Received on /names: %s", name)

    soundhandle.stopAll()
    soundhandle.say(name)

    wait_for_name = False


if __name__ == '__main__':
    rospy.init_node('tts_guest_node', anonymous=True)

    soundhandle = SoundClient()
    rospy.sleep(1)

    rospy.Subscriber('/start', String, start_callback)
    rospy.Subscriber('/talk', String, talk_callback)   
    rospy.Subscriber('/names', String, name_callback)

    rospy.loginfo("TTS node is running...")
    rospy.spin()