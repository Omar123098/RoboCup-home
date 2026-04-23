#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import speech_recognition as sr

names = {
    'emma': ['amma', 'em a', 'im a', 'em', 'anna', 'ima','ema'],
    'mickel': ['michael', 'nickel', 'pickle', 'mikel', 'micheal', 'michel'],
    'sara': ['sarah', 'zara', 'serum', 'sorrow', 'sahra', 'sierra'],
    'adel': ['adil','adeel','adele', 'a dell', 'odell', 'adult', 'add ell', 'idel'],
    'dima': ['deema', 'demon', 'lima', 'team a', 'beam a', 'dim a', 'teema'],
    'rola': ['roll a', 'roller', 'lola', 'row la'],
    'nour': ['north','noor', 'nor', 'more', 'door', 'snore', 'knoor','news','nurse','no'],
    'farah': ['far a', 'pharaoh', 'fara', 'fair a', 'ferra','father','vera'],
    'carol': ['barrel', 'apparel', 'coral', 'car roll', 'carl'],
    'tony': ['pony', 'bony', 'toe knee', 'to any', 'tommy', 'toni'],
    'alex': ['alice', 'alec', "i let's", 'a lex', 'allix'],
    'john': ['zoom','don', 'ron', 'jan', 'jawn', 'jean', 'chon', 'shawn', 'sean', 'jaw', 'yawn', 'drawn', 'jon', 'joan', 'jaon', 'june'],
    'sam': ['same','san', 'sand', 'pam', 'cam', 'ham', 'jam', 'ram', 'slam', 'scam', 'some', 'sum', 'sim', 'sem'],
    'mike': ['mic', 'mick', 'mac', 'mack', 'make', 'bike', 'hike', 'like', 'pike', 'might', 'mite', 'my', 'mk'],
    'mark': ['bark', 'dark', 'park', 'mock', 'marc']
}

status = True
def enable(data):
    global status
    if data.data == 'true':
        status = True
    elif data.data== 'false':
        status = False

def googlesr():
    global started
    global pub2
    rospy.init_node('googlesr', anonymous=True)
    # Initialize publishers BEFORE the loops/callbacks so they have time to connect
    pub = rospy.Publisher('/start', String, queue_size=10)
    pub2 = rospy.Publisher('/names', String, queue_size=10)
    pub3 = rospy.Publisher('/speech', String, queue_size=10)
    rospy.Subscriber('/status', String ,enable)
    r = sr.Recognizer()
    
    while not rospy.is_shutdown():
        if status:
            with sr.Microphone() as source:
                rospy.loginfo("start to talk")
                audio = r.record(source,duration=2.5)
            try:
                result = r.recognize_google(audio).lower()
                print("Recognized: " + result)
                if "find" in result or "guest" in result:
                    pub.publish(result)
                    print("Published to 'start'.")
                elif result in names:
                    pub2.publish(result)
                    pub3.publish("Hi, "+result)
                    # print(result)
                else:
                    for correct_name, wrong_versions in names.items():
                        if result in wrong_versions:
                            pub2.publish(correct_name) # Publish the normalized/correct name
                            # print(correct_name)
                            pub3.publish("Hi, " + correct_name)
                            break

            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print("Request Error; {0}".format(e))
        
            rospy.sleep(0.1)

if __name__ == '__main__':
    try:
        googlesr()
    except rospy.ROSInterruptException:
        pass
