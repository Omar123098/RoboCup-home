#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import speech_recognition as sr
names=['sam' , 'alex', "john", "mary"]

status = True
def found(data):
    if data.data == "true":
        status = True
    else:
        status = False
rospy.Subscriber('/status', String, found)
def googlesr():
    rospy.init_node('googlesr', anonymous=True)
    pub = rospy.Publisher('/start', String, queue_size=1)
    pub2 = rospy.Publisher('/names', String, queue_size=1)
    while not rospy.is_shutdown():
        if status:
            # obtain audio from the microphone
            r = sr.Recognizer()
            
            with sr.Microphone() as source:
                print(">>> Say something!")
                #audio = r.listen(source)
                audio = r.record(source, duration=5)
                
            # recognize speech using Google Speech Recognition
            try:
                result = r.recognize_google(audio)
                print("SR result: " + result)
                if "find" in result or "guest" in result:
                    pub.publish(result)
                elif result.lower( ) in names:
                    pub2.publish(result)
            except sr.UnknownValueError:
                print("SR could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            
if __name__ == '__main__':
    try:
        googlesr()
    except rospy.ROSInterruptException:
        pass