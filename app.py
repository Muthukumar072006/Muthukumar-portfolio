from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    session,
    flash,
    url_for
)
import sqlite3
import os


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = 'muthukumar_portfolio_secret_key_2026'


# =========================================================
# ADMIN LOGIN
# =========================================================

ADMIN_USERNAME = 'muthu'
ADMIN_PASSWORD = 'Muthu@2006'


# =========================================================
# DATABASE PATH
# IMPORTANT:
# Always use the portfolio.db located beside app.py
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'portfolio.db')


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# LOGIN CHECK
# =========================================================

def is_logged_in():
    return session.get('logged_in', False)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # Messages Table
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Projects Table
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Skills Table
    # -----------------------------------------------------

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Run database initialization
init_db()


# =========================================================
# HOME / PORTFOLIO
# =========================================================

@app.route('/')
def home():

    conn = get_db_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # Get Projects
    # -----------------------------------------------------

    cursor.execute('''
        SELECT
            id,
            title,
            category,
            desc,
            tech,
            github,
            demo
        FROM projects
        ORDER BY id DESC
    ''')

    raw_projects = cursor.fetchall()

    projects = []

    for project in raw_projects:

        tech_list = []

        if project['tech']:
            tech_list = [
                item.strip()
                for item in project['tech'].split(',')
                if item.strip()
            ]

        projects.append({
            'id': project['id'],
            'title': project['title'],
            'category': project['category'],
            'desc': project['desc'],
            'tech': tech_list,
            'github': project['github'] or '',
            'demo': project['demo'] or ''
        })

    # -----------------------------------------------------
    # Get Skills
    # -----------------------------------------------------

    cursor.execute('''
        SELECT id, name, level
        FROM skills
        ORDER BY id DESC
    ''')

    raw_skills = cursor.fetchall()

    skills = []

    for skill in raw_skills:

        skills.append({
            'id': skill['id'],
            'name': skill['name'],
            'level': skill['level']
        })

    conn.close()

    return render_template(
        'index.html',
        projects=projects,
        skills=skills
    )


# =========================================================
# LOGIN
# =========================================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session['logged_in'] = True

            flash('Login successful!')
            return redirect(url_for('admin'))

        flash('Invalid Username or Password!')
        return redirect(url_for('login'))

    return render_template('login.html')


# =========================================================
# LOGOUT
# =========================================================

@app.route('/logout')
def logout():

    session.pop('logged_in', None)

    flash('Logged out successfully.')

    return redirect(url_for('login'))


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route('/admin')
def admin():

    if not is_logged_in():
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    cursor.execute('''
        SELECT id, name, level
        FROM skills
        ORDER BY id DESC
    ''')

    skills = cursor.fetchall()

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------

    cursor.execute('''
        SELECT id, title, category, desc, tech, github, demo
        FROM projects
        ORDER BY id DESC
    ''')

    projects = cursor.fetchall()

    # -----------------------------------------------------
    # Messages
    # -----------------------------------------------------

    cursor.execute('''
        SELECT
            id,
            name,
            email,
            subject,
            message,
            submitted_at
        FROM messages
        ORDER BY id DESC
    ''')

    messages = cursor.fetchall()

    # -----------------------------------------------------
    # Dashboard Counts
    # -----------------------------------------------------

    cursor.execute('SELECT COUNT(*) FROM skills')
    skill_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM projects')
    project_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM messages')
    message_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'admin.html',
        skills=skills,
        projects=projects,
        messages=messages,
        skill_count=skill_count,
        project_count=project_count,
        message_count=message_count
    )


# =========================================================
# ADD SKILL
# =========================================================

@app.route('/api/add-skill', methods=['POST'])
def add_skill():

    if not is_logged_in():
        return redirect(url_for('login'))

    name = request.form.get('name', '').strip()
    level = request.form.get('level', '').strip()

    if not name or not level:

        flash('Please fill Skill Name and Level.')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO skills (name, level)
        VALUES (?, ?)
        ''',
        (name, level)
    )

    conn.commit()
    conn.close()

    flash('Skill added successfully!')

    return redirect(url_for('admin'))


# =========================================================
# DELETE SKILL
# =========================================================

@app.route('/api/delete-skill/<int:skill_id>', methods=['POST'])
def delete_skill(skill_id):

    if not is_logged_in():
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM skills WHERE id = ?',
        (skill_id,)
    )

    conn.commit()
    conn.close()

    flash('Skill deleted successfully!')

    return redirect(url_for('admin'))


# =========================================================
# ADD PROJECT
# =========================================================

@app.route('/api/add-project', methods=['POST'])
def add_project():

    if not is_logged_in():
        return redirect(url_for('login'))

    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    desc = request.form.get('desc', '').strip()
    tech = request.form.get('tech', '').strip()
    github = request.form.get('github', '').strip()
    demo = request.form.get('demo', '').strip()

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if not title or not category or not desc or not tech:

        flash(
            'Please fill Project Title, Category, Description and Technologies.'
        )

        return redirect(url_for('admin'))

    # -----------------------------------------------------
    # Clean Technologies
    # -----------------------------------------------------

    tech_list = [
        item.strip()
        for item in tech.split(',')
        if item.strip()
    ]

    tech = ', '.join(tech_list)

    # -----------------------------------------------------
    # Insert
    # -----------------------------------------------------

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO projects
        (
            title,
            category,
            desc,
            tech,
            github,
            demo
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            title,
            category,
            desc,
            tech,
            github,
            demo
        )
    )

    conn.commit()
    conn.close()

    flash('Project added successfully!')

    return redirect(url_for('admin'))


# =========================================================
# EDIT PROJECT
# =========================================================

@app.route('/edit-project/<int:project_id>', methods=['GET'])
def edit_project(project_id):

    if not is_logged_in():
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT
            id,
            title,
            category,
            desc,
            tech,
            github,
            demo
        FROM projects
        WHERE id = ?
        ''',
        (project_id,)
    )

    project = cursor.fetchone()

    conn.close()

    if not project:

        flash('Project not found!')

        return redirect(url_for('admin'))

    return render_template(
        'edit_project.html',
        project=project
    )


# =========================================================
# UPDATE PROJECT
# =========================================================

@app.route('/api/update-project/<int:project_id>', methods=['POST'])
def update_project(project_id):

    if not is_logged_in():
        return redirect(url_for('login'))

    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    desc = request.form.get('desc', '').strip()
    tech = request.form.get('tech', '').strip()
    github = request.form.get('github', '').strip()
    demo = request.form.get('demo', '').strip()

    if not title or not category or not desc or not tech:

        flash(
            'Please fill all required project fields.'
        )

        return redirect(
            url_for(
                'edit_project',
                project_id=project_id
            )
        )

    tech_list = [
        item.strip()
        for item in tech.split(',')
        if item.strip()
    ]

    tech = ', '.join(tech_list)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        UPDATE projects
        SET
            title = ?,
            category = ?,
            desc = ?,
            tech = ?,
            github = ?,
            demo = ?
        WHERE id = ?
        ''',
        (
            title,
            category,
            desc,
            tech,
            github,
            demo,
            project_id
        )
    )

    conn.commit()
    conn.close()

    flash('Project updated successfully!')

    return redirect(url_for('admin'))


# =========================================================
# DELETE PROJECT
# =========================================================

@app.route('/api/delete-project/<int:project_id>', methods=['POST'])
def delete_project(project_id):

    if not is_logged_in():
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM projects WHERE id = ?',
        (project_id,)
    )

    conn.commit()
    conn.close()

    flash('Project deleted successfully!')

    return redirect(url_for('admin'))


# =========================================================
# CONTACT FORM
# =========================================================

@app.route('/api/contact', methods=['POST'])
def contact():

    data = request.get_json(silent=True) or {}

    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip()
    subject = str(
        data.get('subject', 'No Subject')
    ).strip()
    message = str(data.get('message', '')).strip()

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if not name or not email or not message:

        return jsonify({
            'status': 'error',
            'message': 'Please fill all required fields!'
        }), 400

    # -----------------------------------------------------
    # Save Message
    # -----------------------------------------------------

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO messages
        (
            name,
            email,
            subject,
            message
        )
        VALUES (?, ?, ?, ?)
        ''',
        (
            name,
            email,
            subject,
            message
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'message': 'Message sent & saved to database!'
    })


# =========================================================
# DELETE CONTACT MESSAGE
# =========================================================

@app.route('/api/delete-message/<int:message_id>', methods=['POST'])
def delete_message(message_id):

    if not is_logged_in():
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM messages WHERE id = ?',
        (message_id,)
    )

    conn.commit()
    conn.close()

    flash('Message deleted successfully!')

    return redirect(url_for('admin'))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == '__main__':

    print('==============================================')
    print('Portfolio Server Started')
    print('Database:', DB_PATH)
    print('==============================================')

    app.run(
        debug=True
    )