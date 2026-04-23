#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
callbacks.py
====================================
ROS Callbacks Module.
These functions are triggered automatically whenever new data is published
to their respective ROS topics. They update the `shared_state` in real-time.
"""

import rospy
import numpy as np
from tf.transformations import euler_from_quaternion
from cv_bridge import CvBridgeError

import shared_state as st
import utils

from std_msgs.msg import String
import rospy
import shared_state as st

def depth_callback(data):
    """
    Listens to the 3D camera. Converts raw ROS Image messages into 
    OpenCV-compatible numpy arrays for distance calculations.
    """
    try: 
        st.raw_depth_map = st.bridge.imgmsg_to_cv2(data, "passthrough")
    except CvBridgeError: 
        pass

def odom_callback(msg):
    """
    Listens to the robot's wheels/motors. Updates the robot's current 
    position (X, Y) and converts quaternion orientation into a standard 
    Euler angle (Theta/Yaw).
    """
    st.xodom = msg.pose.pose.position.x
    st.yodom = msg.pose.pose.position.y
    rot_q = msg.pose.pose.orientation
    # We only care about the Z-axis rotation (yaw/theta) for 2D movement
    _, _, st.theta = euler_from_quaternion([rot_q.x, rot_q.y, rot_q.z, rot_q.w])
    st.odom_received = True

def pose_callback(msg):
    """
    Listens to OpenPose. Performs two main tasks:
    1. Stabilizes the people count to ignore 1-frame glitches.
    2. Identifies the person furthest to the right (highest X coordinate)
       and sets them as the active target.
    """
    if not hasattr(msg, 'poses'): return
    
    # --- Task 1: Stabilization Filter ---
    st.cnt += 1
    st.lst.append(len(msg.poses))
    if st.cnt >= 10:
        # Every 10 frames, take the most common number of people seen
        st.stable_num_people = utils.get_mode()
        st.cnt = 0
        del st.lst[:]
        
    # --- Task 2: Target the Rightmost Person ---
    if len(msg.poses) > 0:
        rightmost_x = -1
        best_y = -1
        
        # Iterate through all detected bodies
        for p in msg.poses:
            # Fallback to Nose if Chest is blocked/unseen
            px = p.Chest.x if p.Chest.x != -1 else p.Nose.x
            py = p.Chest.y if p.Chest.y != -1 else p.Nose.y
            
            # Highest X means furthest right on the screen
            if px > rightmost_x:
                rightmost_x = px
                best_y = py
                
        # Lock onto the rightmost coordinates
        st.target_chest_x = rightmost_x
        st.target_chest_y = best_y
    else:
        st.target_chest_x = -1
        st.target_chest_y = -1

def location_callback(msg):
    if "Room" in msg.data:
        # Check if we already triggered it so we don't spam the logs
        if not getattr(st, 'process_started', False):
            rospy.loginfo(">>> 'Room' command received on /location! Starting mission...")
            st.process_started = True

def names_callback(msg):
    """Listens for the person's name response."""
    if st.waiting_for_name:
        rospy.loginfo(">>> Received name: {}".format(msg.data))
        st.current_person_name = msg.data
        st.waiting_for_name = False