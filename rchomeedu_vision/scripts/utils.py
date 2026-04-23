#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
utils.py
====================================
Utility Module.
Contains pure helper functions that perform specific calculations or actions.
These functions help keep the main logic clean and readable.
"""

import math
import shared_state as st
import config as cfg

def normalize_angle(angle):
    """
    Ensures an angle stays within the standard ROS range of -PI to +PI.
    Prevents errors when angles wrap around (e.g., rotating past 180 degrees).
    """
    while angle > math.pi: 
        angle -= 2.0 * math.pi
    while angle < -math.pi: 
        angle += 2.0 * math.pi
    return angle

def stop_robot():
    """
    Immediately sets linear and angular velocities to zero and publishes them.
    Used as a safety measure and when transitioning between states.
    """
    st.speed.linear.x = 0.0
    st.speed.angular.z = 0.0
    if st.cmd_pub:
        st.cmd_pub.publish(st.speed)

def is_angle_processed(current_theta):
    """
    Checks if the robot's current heading matches an angle where a person
    was already found. Uses a tolerance to account for slight odometry drift.
    Returns True if the angle is "used", False otherwise.
    """
    for saved_angle in st.person_found_angles:
        if abs(normalize_angle(current_theta - saved_angle)) < cfg.THETA_TOLERANCE:
            return True
    return False

def get_mode():
    """
    Calculates the statistical mode (most frequent value) from the OpenPose 
    people count buffer. This filters out single-frame tracking glitches/flickers.
    """
    counts = {}
    for item in st.lst: 
        counts[item] = counts.get(item, 0) + 1
    return max(counts, key=counts.get) if counts else 0
