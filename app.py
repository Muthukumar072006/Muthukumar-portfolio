from flask import Flask, render_template, request, redirect, jsonify, session, flash
import sqlite3

app = Flask(__name__)

# Secret key required for session management
app.secret_key = 'muthukumar_portfolio_secret_key_2026'

# Set Admin Credentials
ADMIN_USERNAME = 'muthu'
ADMIN_PASSWORD = 'Muthu@2006'  # Ungalukku pudicha password-a inga maathikonga

# Helper function to check login status
def is_logged_in():
    return session.get('logged_in', False)

# Initialize SQLite Database & Tables
def init_db():
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    
    # Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Projects Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            desc TEXT NOT NULL,
            tech TEXT NOT NULL,
            github TEXT,
            demo TEXT
        )
    ''')
    
    # Skills Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Main Portfolio Page (Public Access)
@app.route('/')
def home():
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    
    # Fetch Projects
    cursor.execute('SELECT title, category, desc, tech, github, demo FROM projects')
    raw_projects = cursor.fetchall()
    projects = []
    for p in raw_projects:
        projects.append({
            "title": p[0],
            "category": p[1],
            "desc": p[2],
            "tech": p[3].split(','),  # Convert CSV string to list
            "github": p[4],
            "demo": p[5]
        })
        
    # Fetch Skills
    cursor.execute('SELECT name, level FROM skills')
    raw_skills = cursor.fetchall()
    skills = [{"name": s[0], "level": s[1]} for s in raw_skills]
    
    conn.close()
    return render_template('index.html', projects=projects, skills=skills)

# Login Route (GET & POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect('/admin')
        else:
            flash('Invalid Username or Password!')
            return redirect('/login')
            
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

# Admin Panel Page (Protected)
@app.route('/admin')
def admin():
    if not is_logged_in():
        return redirect('/login')

    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, level FROM skills')
    skills = cursor.fetchall()
    
    cursor.execute('SELECT id, title, category FROM projects')
    projects = cursor.fetchall()
    
    cursor.execute('SELECT id, name, email, subject, message, submitted_at FROM messages ORDER BY id DESC')
    messages = cursor.fetchall()
    
    conn.close()
    return render_template('admin.html', skills=skills, projects=projects, messages=messages)

# Add Skill (Protected)
@app.route('/api/add-skill', methods=['POST'])
def add_skill():
    if not is_logged_in():
        return redirect('/login')

    name = request.form.get('name')
    level = request.form.get('level')
    if name and level:
        conn = sqlite3.connect('portfolio.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO skills (name, level) VALUES (?, ?)', (name, level))
        conn.commit()
        conn.close()
    return redirect('/admin')

# Delete Skill (Protected)
@app.route('/api/delete-skill/<int:skill_id>', methods=['POST'])
def delete_skill(skill_id):
    if not is_logged_in():
        return redirect('/login')

    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

# Add Project (Protected)
@app.route('/api/add-project', methods=['POST'])
def add_project():
    if not is_logged_in():
        return redirect('/login')

    title = request.form.get('title')
    category = request.form.get('category')
    desc = request.form.get('desc')
    tech = request.form.get('tech')
    github = request.form.get('github', '#')
    demo = request.form.get('demo', '#')
    
    if title and category and desc:
        conn = sqlite3.connect('portfolio.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO projects (title, category, desc, tech, github, demo) VALUES (?, ?, ?, ?, ?, ?)',
            (title, category, desc, tech, github, demo)
        )
        conn.commit()
        conn.close()
    return redirect('/admin')

# Delete Project (Protected)
@app.route('/api/delete-project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if not is_logged_in():
        return redirect('/login')

    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

# AJAX Contact API (Public Access)
@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject', 'No Subject')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({"status": "error", "message": "Please fill all required fields!"}), 400

    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO messages (name, email, subject, message) VALUES (?, ?, ?, ?)',
        (name, email, subject, message)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Message sent & saved to database!"})

if __name__ == '__main__':
    app.run(debug=True)