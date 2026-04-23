import sys
import json
import google.generativeai as genai
import cv2
from PIL import Image

api_keys = [
    "AIzaSyAKJ21t6v2QOu7z1ZtC5QTObWwfKToVdRM",
    "AIzaSyDeZ6JWfHb7V7y6eS3m1-ASKRB0C6lrAk8",
    "AIzaSyDtJoQeoJ7KDGHTXVB4IaiXGRYbkTysqh8",
    "AIzaSyCS87aDz9Bu-GF62peepmnsUihU2PSVg60",
    "AIzaSyCcFT_GpvjcNcKFDSmIh2gi6PYSso_9wW4",
    "AIzaSyCQQ9-jagu-XisGhr9r4cVMYmkPWjrlQ98",
    "AIzaSyDpMbs0n32Z4Om1JtO_lqrh_3KPrJQzDRM",
    "AIzaSyCqrii7c3uM5UX2pd-nClyf_nlfIVfLtG8",
    "AIzaSyA9HzQDE0ONLruygygYCx7-L9MPpeRwpik",
    "AIzaSyCBspmcLUoeN50HIvlscTdoVah1k1kg67g",
    "AIzaSyCDV7y9l1i-amDXHiu2eGZmcbE6WKpwlEg",
    "AIzaSyBTYHAE6UA5NcVmXCf-rA_SFMmoCnDyNvE"
]
def get_safe_coord(data, key):
    """Safely extracts a coordinate from the JSON, handling strings, nulls, or missing keys."""
    try:
        return float(data.get(key, 0))
    except (ValueError, TypeError):
        return 0.0
def analyze_and_draw(input_path, used_features_str, output_path):
    try:
        # Load image once before the loop
        img_pil = Image.open(input_path)
        
        # 1. UPDATED PROMPT: Ask for the person's bounding box and update the JSON structure
        prompt = f"""
        Analyze the person and surroundings. 
        1. Pick TWO features from [gender, glasses, cap, hair, tshirt, pants, beard] NOT in [{used_features_str}].
        2. Identify ONE prominent object and its position (left, right, in front of, behind).
        3. Provide normalized bounding box (0-1000) [ymin, xmin, ymax, xmax] of the OBJECT.
        4. Provide normalized bounding box (0-1000) [ymin, xmin, ymax, xmax] of the PERSON.
        Return ONLY JSON:
        {{"feature_1_name": "", "feature_1_value": "", "feature_2_name": "", "feature_2_value": "", "nearby_object": "", "relative_position": "", "obj_ymin": 0, "obj_xmin": 0, "obj_ymax": 0, "obj_xmax": 0, "person_ymin": 0, "person_xmin": 0, "person_ymax": 0, "person_xmax": 0}}
        """

        success = False
        last_error = None
        data = None

        # --- LOOP THROUGH API KEYS ---
        for i, key in enumerate(api_keys):
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                response = model.generate_content([prompt, img_pil])
                
                # Parse the JSON cleanly
                data = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                
                success = True
                break 
                
            except Exception as e:
                last_error = str(e)
                print(f"Key {i+1} failed: {last_error}", file=sys.stderr)
                continue 

        if not success:
            raise Exception(f"All API keys failed. Last error: {last_error}")

        # --- SAFE DRAWING LOGIC ---
        img_cv = cv2.imread(input_path)
        if img_cv is None:
            raise Exception(f"OpenCV failed to read the input image: {input_path}")
            
        h, w, _ = img_cv.shape
        
        # 1. Safely calculate Object Bounding Box (Green)
        o_ymin = int((get_safe_coord(data, "obj_ymin") / 1000.0) * h)
        o_xmin = int((get_safe_coord(data, "obj_xmin") / 1000.0) * w)
        o_ymax = int((get_safe_coord(data, "obj_ymax") / 1000.0) * h)
        o_xmax = int((get_safe_coord(data, "obj_xmax") / 1000.0) * w)
        
        cv2.rectangle(img_cv, (o_xmin, o_ymin), (o_xmax, o_ymax), (0, 255, 0), 3)
        cv2.putText(img_cv, data.get("nearby_object", "Object"), (o_xmin, max(o_ymin-10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # 2. Safely calculate Person Bounding Box (Blue)
        p_ymin = int((get_safe_coord(data, "person_ymin") / 1000.0) * h)
        p_xmin = int((get_safe_coord(data, "person_xmin") / 1000.0) * w)
        p_ymax = int((get_safe_coord(data, "person_ymax") / 1000.0) * h)
        p_xmax = int((get_safe_coord(data, "person_xmax") / 1000.0) * w)
        
        cv2.rectangle(img_cv, (p_xmin, p_ymin), (p_xmax, p_ymax), (255, 0, 0), 3)
        cv2.putText(img_cv, "Person", (p_xmin, max(p_ymin-10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        # 3. Save the image and verify it worked
        write_success = cv2.imwrite(output_path, img_cv)
        if not write_success:
            raise Exception(f"OpenCV failed to write the image to: {output_path}. Check file permissions.")
        
        # 4. Print the successful JSON for ROS
        print(json.dumps(data))
        
    except Exception as e:
        # If a massive failure happens, report it as JSON so ROS doesn't freeze
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    analyze_and_draw(sys.argv[1], sys.argv[2], sys.argv[3])