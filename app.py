"""
AI-Based Online Job Interview Preparation System
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
from functools import wraps
import json

# Import NLP modules
from nlp_evaluator import evaluate_answer

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production
app.config['DATABASE'] = 'instance/interview_system.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure directories exist
os.makedirs('instance', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Database connection helper
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    """Initialize database with schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Create questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            category TEXT,
            difficulty TEXT,
            ideal_answer TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add ideal_answer column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE questions ADD COLUMN ideal_answer TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create interviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            interview_type TEXT,
            total_questions INTEGER,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            status TEXT DEFAULT 'In Progress',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create interview_responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interview_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            user_answer TEXT NOT NULL,
            score REAL,
            feedback TEXT,
            keywords_matched TEXT,
            answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    ''')
    
    # Create performance_analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            interview_id INTEGER NOT NULL,
            overall_score REAL,
            hr_score REAL,
            technical_score REAL,
            total_questions INTEGER,
            questions_answered INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (interview_id) REFERENCES interviews(id)
        )
    ''')
    
    # Create default admin user (username: admin, password: admin123)
    admin_exists = cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_exists:
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@interview.com', admin_password, 'Administrator', 1))
    
    # Insert sample questions if table is empty
    question_count = cursor.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    if question_count == 0:
        sample_questions = [
            # Format: (question_text, question_type, category, difficulty, ideal_answer)
            ('Tell me about yourself.', 'HR', 'General', 'Easy', 
             'I am a dedicated IT professional with a strong background in software development. I have experience in Python, web development, and database management. I completed my BSc IT degree with a focus on practical applications. I enjoy solving complex problems and continuously learning new technologies. My goal is to contribute effectively to a dynamic team and grow professionally.'),
            
            ('What are your strengths and weaknesses?', 'HR', 'Behavioral', 'Medium',
             'My strengths include strong problem-solving skills, attention to detail, and the ability to work well in teams. I am proficient in Python programming and have good communication skills. As for weaknesses, I sometimes tend to be a perfectionist which can slow me down, but I am working on balancing quality with efficiency. I also continuously work on improving my time management skills.'),
            
            ('Why do you want to work here?', 'HR', 'Motivation', 'Medium',
             'I am interested in this position because your company values innovation and provides opportunities for professional growth. I admire your commitment to using cutting-edge technology and your collaborative work culture. I believe my skills in Python and web development align well with your projects. I am excited about the opportunity to contribute to meaningful projects and learn from experienced professionals in your team.'),
            
            ('Where do you see yourself in 5 years?', 'HR', 'Career Goals', 'Medium',
             'In five years, I see myself as a senior software developer or technical lead, having gained expertise in full-stack development and AI technologies. I plan to continue learning and staying updated with industry trends. I hope to mentor junior developers and contribute to innovative projects. My goal is to be a valuable team member who can handle complex technical challenges and help drive the company\'s technological advancement.'),
            
            ('What is Python?', 'Technical', 'Python', 'Easy',
             'Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms including object-oriented, procedural, and functional programming. Python has a large standard library and is widely used in web development, data science, artificial intelligence, automation, and scientific computing. It uses dynamic typing and automatic memory management.'),
            
            ('Explain the difference between list and tuple in Python.', 'Technical', 'Python', 'Medium',
             'Lists and tuples are both sequence data types in Python, but they have key differences. Lists are mutable, meaning you can modify them after creation - you can add, remove, or change elements. Lists are defined using square brackets []. Tuples are immutable, meaning once created, their elements cannot be changed. Tuples are defined using parentheses (). Lists are generally used when you need a collection that may change, while tuples are used for fixed collections. Tuples are also faster and use less memory than lists.'),
            
            ('What is SQL?', 'Technical', 'Database', 'Easy',
             'SQL stands for Structured Query Language. It is a standard programming language used for managing and manipulating relational databases. SQL allows you to perform various operations such as creating databases and tables, inserting, updating, deleting, and querying data. It is used to interact with database management systems like MySQL, PostgreSQL, SQLite, and Oracle. SQL consists of commands like SELECT, INSERT, UPDATE, DELETE, CREATE, and ALTER.'),
            
            ('Explain normalization in databases.', 'Technical', 'Database', 'Hard',
             'Normalization is a database design technique that organizes data to reduce redundancy and improve data integrity. It involves dividing large tables into smaller, related tables and defining relationships between them. The main normal forms are 1NF (First Normal Form), 2NF (Second Normal Form), and 3NF (Third Normal Form). 1NF ensures each column contains atomic values. 2NF eliminates partial dependencies. 3NF removes transitive dependencies. Normalization helps prevent data anomalies, reduces storage space, and makes the database more maintainable.'),
            
            ('What is Flask?', 'Technical', 'Web Development', 'Easy',
             'Flask is a lightweight and flexible Python web framework used for building web applications. It is considered a microframework because it does not require particular tools or libraries. Flask provides the essentials for web development like routing, request handling, and template rendering, while allowing developers to choose extensions for additional functionality. It is simple to learn and suitable for both small and large applications. Flask follows the WSGI standard and is known for its simplicity and flexibility.'),
            
            ('Explain REST API.', 'Technical', 'Web Development', 'Medium',
             'REST stands for Representational State Transfer. A REST API is an architectural style for designing networked applications. It uses standard HTTP methods like GET, POST, PUT, DELETE to perform operations on resources. REST APIs are stateless, meaning each request contains all information needed to process it. Resources are identified by URLs, and data is typically exchanged in JSON format. REST APIs are widely used because they are simple, scalable, and work well with HTTP. They follow principles like client-server architecture, statelessness, and uniform interface.')
        ]
        cursor.executemany('''
            INSERT INTO questions (question_text, question_type, category, difficulty, ideal_answer)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_questions)
    
    conn.commit()
    conn.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        conn = get_db()
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        if not user or user['is_admin'] != 1:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        conn = get_db()
        # Check if username or email already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists.', 'danger')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (username, email, password, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, full_name))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter username and password.', 'danger')
            return render_template('login.html')
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash(f'Welcome, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    conn = get_db()
    user_id = session['user_id']
    
    # Get user's interview history
    interviews = conn.execute('''
        SELECT * FROM interviews WHERE user_id = ? ORDER BY started_at DESC LIMIT 5
    ''', (user_id,)).fetchall()
    
    # Get performance stats
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_interviews,
            AVG(overall_score) as avg_score
        FROM performance_analytics
        WHERE user_id = ?
    ''', (user_id,)).fetchone()
    
    conn.close()
    return render_template('dashboard.html', interviews=interviews, stats=stats)

@app.route('/start_interview', methods=['GET', 'POST'])
@login_required
def start_interview():
    """Start a new mock interview"""
    if request.method == 'POST':
        interview_type = request.form.get('interview_type')
        num_questions = int(request.form.get('num_questions', 5))
        
        conn = get_db()
        user_id = session['user_id']
        
        # Get questions based on type
        if interview_type == 'Mixed':
            questions = conn.execute('''
                SELECT * FROM questions ORDER BY RANDOM() LIMIT ?
            ''', (num_questions,)).fetchall()
        else:
            questions = conn.execute('''
                SELECT * FROM questions WHERE question_type = ? ORDER BY RANDOM() LIMIT ?
            ''', (interview_type, num_questions)).fetchall()
        
        if not questions:
            flash('No questions available. Please add questions first.', 'warning')
            conn.close()
            return redirect(url_for('dashboard'))
        
        # Create interview record
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO interviews (user_id, interview_type, total_questions, status)
            VALUES (?, ?, ?, ?)
        ''', (user_id, interview_type, len(questions), 'In Progress'))
        interview_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        session['current_interview_id'] = interview_id
        session['interview_questions'] = [dict(q) for q in questions]
        session['current_question_index'] = 0
        
        return redirect(url_for('interview_question'))
    
    return render_template('start_interview.html')

@app.route('/interview/question')
@login_required
def interview_question():
    """Display current interview question"""
    if 'current_interview_id' not in session:
        flash('No active interview. Please start a new interview.', 'warning')
        return redirect(url_for('start_interview'))
    
    questions = session.get('interview_questions', [])
    current_index = session.get('current_question_index', 0)
    
    if current_index >= len(questions):
        return redirect(url_for('interview_complete'))
    
    question = questions[current_index]
    question_num = current_index + 1
    total_questions = len(questions)
    
    return render_template('interview_question.html', 
                         question=question, 
                         question_num=question_num,
                         total_questions=total_questions)

@app.route('/interview/answer', methods=['POST'])
@login_required
def submit_answer():
    """Submit answer for current question"""
    if 'current_interview_id' not in session:
        return jsonify({'error': 'No active interview'}), 400
    
    user_answer = request.form.get('answer', '')
    if not user_answer:
        flash('Please provide an answer.', 'warning')
        return redirect(url_for('interview_question'))
    
    questions = session.get('interview_questions', [])
    current_index = session.get('current_question_index', 0)
    question = questions[current_index]
    
    # Get ideal answer from database if available
    conn = get_db()
    question_row = conn.execute('SELECT ideal_answer FROM questions WHERE id = ?', (question['id'],)).fetchone()
    ideal_answer = question_row['ideal_answer'] if question_row and question_row['ideal_answer'] else None
    conn.close()
    
    # Evaluate answer using NLP (pass ideal_answer if available)
    evaluation = evaluate_answer(
        question['question_text'], 
        user_answer, 
        question['question_type'],
        ideal_answer=ideal_answer
    )
    
    # Save response to database
    conn = get_db()
    conn.execute('''
        INSERT INTO interview_responses 
        (interview_id, question_id, user_answer, score, feedback, keywords_matched)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        session['current_interview_id'],
        question['id'],
        user_answer,
        evaluation['score'],
        evaluation['feedback'],
        json.dumps(evaluation.get('keywords_matched', []))
    ))
    conn.commit()
    conn.close()
    
    # Store evaluation in session for feedback display
    session['last_evaluation'] = evaluation
    session['last_question'] = question
    session['last_user_answer'] = user_answer
    
    # Move to next question
    session['current_question_index'] = current_index + 1
    
    # Show feedback before next question
    return redirect(url_for('show_feedback'))

@app.route('/interview/feedback')
@login_required
def show_feedback():
    """Show feedback for the last answered question"""
    if 'last_evaluation' not in session:
        return redirect(url_for('interview_question'))
    
    evaluation = session.get('last_evaluation')
    question = session.get('last_question')
    user_answer = session.get('last_user_answer')
    questions = session.get('interview_questions', [])
    current_index = session.get('current_question_index', 0)
    
    # Check if interview is complete
    is_complete = current_index >= len(questions)
    
    # Clear feedback data from session
    session.pop('last_evaluation', None)
    session.pop('last_question', None)
    session.pop('last_user_answer', None)
    
    return render_template('interview_feedback.html',
                         evaluation=evaluation,
                         question=question,
                         user_answer=user_answer,
                         question_num=current_index,
                         total_questions=len(questions),
                         is_complete=is_complete)

@app.route('/interview/complete')
@login_required
def interview_complete():
    """Complete interview and show results"""
    if 'current_interview_id' not in session:
        return redirect(url_for('dashboard'))
    
    interview_id = session['current_interview_id']
    conn = get_db()
    
    # Get all responses for this interview
    responses = conn.execute('''
        SELECT ir.*, q.question_text, q.question_type, q.category
        FROM interview_responses ir
        JOIN questions q ON ir.question_id = q.id
        WHERE ir.interview_id = ?
        ORDER BY ir.answered_at
    ''', (interview_id,)).fetchall()
    
    if not responses:
        flash('No responses found.', 'warning')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Calculate scores
    total_score = sum(r['score'] for r in responses)
    avg_score = total_score / len(responses) if responses else 0
    
    hr_responses = [r for r in responses if r['question_type'] == 'HR']
    technical_responses = [r for r in responses if r['question_type'] == 'Technical']
    
    hr_score = sum(r['score'] for r in hr_responses) / len(hr_responses) if hr_responses else 0
    technical_score = sum(r['score'] for r in technical_responses) / len(technical_responses) if technical_responses else 0
    
    # Calculate strengths and weaknesses
    strengths = []
    weaknesses = []
    improvement_suggestions = []
    
    # Analyze by question type
    if hr_score >= 70:
        strengths.append("Strong performance in HR/Behavioral questions")
    elif hr_score < 50:
        weaknesses.append("Needs improvement in HR/Behavioral questions")
        improvement_suggestions.append("Practice common HR questions like 'Tell me about yourself', 'Why do you want to work here', and 'Where do you see yourself in 5 years'. Focus on providing structured, detailed answers with examples.")
    
    if technical_score >= 70:
        strengths.append("Strong technical knowledge and understanding")
    elif technical_score < 50:
        weaknesses.append("Technical knowledge needs improvement")
        improvement_suggestions.append("Review technical concepts related to your field. Practice explaining technical topics clearly and concisely. Include specific examples and use cases in your answers.")
    
    # Analyze by score ranges
    excellent_answers = [r for r in responses if r['score'] >= 80]
    poor_answers = [r for r in responses if r['score'] < 50]
    
    if len(excellent_answers) >= len(responses) * 0.5:
        strengths.append("Consistently providing detailed and comprehensive answers")
    elif len(poor_answers) >= len(responses) * 0.5:
        weaknesses.append("Answers are often too brief or lack detail")
        improvement_suggestions.append("Aim to provide answers with at least 50-100 words. Include relevant examples, explain concepts clearly, and structure your answers with an introduction, main points, and conclusion.")
    
    # Analyze by category performance
    category_scores = {}
    for r in responses:
        category = r['category'] or 'General'
        if category not in category_scores:
            category_scores[category] = []
        category_scores[category].append(r['score'])
    
    for category, scores in category_scores.items():
        avg_cat_score = sum(scores) / len(scores)
        if avg_cat_score >= 75:
            strengths.append(f"Strong understanding of {category} topics")
        elif avg_cat_score < 50:
            weaknesses.append(f"Needs improvement in {category} area")
            improvement_suggestions.append(f"Focus on studying {category} concepts. Review fundamental principles and practice explaining them in your own words.")
    
    # General suggestions based on overall performance
    if avg_score >= 80:
        strengths.append("Excellent overall interview performance")
    elif avg_score < 60:
        improvement_suggestions.append("Practice more mock interviews to improve your confidence and answer quality. Review your weak areas and prepare structured answers beforehand.")
    
    # Length analysis
    avg_length = sum(len(r['user_answer'].split()) for r in responses) / len(responses)
    if avg_length < 30:
        weaknesses.append("Answers are consistently too short")
        improvement_suggestions.append("Expand your answers by including examples, explaining your thought process, and providing context. Aim for 50-100 words per answer.")
    elif avg_length > 150:
        weaknesses.append("Some answers may be too lengthy")
        improvement_suggestions.append("Practice being concise while maintaining clarity. Focus on key points and avoid unnecessary details.")
    
    # If no specific strengths/weaknesses identified, provide general ones
    if not strengths:
        if avg_score >= 60:
            strengths.append("Good foundation in interview preparation")
        else:
            strengths.append("Completed the interview - practice makes perfect")
    
    if not weaknesses:
        weaknesses.append("Continue practicing to maintain consistency")
    
    if not improvement_suggestions:
        improvement_suggestions.append("Continue practicing mock interviews regularly")
        improvement_suggestions.append("Review feedback after each interview to identify patterns")
        improvement_suggestions.append("Prepare answers for common questions in advance")
    
    # Update interview status
    conn.execute('''
        UPDATE interviews 
        SET status = ?, completed_at = ?
        WHERE id = ?
    ''', ('Completed', datetime.now(), interview_id))
    
    # Save performance analytics
    conn.execute('''
        INSERT INTO performance_analytics 
        (user_id, interview_id, overall_score, hr_score, technical_score, total_questions, questions_answered)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        session['user_id'],
        interview_id,
        avg_score,
        hr_score,
        technical_score,
        len(responses),
        len(responses)
    ))
    
    conn.commit()
    conn.close()
    
    # Clear interview session
    session.pop('current_interview_id', None)
    session.pop('interview_questions', None)
    session.pop('current_question_index', None)
    
    return render_template('interview_complete.html', 
                         responses=responses,
                         avg_score=avg_score,
                         hr_score=hr_score,
                         technical_score=technical_score,
                         strengths=strengths,
                         weaknesses=weaknesses,
                         improvement_suggestions=improvement_suggestions)

@app.route('/performance')
@login_required
def performance():
    """View performance history"""
    conn = get_db()
    user_id = session['user_id']
    
    analytics = conn.execute('''
        SELECT pa.*, i.interview_type, i.started_at
        FROM performance_analytics pa
        JOIN interviews i ON pa.interview_id = i.id
        WHERE pa.user_id = ?
        ORDER BY pa.created_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    return render_template('performance.html', analytics=analytics)

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db()
    
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'total_questions': conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0],
        'total_interviews': conn.execute('SELECT COUNT(*) FROM interviews').fetchone()[0],
        'hr_questions': conn.execute("SELECT COUNT(*) FROM questions WHERE question_type = 'HR'").fetchone()[0],
        'technical_questions': conn.execute("SELECT COUNT(*) FROM questions WHERE question_type = 'Technical'").fetchone()[0],
    }
    
    conn.close()
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/questions', methods=['GET', 'POST'])
@admin_required
def admin_questions():
    """Manage questions"""
    conn = get_db()
    
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        question_type = request.form.get('question_type')
        category = request.form.get('category')
        difficulty = request.form.get('difficulty')
        ideal_answer = request.form.get('ideal_answer', '')
        
        conn.execute('''
            INSERT INTO questions (question_text, question_type, category, difficulty, ideal_answer)
            VALUES (?, ?, ?, ?, ?)
        ''', (question_text, question_type, category, difficulty, ideal_answer))
        conn.commit()
        flash('Question added successfully!', 'success')
    
    questions = conn.execute('SELECT * FROM questions ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/questions.html', questions=questions)

@app.route('/admin/questions/delete/<int:question_id>')
@admin_required
def delete_question(question_id):
    """Delete a question"""
    conn = get_db()
    conn.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin_questions'))

@app.route('/admin/users')
@admin_required
def admin_users():
    """View all users"""
    conn = get_db()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)


@app.route('/admin/results')
@admin_required
def admin_results():
    """View all interview results / performance analytics"""
    conn = get_db()
    results = conn.execute('''
        SELECT pa.*, u.username, i.interview_type, i.started_at
        FROM performance_analytics pa
        JOIN users u ON pa.user_id = u.id
        JOIN interviews i ON pa.interview_id = i.id
        ORDER BY pa.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/results.html', results=results)


@app.route('/admin/results/<int:interview_id>')
@admin_required
def admin_interview_results(interview_id):
    """View detailed responses for a specific interview"""
    conn = get_db()
    interview = conn.execute('SELECT i.*, u.username FROM interviews i JOIN users u ON i.user_id = u.id WHERE i.id = ?', (interview_id,)).fetchone()
    responses = conn.execute('''
        SELECT ir.*, q.question_text
        FROM interview_responses ir
        JOIN questions q ON ir.question_id = q.id
        WHERE ir.interview_id = ?
        ORDER BY ir.answered_at
    ''', (interview_id,)).fetchall()
    conn.close()
    return render_template('admin/interview_results.html', interview=interview, responses=responses)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

