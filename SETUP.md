# Setup Guide - AI Interview Preparation System

## Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download NLTK Data (First Time Only)
The application will automatically download required NLTK data on first run, but you can also do it manually:
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Access the Application
- Open your browser and go to: `http://localhost:5000`
- Default Admin Login:
  - Username: `admin`
  - Password: `admin123`

## First Time Setup

1. The database will be created automatically in `instance/interview_system.db`
2. Sample questions (10 questions) will be pre-loaded
3. Default admin account will be created

## Project Structure

```
├── app.py                    # Main Flask application
├── nlp_evaluator.py          # NLP evaluation module
├── requirements.txt           # Python dependencies
├── database_schema.md         # Database documentation
├── README.md                 # Project documentation
├── SETUP.md                  # This file
├── .gitignore                # Git ignore file
├── instance/                 # Database storage (auto-created)
│   └── interview_system.db
├── templates/                # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── start_interview.html
│   ├── interview_question.html
│   ├── interview_complete.html
│   ├── performance.html
│   └── admin/
│       ├── dashboard.html
│       ├── questions.html
│       └── users.html
└── static/                   # Static files
    ├── css/
    │   └── style.css
    └── uploads/              # Upload directory (auto-created)
```

## Features Overview

### User Features
- ✅ User Registration & Login
- ✅ Start Mock Interviews (HR/Technical/Mixed)
- ✅ Answer Questions with AI Evaluation
- ✅ View Performance Analytics
- ✅ Detailed Feedback for Each Answer

### Admin Features
- ✅ Admin Dashboard with Statistics
- ✅ Manage Question Bank (Add/Delete)
- ✅ View All Users

### AI Evaluation
- ✅ Keyword Matching
- ✅ TF-IDF Similarity Analysis
- ✅ Answer Length Analysis
- ✅ Domain-Specific Feedback

## Testing the System

1. **Register a new user** or use admin account
2. **Start an interview** from the dashboard
3. **Answer questions** - try to write detailed answers (20+ words)
4. **View feedback** after each question
5. **Check performance** page for analytics

## Troubleshooting

### Issue: NLTK data not found
**Solution**: Run `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

### Issue: Database errors
**Solution**: Delete `instance/interview_system.db` and restart the app (database will be recreated)

### Issue: Port already in use
**Solution**: Change port in `app.py` last line: `app.run(debug=True, port=5001)`

## For Viva/Project Presentation

### Key Points to Highlight:
1. **Flask Backend**: RESTful routing, session management
2. **SQLite Database**: 5 tables with proper relationships
3. **NLP Implementation**: NLTK + scikit-learn for text analysis
4. **User Authentication**: Secure password hashing
5. **Admin Panel**: Question management system
6. **Performance Tracking**: Analytics and feedback system

### Technical Stack:
- Python Flask (Web Framework)
- SQLite (Database)
- NLTK (Natural Language Processing)
- scikit-learn (Machine Learning)
- Bootstrap 5 (Frontend Framework)

## Notes

- All processing is done locally (no external APIs)
- Suitable for academic presentation
- Simple and easy to understand code structure
- Well-documented for viva preparation

