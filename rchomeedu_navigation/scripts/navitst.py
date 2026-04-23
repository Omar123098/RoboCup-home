#!/usr/bin/env python

"""
    RoboCup@Home Education | oc@robocupathomeedu.org
    navi.py - enable turtlebot to navigate to predefined waypoint location
"""
from glob import glob
from turtle import st
import os
import rospy
from std_msgs.msg import String
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped, Point, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler

original = 0
start = 0

class NavToPoint:
    def __init__(self):
        rospy.on_shutdown(self.cleanup)
        
        # Subscribe to the move_base action server
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.pub = rospy.Publisher('location', String, queue_size = 1)
        rospy.loginfo("Waiting for move_base action server...")
        # Wait for the action server to become available
        self.move_base.wait_for_server(rospy.Duration(120))
        rospy.loginfo("Connected to move base server")

        # A variable to hold the initial pose of the robot to be set by the user in RViz
        initial_pose = PoseWithCovarianceStamped()
        rospy.Subscriber('initialpose', PoseWithCovarianceStamped, self.update_initial_pose)
        rospy.Subscriber('/start',String,self.s)
        rospy.Subscriber('/home',String,self.home)
        self.talk_pub = rospy.Publisher('/speech', String, queue_size = 1) # <--- ADDED
        self.talk_states = rospy.Publisher('/status',String,queue_size=1)
        # Get the initial pose from the user
        rospy.loginfo("*** Click the 2D Pose Estimate button in RViz to set the robot's initial pose...")
        rospy.wait_for_message('initialpose', PoseWithCovarianceStamped)
        
        # Make sure we have the initial pose
        while initial_pose.header.stamp == "":
            rospy.sleep(1) 
            
        rospy.loginfo("Ready to go")
        rospy.sleep(1)

        locations = dict()

        # Location A
        A_x = -2.34
        A_y = 4.15
        A_theta = -0.001

        quaternion = quaternion_from_euler(0.0, 0.0, A_theta)
        locations['A'] = Pose(Point(A_x, A_y, 0.000), Quaternion(quaternion[0], quaternion[1], quaternion[2], quaternion[3]))

        self.goal = MoveBaseGoal()
        rospy.loginfo("Starting navigation test")

        while not rospy.is_shutdown():
            self.goal.target_pose.header.frame_id = 'map'
            self.goal.target_pose.header.stamp = rospy.Time.now()
            if start==0:
                rospy.loginfo("waiting to start")
            # Robot will go to point A
            if start == 1:
                rospy.loginfo("Going to point A")
                rospy.sleep(2)
                self.goal.target_pose.pose = locations['A']
                self.move_base.send_goal(self.goal)
                waiting = self.move_base.wait_for_result(rospy.Duration(secs=300))
                
                if waiting == 1:
                    rospy.loginfo("Reached point A")
                    rospy.sleep(2)
                    self.pub.publish("Room")
                    global start
                    start = 0
            # ... inside your class/loop ...

            # if start == 1:
            #     rospy.loginfo("Attempting to go to point A...")
            #     self.goal.target_pose.pose = locations['A']
            #     self.move_base.send_goal(self.goal)
                
            #     # Wait up to 300 seconds for a result (True if finished early, False if timed out)
            #     finished_in_time = self.move_base.wait_for_result(rospy.Duration(secs=300))
                
            #     if finished_in_time:
            #         # Check the actual success/failure state of the goal
            #         state = self.move_base.get_state()
                    
            #         if state == GoalStatus.SUCCEEDED:
            #             rospy.loginfo("Reached point A successfully!")
            #             rospy.sleep(2)
            #             # CRITICAL: Only publish "Room" if the robot ACTUALLY got there!
            #             self.pub.publish("Room") 
            #             global start
            #             start = 0  # Success! Move on to the next state.
                    
            #         else:
            #             # If it aborted (state 4), it will warn you and retry
            #             rospy.logwarn("Failed to reach point A (State: {}). Retrying from current position...".format(state))
            #             rospy.sleep(3) 
            #             # Notice we DO NOT change the 'start' variable here. It will retry next loop.
                        
            #     else:
            #         rospy.logerr("Going to point A timed out! Canceling goal and retrying...")
            #         self.move_base.cancel_goal()
            #         rospy.sleep(3)
            #         # Again, 'start' remains 1, so it will retry automatically.
            if start==2:  
                rospy.loginfo("waiting to finish room")
            
            # elif start == 3:
            #     rospy.loginfo("Attempting to go back home...")
            #     self.goal.target_pose.pose = self.origin
            #     self.move_base.send_goal(self.goal)
                
            #     # Wait up to 300 seconds for a result
            #     finished_in_time = self.move_base.wait_for_result(rospy.Duration(secs=300))
                
            #     if finished_in_time:
            #         state = self.move_base.get_state()
                    
            #         if state == GoalStatus.SUCCEEDED:
            #             rospy.loginfo("Reached home successfully!")
            #             rospy.sleep(2)
            #             global start
            #             start = 4  # Success! Move on to the next state.
                    
            #         else:
            #             rospy.logwarn("Failed to reach home (State: {}). Retrying from current position...".format(state))
            #             rospy.sleep(3) 
            #             # Notice we DO NOT change the 'start' variable here.
            #             # On the next tick of your main loop, it will run 'elif start == 3' again!
                        
            #     else:
            #         rospy.logerr("Going home timed out! Canceling goal and retrying...")
            #         self.move_base.cancel_goal()
            #         rospy.sleep(3)
                    # Again, 'start' remains 3, so it will retry automatically.
            # After reached point A, robot will go back to initial position
            elif start == 3:
                rospy.loginfo("Going back home")
                rospy.sleep(2)
                self.goal.target_pose.pose = self.origin
                self.move_base.send_goal(self.goal)
                waiting = self.move_base.wait_for_result(rospy.Duration(secs=300))
                if waiting == 1:
                    rospy.loginfo("Reached home")
                    rospy.sleep(2)
                    global start
                    start = 4
            # ==========================================
            # NEW STATE: READ THE FEATURES ALOUD
            # ==========================================
            elif start == 4:
                rospy.loginfo("Mission complete. Reading the saved features...")
                
                # Use glob to find all features.txt files 
                search_path = "/home/mustar/person */features.txt"
                feature_files = sorted(glob(search_path))
                
                if not feature_files:
                    rospy.logwarn("No feature files found in /home/mustar/!")
                    self.talk_pub.publish("I could not find any saved features.")
                else:
                    # Loop through every file found
                    for file_path in feature_files:
                        try:
                            with open(file_path, "r") as f:
                                sentence = f.read().strip()
                                
                                # Print it to the terminal
                                rospy.loginfo("Reading: {}".format(sentence))
                                
                                # Speak it out loud
                                self.talk_states.publish('true')
                                rospy.sleep(1)
                                self.talk_pub.publish(sentence)
                                
                                # Wait a few seconds so the robot finishes speaking before reading the next one
                                rospy.sleep(10) 
                                
                        except Exception as e:
                            rospy.logerr("Error reading {}: {}".format(file_path, e))
                
                rospy.loginfo("Finished reporting all features.")
                
                # Set start to 5 so it stops looping and waits idly
                global start
                start = 5
                
            rospy.sleep(0.1) # <--- ADDED: Tiny sleep to prevent the while loop from maxing out the CPU
            # rospy.Rate(5).sleep()
    def s(self,msg):
        global start
        start=1
    def home (self,msg):
        global start
        start =3
    def update_initial_pose(self, initial_pose):
        self.initial_pose = initial_pose
        if original == 0:
            self.origin = self.initial_pose.pose.pose
            global original
            original = 1

    def cleanup(self):
        rospy.loginfo("Shutting down navigation....")
        self.move_base.cancel_goal()

if __name__=="__main__":
    rospy.init_node('navi_point')
    try:
        NavToPoint()
        rospy.spin()
    except:
        pass
