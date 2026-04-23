#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from std_msgs.msg import String # <--- ADD THIS IMPORT
from cv_bridge import CvBridge

import shared_state as st
import callbacks
import states_logic
import utils
import gemini_functions

if __name__ == '__main__':
    try:
        print(">>> Python 2 ROS Environment Initialized...")
        rospy.init_node('auto_tracker_simple', anonymous=False)
        
        if not hasattr(st, 'bridge'):
            st.bridge = CvBridge()
        # ---> ADD THE NEW PUBLISHER & SUBSCRIBER HERE <---        
        
        rospy.Subscriber("/camera_top/depth_registered/image_raw", Image, callbacks.depth_callback)
        rospy.Subscriber('/odom', Odometry, callbacks.odom_callback)
        rospy.Subscriber("/camera_top/rgb/image_raw", Image, gemini_functions.rgb_image_callback)
        rospy.Subscriber("/location", String, callbacks.location_callback)
        rospy.Subscriber('/names', String, callbacks.names_callback)

        # st.name_pub = rospy.Publisher('/name', String, queue_size=1)
        st.status_pub = rospy.Publisher('/status', String, queue_size=1)
        st.talk_pub = rospy.Publisher('/speech', String, queue_size=1)
        st.cmd_pub = rospy.Publisher('/cmd_vel_mux/input/navi', Twist, queue_size=10)
        st.go_home=rospy.Publisher('/home',String, queue_size=1)
        # Initialize our starting flag
        st.process_started = False
        
        rate = rospy.Rate(10) 
        rospy.loginfo("Node started. Awaiting sensor data and 'Room' trigger...")

        while not rospy.is_shutdown():
            # Gate 1: THE ROOM TRIGGER WAITER <---
            if not st.process_started:
                if st.pose_sub is not None:
                    st.pose_sub.unregister()
                rospy.loginfo_throttle(3, "Standing by. Waiting for 'Room' to be published to /location...")
                rate.sleep()
                continue

            # Gate 2: Check for ultimate mission completion
            if getattr(st, 'people_found_count', 0) >= 3:
                utils.stop_robot()
                rospy.loginfo("MISSION COMPLETE! 3 people found.")
                st.go_home.publish("Go home")
                rospy.loginfo("going home")
                break 

            # Gate 3: Safety check for sensors
            if getattr(st, 'raw_depth_map', None) is None or not getattr(st, 'odom_received', False):
                rospy.loginfo_throttle(5, "Waiting for sensor data (Depth Map / Odom)...")
                rate.sleep()
                continue
            
            # Gate 4: State Machine Executor
            if st.mission_state == "INIT": 
                states_logic.run_init()
            elif st.mission_state == "SEARCH_WAITING": 
                states_logic.run_search_waiting()
            elif st.mission_state == "SEARCH_ROTATING": 
                states_logic.run_search_rotating()
            elif st.mission_state == "APPROACHING": 
                states_logic.run_approaching()
            elif st.mission_state == "RETURNING": 
                states_logic.run_returning()
            
            rate.sleep()
            
    except rospy.ROSInterruptException:
        pass