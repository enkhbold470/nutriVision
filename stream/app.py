import cv2
from flask import Flask, Response, request, send_from_directory, render_template, redirect, url_for, flash, jsonify
import os
import uuid
import base64
from flask_login import current_user, LoginManager, login_required, login_user, logout_user
from openai import OpenAI
import json
from dotenv import load_dotenv
import threading
from threading import Lock
from datetime import datetime, timedelta
from database import init_db, add_scan_record, get_scan_records, search_records, get_db_connection, get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from utils import calculate_bmr, calculate_daily_calories, calculate_daily_protein

# Load environment variables
load_dotenv()
print("[DEBUG] Environment variables loaded")

# Initialize Flask app
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
print("[DEBUG] Flask app initialized")

# Register database close function
app.teardown_appcontext(close_db)

# Add min function to Jinja2 environment
app.jinja_env.globals.update(min=min)
print("[DEBUG] Added min function to Jinja2 environment")

# Add helper functions to Jinja2 environment
def get_user_achievements(user_id):
    """Get user achievements with unlock status."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get user's scan count and other stats
    cur.execute('''
        SELECT COUNT(*) as scan_count,
               COUNT(DISTINCT DATE(timestamp)) as active_days,
               COUNT(DISTINCT food_name) as unique_foods
        FROM scanned_items 
        WHERE user_id = %s
    ''', (user_id,))
    stats = cur.fetchone()
    conn.close()
    
    # Define achievements
    achievements = [
        {
            'title': 'First Scan',
            'description': 'Scan your first food item',
            'icon': 'bi-camera',
            'unlocked': stats['scan_count'] > 0
        },
        {
            'title': 'Health Explorer',
            'description': 'Scan 10 different food items',
            'icon': 'bi-search',
            'unlocked': stats['unique_foods'] >= 10
        },
        {
            'title': 'Consistency King',
            'description': 'Track food for 7 consecutive days',
            'icon': 'bi-calendar-check',
            'unlocked': stats['active_days'] >= 7
        },
        {
            'title': 'Nutrition Master',    
            'description': 'Complete 100 food scans',
            'icon': 'bi-trophy',
            'unlocked': stats['scan_count'] >= 100
        }
    ]
    return achievements

def get_activity_data(user_id):
    """Get user's activity data for the last year."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get daily scan counts for the last year
    cur.execute('''
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM scanned_items 
        WHERE user_id = %s 
        AND timestamp >= CURRENT_DATE - INTERVAL '1 year'
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (user_id,))
    
    activity = cur.fetchall()
    conn.close()
    
    # Convert to week-based format
    weeks = []
    current_week = []
    
    # Fill in missing dates with zero counts
    date_counts = {row['date']: row['count'] for row in activity}
    
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        current_week.append({
            'date': date_str,
            'count': date_counts.get(date_str, 0)
        })
        
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
        
        current_date += timedelta(days=1)
    
    if current_week:
        weeks.append(current_week)
    
    return weeks

def get_activity_color(count):
    """Get color for activity based on count."""
    if count == 0:
        return '#ebedf0'
    elif count <= 2:
        return '#9be9a8'
    elif count <= 4:
        return '#40c463'
    elif count <= 6:
        return '#30a14e'
    else:
        return '#216e39'

# Add functions to Jinja environment
app.jinja_env.globals.update(
    get_user_achievements=get_user_achievements,
    get_activity_data=get_activity_data,
    get_activity_color=get_activity_color
)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize database
init_db()
print("[DEBUG] Database initialized")

# Initialize OpenAI clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
perplexity_client = OpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)
print("[DEBUG] API clients initialized")

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
@login_required
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
                user_id=current_user.id,
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
@login_required
def logs():
    print("[DEBUG] Accessing logs page")
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    print(f"[DEBUG] Getting records for page {page}")
    # Get records with pagination for the current user only
    records, total_pages, total_records = get_scan_records(page, per_page, current_user.id)
    
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

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        age = request.form.get('age', type=int)
        weight = request.form.get('weight', type=float)
        target_weight = request.form.get('target_weight', type=float)
        gender = request.form.get('gender')
        height = request.form.get('height', type=int)
        goal = request.form.get('goal', type=int)
        target_date = request.form.get('target_date')
        
        if not all([username, password, age, weight, target_weight, gender, height, goal, target_date]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        user_id = create_user(username, password, age, weight, target_weight, gender, height, goal, target_date)
        if user_id:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists', 'danger')
    
    return render_template('register.html')

def create_user(username, password, age, weight, target_weight, gender, height, goal, target_date):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if username exists
        cur.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cur.fetchone():
            return None
            
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Calculate BMR and daily targets
        bmr = calculate_bmr(weight, height, age, gender)
        max_daily_calories = calculate_daily_calories(bmr, goal)
        max_daily_protein = calculate_daily_protein(weight, goal)
        
        # Insert new user with all required fields
        cur.execute('''
            INSERT INTO users (
                username, password, age, weight, target_weight, gender, height, goal, target_date,
                calories, potassium, protein, carbs, total_fat,
                max_daily_calories, max_daily_protein
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            username, hashed_password, age, weight, target_weight, gender, height, goal, target_date,
            0, 0, 0, 0, 0,  # Initial daily totals
            max_daily_calories, max_daily_protein  # Calculated targets
        ))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    finally:
        conn.close()


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_data = cur.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(dict(user_data))
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

def get_personalized_feedback(user):
    """Get AI-driven personalized feedback based on user's data and progress."""
    try:
        # Get user's recent activity
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            SELECT 
                COUNT(*) as scan_count,
                STRING_AGG(food_name, ',') as foods,
                ROUND(AVG(total_cal)::numeric, 1) as avg_calories,
                ROUND(AVG(protein)::numeric, 1) as avg_protein,
                ROUND(AVG(total_carbs)::numeric, 1) as avg_carbs,
                ROUND(AVG(total_fat)::numeric, 1) as avg_fat
            FROM scanned_items 
            WHERE user_id = %s 
            AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
        ''', (user.id,))
        recent_activity = cur.fetchone()
        conn.close()

        # Calculate progress towards goal
        days_remaining = (datetime.strptime(user.data['target_date'], '%Y-%m-%d') - datetime.now()).days
        weight_diff = abs(user.data['weight'] - user.data['target_weight'])
        daily_change_needed = weight_diff / max(1, days_remaining) if days_remaining > 0 else 0

        # Get list of recent foods
        recent_foods = recent_activity['foods'].split(',') if recent_activity['foods'] else []

        # Prepare context for AI
        context = {
            "user_stats": {
                "age": user.data['age'],
                "gender": user.data['gender'],
                "current_weight": user.data['weight'],
                "target_weight": user.data['target_weight'],
                "height": user.data['height'],
                "goal": "lose weight" if user.data['goal'] == 1 else "maintain weight" if user.data['goal'] == 2 else "gain weight",
                "days_remaining": max(0, days_remaining),
                "daily_change_needed": daily_change_needed
            },
            "recent_activity": {
                "scans_last_7_days": recent_activity['scan_count'],
                "recent_foods": recent_foods[-5:],  # Last 5 foods
                "avg_daily_calories": round(recent_activity['avg_calories'] or 0, 1),
                "avg_daily_protein": round(recent_activity['avg_protein'] or 0, 1),
                "avg_daily_carbs": round(recent_activity['avg_carbs'] or 0, 1),
                "avg_daily_fat": round(recent_activity['avg_fat'] or 0, 1)
            },
            "targets": {
                "daily_calories": user.data['max_daily_calories'],
                "daily_protein": user.data['max_daily_protein']
            }
        }
        print(f"[DEBUG] Context: {context}")

        # Get AI insights
        response = perplexity_client.chat.completions.create(
            model="sonar",
            messages=[
                {
                    "role": "system",
                    "content": """You are a professional nutritionist and fitness coach. Analyze the user's data and provide personalized feedback in the following JSON format:
                    {
                        "overall_status": "string (one of: 'Excellent', 'Good', 'Needs Attention', 'Requires Improvement')",
                        "key_insights": ["string", "string", "string"],
                        "recommendations": ["string", "string", "string"],
                        "motivation": "string"
                    }
                    Keep insights and recommendations specific, actionable, and based on the data provided."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this user's nutrition and fitness data and provide personalized feedback: {json.dumps(context)}"
                }
            ],
            max_tokens=500
        )

        feedback = json.loads(response.choices[0].message.content)
        return feedback

    except Exception as e:
        print(f"Error getting personalized feedback: {str(e)}")
        return {
            "overall_status": "Good",
            "key_insights": [
                "Unable to analyze recent activity",
                "Continue tracking your meals regularly",
                "Stay consistent with your goals"
            ],
            "recommendations": [
                "Keep logging your meals",
                "Maintain a balanced diet",
                "Stay hydrated"
            ],
            "motivation": "Every small step counts towards your health goals!"
        }

@app.route("/profile")
@login_required
def profile():
    """Display user profile with personalized feedback."""
    print("[DEBUG] Accessing profile page")
    
    # Get today's nutrition totals for the user
    conn = get_db()
    cur = conn.cursor()
    
    # Get today's totals with proper rounding and type conversion
    cur.execute('''
        SELECT 
            ROUND(COALESCE(SUM(total_cal), 0)::numeric, 1) as calories,
            ROUND(COALESCE(SUM(potassium), 0)::numeric, 1) as potassium,
            ROUND(COALESCE(SUM(protein), 0)::numeric, 1) as protein,
            ROUND(COALESCE(SUM(total_carbs), 0)::numeric, 1) as carbs,
            ROUND(COALESCE(SUM(total_fat), 0)::numeric, 1) as total_fat
        FROM scanned_items 
        WHERE user_id = %s 
        AND DATE(timestamp) = CURRENT_DATE
    ''', (current_user.id,))
    
    totals = cur.fetchone()
    conn.close()
    
    # Convert SQLite Row to dictionary with proper float values
    totals_dict = {
        'calories': float(totals['calories']) if totals else 0.0,
        'potassium': float(totals['potassium']) if totals else 0.0,
        'protein': float(totals['protein']) if totals else 0.0,
        'carbs': float(totals['carbs']) if totals else 0.0,
        'total_fat': float(totals['total_fat']) if totals else 0.0
    }
    
    # Get personalized feedback
    feedback = get_personalized_feedback(current_user)
    
    return render_template('profile.html', 
                         user=current_user, 
                         totals=totals_dict,
                         feedback=feedback)

@app.route("/get_nutrition_data")
@login_required
def get_nutrition_data():
    """Get current day's nutrition data for the logged-in user."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get today's totals
    cur.execute('''
        SELECT 
            COALESCE(SUM(total_cal), 0) as calories,
            COALESCE(SUM(potassium), 0) as potassium,
            COALESCE(SUM(protein), 0) as protein,
            COALESCE(SUM(total_carbs), 0) as carbs,
            COALESCE(SUM(total_fat), 0) as total_fat
        FROM scanned_items 
        WHERE user_id = %s 
        AND DATE(timestamp) = CURRENT_DATE
    ''', (current_user.id,))
    
    totals = dict(cur.fetchone())
    conn.close()
    
    # Add max daily values from user data
    totals.update({
        'max_daily_calories': current_user.data['max_daily_calories'],
        'max_daily_protein': current_user.data['max_daily_protein']
    })
    
    return jsonify(totals)

# User class for Flask-Login
class User:
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        # Format target_date if it's a datetime object
        if isinstance(user_data['target_date'], datetime):
            user_data['target_date'] = user_data['target_date'].strftime('%Y-%m-%d')
        self.data = user_data
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_data = cur.fetchone()
    conn.close()
    
    if user_data:
        # Convert SQLite Row to dictionary
        user_dict = dict(user_data)
        return User(user_dict)
    return None

if __name__ == '__main__':
    print("[DEBUG] Starting Flask application")
    app.run(host='0.0.0.0', port=5001, debug=True)