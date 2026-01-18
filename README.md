# AI-Based Online Job Interview Preparation System

A TY BSc IT final-year project that helps users prepare for job interviews using AI-powered evaluation.

## Features

- **User Registration & Login**: Secure authentication system
- **Question Bank**: HR and Technical questions with categories
- **Mock Interview Module**: Text-based interview simulation
- **AI-Based Answer Evaluation**: Uses NLTK and scikit-learn for NLP analysis
- **Performance Analytics**: Track progress and view detailed feedback
- **Admin Panel**: Manage questions and view users

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap 5
- **NLP**: NLTK, scikit-learn
- **Other**: NumPy, Pandas

## Installation

1. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**

   ```bash
   python app.py
   ```

3. **Access the application:**
   - Open browser: `http://localhost:5000`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`

## Project Structure

```
ai-based-interview-preparation-system/
├── app.py                 # Main Flask application
├── nlp_evaluator.py       # NLP evaluation module
├── requirements.txt        # Python dependencies
├── database_schema.md      # Database schema documentation
├── README.md              # This file
├── instance/
│   └── interview_system.db  # SQLite database (created automatically)
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # User dashboard
│   ├── start_interview.html
│   ├── interview_question.html
│   ├── interview_complete.html
│   ├── performance.html
│   └── admin/
│       ├── dashboard.html
│       ├── questions.html
│       └── users.html
└── static/
    ├── css/
    │   └── style.css      # Custom styles
    └── uploads/           # Upload directory
```

## Database Schema

The system uses SQLite with the following tables:

1. **users**: User accounts and authentication
2. **questions**: Question bank (HR and Technical)
3. **interviews**: Interview sessions
4. **interview_responses**: User answers and AI evaluations
5. **performance_analytics**: Performance tracking and statistics

See `database_schema.md` for detailed schema documentation.

## Usage

1. **Register/Login**: Create an account or login
2. **Start Interview**: Choose interview type (HR/Technical/Mixed) and number of questions
3. **Answer Questions**: Type your answers for each question
4. **View Feedback**: Get instant AI-powered feedback after each answer
5. **Check Performance**: View your performance history and analytics

## Admin Features

- Add/Delete questions
- View all users
- View system statistics

## NLP Evaluation

The system uses:

- **NLTK**: Text preprocessing, tokenization, stemming
- **scikit-learn**: TF-IDF vectorization and cosine similarity
- **Keyword Matching**: Domain-specific keyword analysis
- **Length Analysis**: Answer completeness scoring

## Notes

- This is an academic project for TY BSc IT
- No paid APIs or external services required
- All NLP processing is done locally
- Database is initialized automatically on first run
- Sample questions are pre-loaded

## How to run (step-by-step)

1. Create and activate a Python virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize and run the application:
   ```bash
   python app.py
   ```
4. Open the application in your browser at `http://localhost:5000`.
5. Default admin credentials:
   - Username: `admin`
   - Password: `admin123`

## Sample screenshots (descriptions)

- **Login / Register**: Simple Bootstrap card forms for signing in and signing up (username, email, password).
- **Dashboard**: Shows total interviews, average score, recent interviews, and quick actions (Start Interview / View Performance).
- **Mock Interview (Question Page)**: Full-width card showing the question, metadata (type/category/difficulty), and a large textarea for typing the answer.
- **Feedback (Per Question)**: Card displaying AI evaluation score, visual progress bar, feedback text, matched keywords, and a short explanation of the evaluation method.
- **Final Results**: Shows Overall / HR / Technical scores, detailed feedback per question, strengths & weaknesses, and suggested improvements.
- **Admin Panel**: Dashboard statistics, question management form (with ideal answer), user list, and a results page to inspect interview responses.

## Future scope (voice & video interviews)

- **Voice (Speech-to-Text)**: Integrate an open-source STT engine (e.g., VOSK) or cloud STT with explicit consent to convert spoken answers into text for the existing NLP pipeline.
- **Video (Behavioral Analysis)**: Capture short webcam recordings and analyze non-verbal cues (eye contact, facial expressions) using lightweight computer vision models. Add consent and privacy controls.
- **Real-time Feedback**: Implement streaming evaluation to provide hints during an ongoing answer (advanced feature).
- **Interview Scheduling & Mock Interviewers**: Add timed interviews, scheduling, and interviewer personas (automated prompts and follow-ups).

## Development

- Flask debug mode is enabled by default
- Change `app.secret_key` in production
- Database file is created in `instance/` directory

## License

Academic Project - TY BSc IT
