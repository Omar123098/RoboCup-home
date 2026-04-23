#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
shared_state.py
====================================
Shared Memory Module.
Instead of passing dozens of variables between functions or using global 
variables in a single massive file, this file acts as a centralized "whiteboard".
All modules read from and write to this state file.
"""

from geometry_msgs.msg import Twist
from cv_bridge import CvBridge

# --- ROS Infrastructure ---
bridge = CvBridge()   # Tool to convert ROS Image messages to OpenCV format
cmd_pub = None        # Placeholder for the velocity publisher
pose_sub = None       # Placeholder for the OpenPose subscriber
speed = Twist()       # Standard ROS velocity message

# --- Mission State Tracking ---
mission_state = "INIT"       # Current state of the state machine
people_found_count = 0       # How many distinct people the robot has successfully tracked
person_found_angles = []     # List of angles where people were found (to prevent double-counting)

target_theta = 0.0           # The angle the robot is currently trying to rotate to
search_start_time = None     # Timestamp used for the SEARCH_WAIT_TIME delay
initial_person_dist = None   # Distance recorded when a person is first spotted    

# --- Sensor Data (Live Updates) ---
raw_depth_map = None         # Latest 2D array of depth data from the camera
xodom = 0.0                  # Current X coordinate from odometry
yodom = 0.0                  # Current Y coordinate from odometry
theta = 0.0                  # Current heading (yaw) from odometry
home_x = None                # X coordinate where the mission started
home_y = None                # Y coordinate where the mission started
home_theta = None            # Heading where the mission started
odom_received = False        # Flag to ensure odometry is active before moving

# --- OpenPose Tracking Data ---
stable_num_people = 0        # Filtered count of people currently in frame
target_chest_x = -1          # Pixel X-coordinate of the targeted person
target_chest_y = -1          # Pixel Y-coordinate of the targeted person
cnt = 0                      # Counter for the stabilization filter
lst = []                    # Buffer of recent people counts for the stabilization filter

# Add these near the bottom of shared_state.py
current_cv_image = None
people_data = []
used_features = []

# --- Sync Data ---
waiting_for_name = False     # Flag to pause the robot while waiting for a name
current_person_name = None   # Temporarily holds the received name
latest_gemini_data = {}      # Temporarily holds the JSON output from Gemini
name_pub = None              # Publisher to ask for the name
