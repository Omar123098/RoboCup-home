import rospy
import cv2
import os
import subprocess
import json
import threading
from cv_bridge import CvBridgeError

import shared_state as st

# Setup paths as standard global variables
conda_python_path = "/home/mustar/miniconda3/envs/gemini_ros/bin/python"
script_path = "/home/mustar/catkin_ws/src/rc-home-edu-learn-ros/rchomeedu_vision/scripts/gemini_analyzer.py"
current_dir = "/home/mustar"
raw_image_path = os.path.join(current_dir, "person_frame_raw.jpg")
final_image_path = os.path.join(current_dir, "person_frame_annotated.jpg")

# ==========================================
# RGB IMAGE CALLBACK
# ==========================================
def rgb_image_callback(data):
    try:
        if hasattr(st, 'bridge'):
            st.current_cv_image = st.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
        rospy.logerr(e)

# ==========================================
# BACKGROUND API CALL
# ==========================================
def call_gemini_api_async():
    """Runs the external python script in a separate thread."""
    used_features = getattr(st, 'used_features', [])
    used_features_str = ",".join(used_features) if used_features else "none"
    
    try:
        result = subprocess.check_output(
            [conda_python_path, script_path, raw_image_path, used_features_str, final_image_path],
            stderr=subprocess.STDOUT
        )
        st.gemini_output = result.decode('utf-8').strip()
        
        rospy.loginfo("[BACKGROUND AI] --- GEMINI OUTPUT RECEIVED ---")
        rospy.loginfo(st.gemini_output)
        rospy.loginfo("----------------------------------------------")
        
        # --- THE FIX: Extract only the valid JSON line ---
        try:
            lines = st.gemini_output.split('\n')
            clean_json_str = None
            
            # Read from the bottom up to find the actual JSON response
            for line in reversed(lines):
                if 'feature_1_name' in line and '{' in line:
                    start_idx = line.find('{')
                    end_idx = line.rfind('}') + 1
                    clean_json_str = line[start_idx:end_idx]
                    break
            
            if clean_json_str:
                data = json.loads(clean_json_str)
                
                st.latest_gemini_data = data # Save the data for the sync thread
                
                if "feature_1_name" in data:
                    if not hasattr(st, 'used_features'): st.used_features = []
                    st.used_features.append(data["feature_1_name"])
                    st.used_features.append(data["feature_2_name"])
            else:
                rospy.logwarn("[BACKGROUND AI] No valid JSON containing features found in output.")
                
        except Exception as e:
            rospy.logwarn("[BACKGROUND AI] Could not parse JSON features: {}".format(e))
            
    except subprocess.CalledProcessError as e:
        rospy.logerr("Gemini API call failed: {}".format(e.output))
        st.gemini_output = '{"error": "API Call Failed"}'
    finally:
        st.gemini_processing = False

# ==========================================
# TRIGGER FUNCTION
# ==========================================
def trigger_gemini_analysis():
    if getattr(st, 'current_cv_image', None) is None:
        rospy.logwarn("No camera image available yet. Retrying next frame...")
        return False
        
    person_num = getattr(st, 'people_found_count', 0) + 1
    cv2.imwrite(raw_image_path, st.current_cv_image)
    rospy.loginfo("Captured image for Person {}. Sending to AI in the background...".format(person_num))
    
    # Initialize state variables for thread tracking
    st.gemini_processing = True
    st.gemini_output = None
    # ---> THE FIX: Clear the previous person's data so it doesn't leak <---
    st.latest_gemini_data = {}
    # Fire and forget the API call in a new thread
    thread = threading.Thread(target=call_gemini_api_async)
    thread.start()
    
    return True

# ==========================================
# BACKGROUND DIRECTORY & SYNC MANAGER
# ==========================================
def sync_and_save_async(person_num, person_name):
    """Waits for Gemini to finish, then organizes everything into a folder."""
    rospy.loginfo("[BACKGROUND SYNC] Waiting for Gemini API to finish processing...")
    
    # 1. Wait until Gemini is no longer processing (does not freeze the robot)
    while getattr(st, 'gemini_processing', False):
        rospy.sleep(0.5)
        
    data = getattr(st, 'latest_gemini_data', {})
    if not data:
        rospy.logwarn("[BACKGROUND SYNC] No Gemini data found to sync.")
        return

    # 2. Create the "person X" folder
    folder_name = "person {}".format(person_num)
    folder_path = os.path.join(current_dir, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 3. Move Annotated Image into the folder
    new_image_path = os.path.join(folder_path, "annotated_image.jpg")
    if os.path.exists(final_image_path):
        import shutil
        shutil.move(final_image_path, new_image_path)

    # 4. Extract features for formatting
    f1_name = data.get("feature_1_name", "unknown feature")
    f1_val = data.get("feature_1_value", "unknown")
    f2_name = data.get("feature_2_name", "unknown feature")
    f2_val = data.get("feature_2_value", "unknown")
    obj = data.get("nearby_object", "an object")
    pos = data.get("relative_position", "an unknown position")

    # Helper to create "1st", "2nd", "3rd", "4th"
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(person_num if person_num < 20 else person_num % 10, 'th')
    nth_person = "{}{}".format(person_num, suffix)

    # 5. Format the beautiful text sentence
    sentence = "The {} person is named {}, has {}: {} and {}: {}, and there is {} and it is located {}.".format(
        nth_person, person_name, f1_name, f1_val, f2_name, f2_val, obj, pos
    )

    # 6. Save the text file
    txt_file_path = os.path.join(folder_path, "features.txt")
    with open(txt_file_path, "w") as f:
        f.write(sentence)
        
    rospy.loginfo("[BACKGROUND SYNC] Success! Saved data for {} to folder '{}'".format(person_name, folder_name))

def start_background_sync(person_num, name):
    """Triggers the background sync process."""
    thread = threading.Thread(target=sync_and_save_async, args=(person_num, name))
    thread.start()