import cv2
from flask import Flask, Response, request, send_from_directory
import os
import uuid

app = Flask(__name__)

# Initialize the webcam
camera = cv2.VideoCapture(0)

@app.route("/")
def home():
    return "Hello, welcome to nutriVision, <a href='http://localhost:5001/video_feed'>http://localhost:5001/video_feed</a>"

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['GET'])
def capture_image():
    success, frame = camera.read()
    if not success:
        return "Failed to capture image", 500
    else:
        # Generate a unique filename
        image_name = f"captured_{uuid.uuid4()}.jpg"
        image_path = os.path.join("captured_images", image_name)
        
        # Ensure the directory exists
        os.makedirs("captured_images", exist_ok=True)
        
        # Save the image
        cv2.imwrite(image_path, frame)
        return {"message": "Image captured successfully", "image_path": image_path}, 200

# Serve static files from the captured_images directory
@app.route('/captured_images/<filename>')
def serve_image(filename):
    return send_from_directory('captured_images', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)