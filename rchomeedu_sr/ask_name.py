#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from gtts import gTTS
import speech_recognition as sr
import os

user_name = None

def speak(text):
    rospy.loginfo("Speaking: %s", text)
    tts = gTTS(text)
    tts.save("speech.mp3")
    os.system("mpg321 speech.mp3")
    os.remove("speech.mp3")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        rospy.loginfo("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=10, phrase_time_limit=7)

    try:
        result = r.recognize_google(audio)
        rospy.loginfo("SR result: %s", result)
        return result
    except:
        rospy.logwarn("Speech not understood")
        return None

def ask_name_and_save():
    global user_name

    speak("What is your name?")
    answer = listen()

    if answer:
        user_name = answer
        rospy.loginfo("User name saved: %s", user_name)

        with open('/home/mustar/catkin_ws/src/jupiterobot/scripts/detected_name.txt', 'w') as f:
            f.write(user_name + '\n')

        speak("Nice to meet you " + user_name)

    else:
        speak("Sorry, I did not catch that")

def trigger_callback(msg):
    rospy.loginfo("Received signal: %s", msg.data)

    if "find my guest" in msg.data:
        ask_name_and_save()

if __name__ == '__main__':
    rospy.init_node('ask_name_node')

    rospy.Subscriber('/command', String, trigger_callback)

    rospy.loginfo("Waiting for command: 'find my guest'")

    rospy.spin()
