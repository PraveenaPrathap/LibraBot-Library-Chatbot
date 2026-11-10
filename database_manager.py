import sqlite3
import csv
import os

DB_NAME = 'lumina_library.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Books Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT,
            author TEXT,
            genre TEXT,
            availability TEXT
        )
    ''')
    
    # Borrowing Records Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowing_records (
            record_id TEXT PRIMARY KEY,
            user_id TEXT,
            book_id TEXT,
            status TEXT,
            due_date TEXT
        )
    ''')
    
    # Knowledge Base Table (For training module)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_pattern TEXT,
            answer TEXT
        )
    ''')
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    
    # Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def load_single_csv_to_db(csv_path):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if csv_path and os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                book_id = row.get('book_id', '')
                title = row.get('book_title', '')
                author = row.get('author', '')
                genre = row.get('book_category', '')
                
                # Determine basic availability
                return_status = row.get('return_status', '')
                availability = 'Borrowed' if return_status == 'Overdue' else 'Available'
                
                cursor.execute('''
                    INSERT OR REPLACE INTO books (book_id, title, author, genre, availability)
                    VALUES (?, ?, ?, ?, ?)
                ''', (book_id, title, author, genre, availability))
                
                user_id = row.get('user_id', '')
                due_date = row.get('due_date', '')
                status = 'Borrowed' if return_status == 'Overdue' else 'Returned'
                borrow_date = row.get('borrow_date', '')
                record_id = f"{user_id}_{book_id}_{borrow_date}"
                
                cursor.execute('''
                    INSERT OR REPLACE INTO borrowing_records (record_id, user_id, book_id, status, due_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (record_id, user_id, book_id, status, due_date))
                
    conn.commit()
    conn.close()

# Database Query Functions
def search_books_by_title(title):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, availability FROM books WHERE title LIKE ?", ('%' + title + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

def search_books_by_author(author):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, availability FROM books WHERE author LIKE ?", ('%' + author + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

def get_recommendations_by_genre(genre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, author FROM books WHERE genre LIKE ? AND availability='Available' LIMIT 5", ('%' + genre + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

def get_borrowing_status(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.title, r.status, r.due_date 
        FROM borrowing_records r
        JOIN books b ON r.book_id = b.book_id
        WHERE r.user_id = ? AND r.status = 'Borrowed'
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

# Training Module Functions
def add_to_knowledge_base(question_pattern, answer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO knowledge_base (question_pattern, answer)
        VALUES (?, ?)
    ''', (question_pattern, answer))
    conn.commit()
    conn.close()

def get_all_knowledge():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT question_pattern, answer FROM knowledge_base")
    results = cursor.fetchall()
    conn.close()
    return results

# User and Chat History Functions
def create_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def save_chat_message(username, role, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (username, role, content) VALUES (?, ?, ?)", (username, role, content))
    conn.commit()
    conn.close()

def get_chat_history(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history WHERE username = ? ORDER BY timestamp ASC", (username,))
    results = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in results]
