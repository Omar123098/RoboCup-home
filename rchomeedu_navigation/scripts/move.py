#!/usr/bin/env python2
from cmath import sqrt
from re import S
from turtle import st
import rospy
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Point, Twist
from math import atan2

x = 0.0
y = 0.0 
theta = 0.0

def rotate_180():
    b=1
    print(theta)   
    rospy.sleep(1)
    t=theta+3.14
    if t>3.14159:
        t-=6.28318
    while abs(t-theta)>0.05 and b and  not rospy.is_shutdown():
        print("rotating 180")
        speed.angular.z=0.35
        pub.publish(speed)
        rospy.sleep(0.1)
    print("done rotating 180")
    speed.angular.z=0
    pub.publish(speed)
    b=0

def rotate_left_90():
    b=1
    print(theta)   
    rospy.sleep(1)
    t=theta+1.57
    if t>3.14159:
        t-=6.28318
    while abs(t-theta)>0.05 and b and  not rospy.is_shutdown():
        print("rotating left")
        speed.angular.z=0.35
        pub.publish(speed)
        rospy.sleep(0.1)
    print("done rotating left")
    speed.angular.z=0
    pub.publish(speed)
    b=0

def rotate_right_90():
    b=1
    print(theta)   
    rospy.sleep(1)
    t=theta-1.57
    if t<-3.14159:
        t+=6.28318
    while abs(theta-t)>0.05 and b and  not rospy.is_shutdown():
        print("rotating right")
        speed.angular.z=-0.35
        pub.publish(speed)
        rospy.sleep(0.1)
    print("done rotating right")
    speed.angular.z=0
    pub.publish(speed)
    b=0   

def stop():
    speed.linear.x=0
    speed.angular.z=0
    pub.publish(speed)

def newOdom(msg):
    global x
    global y
    global theta

    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y

    rot_q = msg.pose.pose.orientation
    
    (roll, pitch, theta) = euler_from_quaternion([rot_q.x, rot_q.y, rot_q.z, rot_q.w])
    # print (x,y,theta)
rospy.init_node("speed_controller")

sub = rospy.Subscriber("/odom", Odometry, newOdom)
pub = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size = 1)

speed = Twist()
goal1 = Point()
goal2 = Point()

while not rospy.is_shutdown():
    # print(y)
    # rospy.sleep(1)
    # goal2.y=y-2
    # print(goal2.y,y)
    # rospy.sleep(1)
    # dist=float(sqrt((goal2.y-y)*(goal2.y-y))) 
    # while dist > 0.1 and not rospy.is_shutdown():
    #     dist=float(sqrt((goal2.y-y)*(goal2.y-y))) 
    #     print(y,goal2.y,abs(abs(y)-abs(goal2.y)))
    #     speed.linear.x=0.2
    #     pub.publish(speed)
    # stop()
    # rospy.sleep(2000)    

