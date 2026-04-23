#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from sound_play.libsoundplay import SoundClient
soundhandle = None 
def talk(data):
    soundhandle.say(data.data)
    rospy.sleep(.1)
if __name__ == '__main__':
    # Initialize the node
    rospy.init_node('speech_node', anonymous=True)
    soundhandle = SoundClient() 
    rospy.sleep(1) 
    soundhandle.stopAll()
    rospy.Subscriber('/speech', String, talk)
    rospy.loginfo("Speech node initialized and waiting for messages on '/speech'...")
    rospy.spin()