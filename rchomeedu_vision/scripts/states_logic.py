#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
states_logic.py
====================================
State Machine Module.
"""

import rospy
import numpy as np
from robot_vision_msgs.msg import HumanPoses

import config as cfg
import shared_state as st
import utils
import callbacks
# import gemini_functions # Imported to trigger the API

def run_init():
    if st.pose_sub is not None:
        st.pose_sub.unregister()
    if st.odom_received:
        st.home_x, st.home_y, st.home_theta = st.xodom, st.yodom, st.theta
        st.target_theta = st.home_theta 
        rospy.loginfo("[INIT] Home coordinates saved. Transitioning to SEARCH_WAITING at angle 0.")
        st.mission_state = "SEARCH_WAITING"
        st.search_start_time = rospy.Time.now()

def run_search_waiting():
    utils.stop_robot()
    if utils.is_angle_processed(st.theta):
        rospy.loginfo("[SEARCH_WAITING] Angle already processed. Preparing to rotate to next step.")
        st.target_theta = utils.normalize_angle(st.target_theta + cfg.ANGLE_STEP)
        st.mission_state = "SEARCH_ROTATING"
        return
        
    if st.pose_sub is None:
        rospy.loginfo("[SEARCH_WAITING] Subscribing to human poses to scan the area.")
        st.pose_sub = rospy.Subscriber("/openpose_ros/human_poses", HumanPoses, callbacks.pose_callback, queue_size=1)
    
    if st.stable_num_people >= 1 and st.target_chest_x != -1:
        rospy.loginfo("[SEARCH_WAITING] Target person stabilized. Transitioning to APPROACHING.")
        st.mission_state = "APPROACHING"
        return
        
    if st.search_start_time is None: 
        st.search_start_time = rospy.Time.now()
    
    if (rospy.Time.now() - st.search_start_time).to_sec() > cfg.SEARCH_WAIT_TIME:
        rospy.loginfo("[SEARCH_WAITING] Wait time exceeded without finding a person. Moving to next angle.")
        st.target_theta = utils.normalize_angle(st.target_theta + cfg.ANGLE_STEP)
        st.mission_state = "SEARCH_ROTATING"


def run_search_rotating():
    if st.pose_sub is not None:
        st.pose_sub.unregister()
        st.pose_sub = None 
        st.stable_num_people = 0
        st.cnt = 0
        st.lst = []
        st.target_chest_x = -1
        st.target_chest_y = -1
        
    angle_error = utils.normalize_angle(st.target_theta - st.theta)
    
    if abs(angle_error) > 0.05:
        rospy.loginfo_throttle(1, "[SEARCH_ROTATING] Rotating to target angle... Error: {:.2f}".format(angle_error))
        st.speed.angular.z = 0.8 if angle_error > 0 else -0.8
        st.speed.linear.x = 0.0
        st.cmd_pub.publish(st.speed)
    else:
        rospy.loginfo("[SEARCH_ROTATING] Target angle reached. Stopping and scanning.")
        utils.stop_robot()
        st.mission_state = "SEARCH_WAITING"
        st.search_start_time = rospy.Time.now()

def run_approaching():
    if st.target_chest_x != -1 and st.target_chest_y != -1:
        offset = st.target_chest_x - cfg.CENTER_X
        
        # --- 1. Alignment Logic ---
        if offset < -cfg.CENTER_TOLERANCE:
            st.speed.angular.z = 0.75
            st.speed.linear.x = 0.0 
        elif offset > cfg.CENTER_TOLERANCE:
            st.speed.angular.z = -0.75
            st.speed.linear.x = 0.0 
            
        # --- 2. In the Center ---
        else:
            st.speed.angular.z = 0.0 
            x, y = int(st.target_chest_x), int(st.target_chest_y)
            h, w = st.raw_depth_map.shape[:2]
            
            if 0 <= x < w and 0 <= y < h:
                roi = st.raw_depth_map[max(0, y-2):min(h, y+3), max(0, x-2):min(w, x+3)]
                if np.all(np.isnan(roi)):
                    st.speed.linear.x = 0.0
                else:
                    dist = np.nanmean(roi)
                    if dist > 20: dist /= 1000.0 
                    
                    if getattr(st, 'initial_person_dist', None) is None: 
                        st.initial_person_dist = dist
                        
                    # ==========================================
                    # CONDITION 1: Send to Gemini if < 2 meters
                   # ==========================================
                    # if dist < 2.0 and not getattr(st, 'photo_captured', False):
                    #     rospy.loginfo("[APPROACHING] Distance < 2m! Sending to Gemini...")
                    #     gemini_functions.trigger_gemini_analysis()
                    #     st.photo_captured = True # Mark as captured so it doesn't spam the API

                    # ==========================================
                    # CONDITION 2: Stop, Ask Name, Wait, Then Return
                    # ==========================================
                    if dist > (cfg.TARGET_DIST + cfg.DIST_TOLERANCE):
                        st.speed.linear.x = 0.5
                    else:
                        utils.stop_robot()
                        
                        # 1. We just arrived. Ask for the name ONCE.
                        if not getattr(st, 'waiting_for_name', False) and getattr(st, 'current_person_name', None) is None:
                            rospy.loginfo("[APPROACHING] Target distance reached. Asking for name...")
                            st.waiting_for_name = True
                            
                            # Trigger the robot's voice
                            if hasattr(st, 'status_pub'): st.status_pub.publish("false")
                            if hasattr(st, 'talk_pub'): st.talk_pub.publish("what is your name?")
                            if hasattr(st, 'status_pub'): st.status_pub.publish("true")
                                
                        # 2. We got the name! Trigger the background save and leave.
                        elif getattr(st, 'current_person_name', None) is not None:
                            rospy.loginfo("[APPROACHING] Name acquired! Transitioning to RETURNING.")
                            
                            # Trigger the background sync/save function
                            person_num = st.people_found_count + 1
                            # gemini_functions.start_background_sync(person_num, st.current_person_name)
                            
                            # Reset flags and leave
                            st.photo_captured = False
                            st.current_person_name = None 
                            st.waiting_for_name = False # Reset for the next person!
                            st.mission_state = "RETURNING"
                            
                        # 3. We are still waiting for the name. Do nothing but wait.
                        else:
                            rospy.loginfo_throttle(2, "[APPROACHING] Waiting for person to say their name on /names topic...")
    else:
        # Failsafe if person is lost
        st.speed.linear.x = 0.0
        st.speed.angular.z = 0.0
                        
    st.cmd_pub.publish(st.speed)


def run_returning():
    h, w = st.raw_depth_map.shape[:2]
    dist = 0.0
    
    if st.target_chest_x != -1 and st.target_chest_y != -1:
        x, y = int(st.target_chest_x), int(st.target_chest_y)
        if 0 <= x < w and 0 <= y < h:
            roi = st.raw_depth_map[max(0, y-2):min(h, y+3), max(0, x-2):min(w, x+3)]
            if not np.all(np.isnan(roi)):
                dist = np.nanmean(roi)
                if dist > 20: dist /= 1000.0
                
    if dist == 0.0:
        roi = st.raw_depth_map[h//2-5:h//2+5, w//2-5:w//2+5]
        if not np.all(np.isnan(roi)):
            dist = np.nanmean(roi)
            if dist > 20: dist /= 1000.0
            
    # Are we still reversing?
    if dist == 0.0 or dist < (st.initial_person_dist - cfg.RETURN_TOLERANCE): 
        rospy.loginfo_throttle(1, "[RETURNING] Reversing. Current Dist: {:.2f}m".format(dist))
        st.speed.linear.x = -0.5
        st.speed.angular.z = 0.0
    else:
        # We have successfully reversed to our original spot
        utils.stop_robot()
        rospy.loginfo("[RETURNING] Reached original distance. Logging person and resuming search.")
        
        # Instantly move on to the next angle without waiting for the AI!
        st.people_found_count += 1
        st.person_found_angles.append(st.theta)
        st.initial_person_dist = None
        st.target_theta = utils.normalize_angle(st.target_theta + cfg.ANGLE_STEP)
        st.mission_state = "SEARCH_ROTATING"
            
    st.cmd_pub.publish(st.speed)