import sqlite3
import os
from datetime import datetime

# Database configuration
DATABASE_NAME = "nutrition_data.db"

def get_db_connection():
    """Create a database connection and return the connection and cursor."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Create scanned_items table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS scanned_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        food_name TEXT NOT NULL,
        total_cal REAL,
        potassium REAL,
        protein REAL,
        total_carbs REAL,
        total_fat REAL,
        image_path TEXT
    )
    ''')

    # Create an index on timestamp for faster sorting
    cur.execute('''
    CREATE INDEX IF NOT EXISTS idx_timestamp 
    ON scanned_items(timestamp DESC)
    ''')

    conn.commit()
    conn.close()

def add_scan_record(food_name, nutrition_data, image_path=None):
    """
    Add a new scan record to the database.
    
    Args:
        food_name (str): Name of the food item
        nutrition_data (dict): Dictionary containing nutrition information
        image_path (str, optional): Path to the saved image
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
    INSERT INTO scanned_items 
    (food_name, total_cal, potassium, protein, total_carbs, total_fat, image_path, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        food_name,
        nutrition_data.get('total_cal', 0),
        nutrition_data.get('potassium', 0),
        nutrition_data.get('protein', 0),
        nutrition_data.get('total_carbs', 0),
        nutrition_data.get('total_fat', 0),
        image_path,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    conn.commit()
    conn.close()

def get_scan_records(page=1, per_page=10):
    """
    Get paginated scan records.
    
    Args:
        page (int): Page number (1-based)
        per_page (int): Number of records per page
    
    Returns:
        tuple: (records, total_pages, total_records)
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get total count
    cur.execute("SELECT COUNT(*) FROM scanned_items")
    total_records = cur.fetchone()[0]
    
    # Calculate total pages
    total_pages = (total_records + per_page - 1) // per_page
    
    # Get paginated records
    offset = (page - 1) * per_page
    cur.execute("""
        SELECT id, timestamp, food_name, total_cal, potassium, protein, total_carbs, total_fat, image_path
        FROM scanned_items 
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
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
    
    query = "SELECT * FROM scanned_items WHERE food_name LIKE ?"
    params = [f"%{search_term}%"]
    
    if date_filter:
        if date_filter == 'today':
            query += " AND date(timestamp) = date('now')"
        elif date_filter == 'week':
            query += " AND timestamp >= datetime('now', '-7 days')"
        elif date_filter == 'month':
            query += " AND timestamp >= datetime('now', '-1 month')"
    
    query += " ORDER BY timestamp DESC"
    
    cur.execute(query, params)
    records = cur.fetchall()
    conn.close()
    
    return records

# Initialize the database when this module is imported
if not os.path.exists(DATABASE_NAME):
    print(f"Initializing database: {DATABASE_NAME}")
    init_db() 