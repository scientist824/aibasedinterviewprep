# Database Schema - AI-Based Interview Preparation System

## Tables and Fields

### 1. users
- **id** (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- **username** (TEXT, UNIQUE, NOT NULL)
- **email** (TEXT, UNIQUE, NOT NULL)
- **password** (TEXT, NOT NULL) - Hashed password
- **full_name** (TEXT)
- **created_at** (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- **is_admin** (INTEGER, DEFAULT 0) - 0 for regular user, 1 for admin

### 2. questions
- **id** (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- **question_text** (TEXT, NOT NULL)
- **question_type** (TEXT, NOT NULL) - 'HR' or 'Technical'
- **category** (TEXT) - e.g., 'Python', 'Database', 'General', 'Behavioral'
- **difficulty** (TEXT) - 'Easy', 'Medium', 'Hard'
- **created_at** (DATETIME, DEFAULT CURRENT_TIMESTAMP)

### 3. interviews
- **id** (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- **user_id** (INTEGER, NOT NULL, FOREIGN KEY references users(id))
- **interview_type** (TEXT) - 'HR', 'Technical', 'Mixed'
- **total_questions** (INTEGER)
- **started_at** (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- **completed_at** (DATETIME)
- **status** (TEXT, DEFAULT 'In Progress') - 'In Progress', 'Completed'

### 4. interview_responses
- **id** (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- **interview_id** (INTEGER, NOT NULL, FOREIGN KEY references interviews(id))
- **question_id** (INTEGER, NOT NULL, FOREIGN KEY references questions(id))
- **user_answer** (TEXT, NOT NULL)
- **score** (REAL) - AI evaluation score (0-100)
- **feedback** (TEXT) - AI-generated feedback
- **keywords_matched** (TEXT) - JSON string of matched keywords
- **answered_at** (DATETIME, DEFAULT CURRENT_TIMESTAMP)

### 5. performance_analytics
- **id** (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- **user_id** (INTEGER, NOT NULL, FOREIGN KEY references users(id))
- **interview_id** (INTEGER, NOT NULL, FOREIGN KEY references interviews(id))
- **overall_score** (REAL) - Average score across all questions
- **hr_score** (REAL) - Average score for HR questions
- **technical_score** (REAL) - Average score for Technical questions
- **total_questions** (INTEGER)
- **questions_answered** (INTEGER)
- **created_at** (DATETIME, DEFAULT CURRENT_TIMESTAMP)

