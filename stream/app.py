import cv2
from flask import Flask, Response, request, send_from_directory, render_template
import os
import uuid
import base64
from openai import OpenAI
import json
from dotenv import load_dotenv
import threading
from threading import Lock
from database import init_db, add_scan_record, get_scan_records, search_records

# Load environment variables
load_dotenv()
print("[DEBUG] Environment variables loaded")

# Initialize Flask app
app = Flask(__name__)
print("[DEBUG] Flask app initialized")

# Initialize database
init_db()
print("[DEBUG] Database initialized")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("[DEBUG] OpenAI client initialized")

# Global variables for video streaming
class VideoCamera:
    def __init__(self):
        print("[DEBUG] Initializing VideoCamera")
        self.camera = cv2.VideoCapture(0)
        self.lock = Lock()
        self.frame = None
        self.stopped = False
        
        # Start frame capture thread
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.daemon = True
        self.thread.start()
        print("[DEBUG] Frame capture thread started")
    
    def _capture_loop(self):
        print("[DEBUG] Starting capture loop")
        while not self.stopped:
            success, frame = self.camera.read()
            if success:
                with self.lock:
                    self.frame = frame
    
    def get_frame(self):
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
            return None
    
    def stop(self):
        print("[DEBUG] Stopping VideoCamera")
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join()
        self.camera.release()

video_camera = None

def get_camera():
    print("[DEBUG] Getting camera instance")
    global video_camera
    if video_camera is None:
        video_camera = VideoCamera()
    return video_camera

@app.route("/")
def home():
    print("[DEBUG] Rendering home page")
    return render_template('index.html')

def generate_frames():
    print("[DEBUG] Starting frame generation")
    camera = get_camera()
    while True:
        frame = camera.get_frame()
        if frame is None:
            print("[DEBUG] No frame received")
            continue
        
        # Encode frame
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_bytes = buffer.tobytes()
        # print("[DEBUG] Frame encoded")
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    print("[DEBUG] Starting video feed")
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def encode_image_to_base64(image_path):
    print(f"[DEBUG] Encoding image to base64: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/capture', methods=['GET'])
def capture_image():
    print("[DEBUG] Capturing image")
    camera = get_camera()
    frame = camera.get_frame()
    
    if frame is None:
        print("[DEBUG] Failed to capture frame")
        return {"error": "Failed to capture image"}, 500
    
    # Generate a unique filename
    image_name = f"captured_{uuid.uuid4()}.jpg"
    image_path = os.path.join("captured_images", image_name)
    print(f"[DEBUG] Generated image path: {image_path}")
    
    # Ensure the directory exists
    os.makedirs("captured_images", exist_ok=True)
    
    # Save the image temporarily
    cv2.imwrite(image_path, frame)
    print("[DEBUG] Image saved temporarily")
    
    # Convert image to base64
    base64_image = encode_image_to_base64(image_path)
    print("[DEBUG] Image encoded to base64")
    
    try:
        print("[DEBUG] Calling GPT-4-Vision API")
        # Call GPT-4-Vision API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a nutritionist and software engineer. If you don't see any food in the image, respond with {"name": "unknown"}. Otherwise, respond with nutrition output:
                    {
                        "name": "string",
                        "nutrition": {
                            "total_cal": number,
                            "potassium": number,
                            "protein": number,
                            "total_carbs": number,
                            "total_fat": number
                        }
                    }"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this food image and provide nutrition information in the specified JSON format."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        print("[DEBUG] Received API response")
        print(f"[DEBUG] Raw response content: {response.choices[0].message.content}")
        
        try:
            # Clean the response content by removing markdown code blocks if present
            content = response.choices[0].message.content
            if content.startswith('```') and content.endswith('```'):
                content = content.strip('`').strip()
                if content.startswith('json\n'):  # Remove "json" language identifier if present
                    content = content[4:].strip()
            
            nutrition_data = json.loads(content)
            print(f"[DEBUG] Parsed nutrition data: {nutrition_data}")
            
            # Check if food was detected
            if nutrition_data.get('name', '').lower() == 'unknown':
                # Remove the temporary image
                if os.path.exists(image_path):
                    os.remove(image_path)
                print("[DEBUG] No food detected in the image")
                return {"error": "No food detected in the image"}, 400
            
            # Only save to database and keep image if food was detected
            add_scan_record(
                food_name=nutrition_data['name'],
                nutrition_data=nutrition_data['nutrition'],
                image_path=image_path
            )
            print("[DEBUG] Scan record added to database")
            
            return nutrition_data, 200
            
        except json.JSONDecodeError:
            print("[DEBUG] Failed to parse JSON response")
            return {"error": "Failed to analyze the image"}, 400
            
    except Exception as e:
        print(f"[DEBUG] Error occurred: {str(e)}")
        return {"error": str(e)}, 500

# Serve static files from the captured_images directory
@app.route('/captured_images/<filename>')
def serve_image(filename):
    print(f"[DEBUG] Serving image: {filename}")
    return send_from_directory('captured_images', filename)

# Cleanup when the server shuts down
@app.teardown_appcontext
def cleanup(error):
    if error is not None:  # Only cleanup on actual errors or shutdown
        print("[DEBUG] Cleaning up resources")
        global video_camera
        if video_camera:
            video_camera.stop()
            video_camera = None

@app.route("/logs")
def logs():
    print("[DEBUG] Accessing logs page")
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    print(f"[DEBUG] Getting records for page {page}")
    # Get records with pagination
    records, total_pages, total_records = get_scan_records(page, per_page)
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages if total_pages > 0 else 1))
    print(f"[DEBUG] Total pages: {total_pages}, Total records: {total_records}")
    
    return render_template("logs.html", 
                         records=records,
                         page=page,
                         total_pages=total_pages,
                         total_records=total_records,
                         page_range=range(max(1, page-2), min(total_pages+1, page+3) if total_pages > 0 else 1))

@app.route("/search")
def search():
    print("[DEBUG] Performing search")
    search_term = request.args.get('term', '')
    date_filter = request.args.get('date', None)
    print(f"[DEBUG] Search term: {search_term}, Date filter: {date_filter}")
    
    records = search_records(search_term, date_filter)
    print(f"[DEBUG] Found {len(records)} records")
    return render_template("logs.html", records=records, is_search=True)

if __name__ == '__main__':
    print("[DEBUG] Starting Flask application")
    app.run(host='0.0.0.0', port=5001, debug=True)