#!/usr/bin/python2
print(">>> Python 2 ROS Environment Initialized...")
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import subprocess
import os
import json

class ImageFeatureExtractor:
    def __init__(self):
        print(">>> Initializing ROS Node...")
        rospy.init_node('gemini_feature_extractor', anonymous=True)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/camera_top/rgb/image_raw", Image, self.image_callback)
        self.conda_python_path = "/home/mustar/miniconda3/envs/gemini_ros/bin/python"
        self.script_path = "/home/mustar/catkin_ws/src/rc-home-edu-learn-ros/rchomeedu_vision/scripts/gemini_analyzer.py"
       
        current_dir = os.getcwd()
        self.raw_image_path = os.path.join(current_dir, "person_frame_raw.jpg")
        self.final_image_path = os.path.join(current_dir, "person_frame_annotated.jpg")
        self.processing = False
        self.people_data = []
        self.used_features = []
        print(">>> Node ready. Images will save to: " + current_dir)
    
    def image_callback(self, data):
        if self.processing or len(self.people_data) >= 3:
            return
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(e)
            return

        person_num = len(self.people_data) + 1
        msg = "Person {} - Press 'n' to scan".format(person_num)
        display_img = cv_image.copy()
        cv2.putText(display_img, msg, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Jupiter Camera View", display_img)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('n') and person_num <= 3:
            self.processing = True
            cv2.imwrite(self.raw_image_path, cv_image)
            rospy.loginfo("Image saved to current folder. Analyzing Person {}...".format(person_num))
            self.call_gemini_api()

    def call_gemini_api(self):
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            del env['PYTHONPATH']
        used_features_str = ",".join(self.used_features)
        if not used_features_str:
            used_features_str = "NONE"
        try:
            process = subprocess.Popen(
                [self.conda_python_path, self.script_path, self.raw_image_path, used_features_str, self.final_image_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                try:
                    person_features = json.loads(stdout.strip())
                    if "error" in person_features:
                        rospy.logerr("API Error: " + person_features["error"])
                    else:
                        f1_name = person_features.get("feature_1_name", "")
                        f2_name = person_features.get("feature_2_name", "")
                        if f1_name: self.used_features.append(f1_name)
                        if f2_name: self.used_features.append(f2_name)
                        self.people_data.append(person_features)
                        person_num = len(self.people_data)
                        print("\n--- LIVE GEMINI RESPONSE FOR PERSON {} ---".format(person_num))
                        print("Feature 1: {} - {}".format(f1_name.capitalize(), person_features.get("feature_1_value")))
                        print("Feature 2: {} - {}".format(f2_name.capitalize(), person_features.get("feature_2_value")))
                        print("Nearby Object: {}".format(person_features.get("nearby_object")))
                        print("Position: {}".format(person_features.get("relative_position")))
                        print("-----------------------------------------")
                        final_img = cv2.imread(self.final_image_path)
                        if final_img is not None:
                            window_name = "Detection Result - Person {}".format(person_num)
                            cv2.imshow(window_name, final_img)
                            cv2.waitKey(2500)
                            cv2.destroyWindow(window_name)
                        if len(self.people_data) == 3:
                            rospy.loginfo("Task complete. Images are saved in your folder.")
                            rospy.signal_shutdown("Finished processing 3 persons.")
                        else:
                            rospy.loginfo("Waiting for next person...")
                except ValueError:
                    rospy.logerr("Invalid JSON received. Output: \n" + stdout)
            else:
                rospy.logerr("Error calling Gemini API:\n" + stderr)
        except Exception as e:
            rospy.logerr("Subprocess failed: " + str(e))
        finally:
            self.processing = False
if __name__ == '__main__':
    try:
        extractor = ImageFeatureExtractor()
        rospy.spin()
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()