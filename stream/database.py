import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from flask import g

from utils import calculate_bmr, calculate_daily_calories, calculate_daily_protein
# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")

def get_db_connection():
    """Create a database connection and return the connection and cursor."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=DictCursor
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Could not connect to database: {str(e)}")
        print("\nIf you're running locally, make sure PostgreSQL is installed and running.")
        print("You can also use Docker Compose with: docker-compose up --build")
        raise

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Create users table if it doesn't exist
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age INTEGER NOT NULL,
        weight REAL NOT NULL,
        target_weight REAL,
        gender TEXT NOT NULL,
        height INTEGER NOT NULL,
        goal INTEGER NOT NULL,
        target_date TIMESTAMP NOT NULL,
        calories INTEGER NOT NULL,
        potassium INTEGER NOT NULL,
        protein INTEGER NOT NULL,
        carbs INTEGER NOT NULL,
        total_fat INTEGER NOT NULL,
        max_daily_calories INTEGER NOT NULL,
        max_daily_protein INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create scanned_items table if it doesn't exist
    cur.execute('''
    CREATE TABLE IF NOT EXISTS scanned_items (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        food_name TEXT NOT NULL,
        total_cal REAL,
        potassium REAL,
        protein REAL,
        total_carbs REAL,
        total_fat REAL,
        image_path TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    # Create indexes if they don't exist
    cur.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON scanned_items(timestamp DESC)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON scanned_items(user_id)')

    conn.commit()
    conn.close()

def add_scan_record(user_id, food_name, nutrition_data, image_path=None):
    """
    Add a new scan record to the database.
    
    Args:
        user_id (int): ID of the user who scanned the food
        food_name (str): Name of the food item
        nutrition_data (dict): Dictionary containing nutrition information
        image_path (str, optional): Path to the saved image
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
    INSERT INTO scanned_items 
    (user_id, food_name, total_cal, potassium, protein, total_carbs, total_fat, image_path, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        user_id,
        food_name,
        nutrition_data.get('total_cal', 0),
        nutrition_data.get('potassium', 0),
        nutrition_data.get('protein', 0),
        nutrition_data.get('total_carbs', 0),
        nutrition_data.get('total_fat', 0),
        image_path,
        datetime.now()
    ))
    
    conn.commit()
    conn.close()

def get_scan_records(page=1, per_page=10, user_id=None):
    """
    Get paginated scan records.
    
    Args:
        page (int): Page number (1-based)
        per_page (int): Number of records per page
        user_id (int): Optional user ID to filter records
    
    Returns:
        tuple: (records, total_pages, total_records)
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get total count
    if user_id is not None:
        cur.execute("SELECT COUNT(*) FROM scanned_items WHERE user_id = %s", (user_id,))
    else:
        cur.execute("SELECT COUNT(*) FROM scanned_items")
    total_records = cur.fetchone()[0]
    
    # Calculate total pages
    total_pages = (total_records + per_page - 1) // per_page
    
    # Get paginated records
    offset = (page - 1) * per_page
    if user_id is not None:
        cur.execute("""
            SELECT id, timestamp, food_name, total_cal, potassium, protein, total_carbs, total_fat, image_path
            FROM scanned_items 
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))
    else:
        cur.execute("""
            SELECT id, timestamp, food_name, total_cal, potassium, protein, total_carbs, total_fat, image_path
            FROM scanned_items 
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
    
    records = cur.fetchall()
    conn.close()
    
    return records, total_pages, total_records

def search_records(search_term, date_filter=None):
    """
    Search records by food name and date filter.
    
    Args:
        search_term (str): Term to search in food_name
        date_filter (str, optional): 'today', 'week', 'month', or None
    
    Returns:
        list: Matching records
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT * FROM scanned_items WHERE food_name ILIKE %s"
    params = [f"%{search_term}%"]
    
    if date_filter:
        if date_filter == 'today':
            query += " AND date(timestamp) = current_date"
        elif date_filter == 'week':
            query += " AND timestamp >= current_date - interval '7 days'"
        elif date_filter == 'month':
            query += " AND timestamp >= current_date - interval '1 month'"
    
    query += " ORDER BY timestamp DESC"
    
    cur.execute(query, params)
    records = cur.fetchall()
    conn.close()
    
    return records

def create_user(username, password, age, weight, target_weight, gender, height, goal, target_date):
    """Create a new user with nutrition goals."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Calculate base nutrition values based on user data
        bmr = calculate_bmr(weight, height, age, gender)
        max_daily_calories = calculate_daily_calories(bmr, goal)
        max_daily_protein = calculate_daily_protein(weight, goal)
        
        hashed_password = generate_password_hash(password)
        
        cur.execute('''
        INSERT INTO users (
            username, password, age, weight, target_weight, gender, height, goal, target_date,
            calories, potassium, protein, carbs, total_fat,
            max_daily_calories, max_daily_protein
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''', (
            username, hashed_password, age, weight, target_weight, gender, height, goal, target_date,
            0, 0, 0, 0, 0,  # Initial daily values
            max_daily_calories, max_daily_protein
        ))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.IntegrityError:
        return None
    finally:
        conn.close()

def get_db():
    """Get database connection for use with 'with' statement."""
    if not hasattr(g, 'db'):
        g.db = get_db_connection()
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize the database when this module is imported
try:
    init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Error initializing database: {str(e)}") 