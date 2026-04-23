#!/usr/bin/python2.7
import rospy
from std_msgs.msg import String

def main():
    # Initialize the ROS node
    rospy.init_node('chatbot_brain', anonymous=True)
    
    # Publisher to trigger the Speaker node
    tts_pub = rospy.Publisher('/input', String, queue_size=10)
    
    # Allow ROS time to connect the nodes
    rospy.sleep(1) 

    # --- STEP 1: ASK ---
    print("Bot: What is your name?")
    tts_pub.publish("What is your name?")

    # --- STEP 2: WAIT & LISTEN ---
    print("Listening for your response...")
    try:
        # Pauses here until google_sr.py sends a name to /result
        msg = rospy.wait_for_message('/start', String, timeout=15.0)
        name = msg.data
        
        # --- STEP 3: WELCOME ---
        welcome_text = "Welcome " + name
        print("Bot: " + welcome_text)
        tts_pub.publish(welcome_text)
        
    except rospy.ROSException:
        print("Error: I didn't hear a name in time.")

if __name__ == '__main__':
    main()