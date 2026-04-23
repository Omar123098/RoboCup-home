#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
config.py
====================================
Configuration Module for the Auto-Tracker.
This file holds all the hardcoded physical parameters, thresholds, and limits.
Tweak these values to adjust the robot's sensitivity, speed, and search behavior.
"""

import math

# --- Camera & Image Parameters ---
IMAGE_WIDTH = 640            # Width of the camera resolution in pixels
CENTER_X = IMAGE_WIDTH / 2.0 # The pixel X-coordinate representing the center of the robot's vision
CENTER_TOLERANCE = 50        # Pixel tolerance for aligning the robot to the target (deadband)

# --- Physical Distance Parameters (Meters) ---
TARGET_DIST = 0.7           # The ideal distance to maintain from the person when approaching
DIST_TOLERANCE = 0.2        # Acceptable error margin when moving to TARGET_DIST
RETURN_TOLERANCE = 0.4      # Acceptable error margin when reversing back to the original spot

# --- Search & Rotation Parameters ---
SEARCH_WAIT_TIME = 2         # Seconds the robot waits at a specific angle to scan for people
ANGLE_STEP = math.radians(60)# How far the robot rotates per search step (45 degrees)
THETA_TOLERANCE = math.radians(30) # Margin to determine if an angle has already been searched
