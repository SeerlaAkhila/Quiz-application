from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json

# Initialize the Flask application
app = Flask(__name__)

# --- Database Setup ---
def init_db():
    """Initializes the database and creates the scores table if it doesn't exist."""
    with sqlite3.connect('quiz.db') as conn:
        cursor = conn.cursor()
        # Create a table to store user scores if it's not already there
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL
            )
        ''')
        conn.commit()

# --- Quiz Data ---
# A simple list of dictionaries to hold our quiz questions.
# In a real-world application, you would likely load this from a database or a JSON file.
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Lisbon"],
        "answer": "Paris"
    },
    {
        "id": 2,
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Mars"
    },
    {
        "id": 3,
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "answer": "Pacific"
    },
    {
        "id": 4,
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"],
        "answer": "William Shakespeare"
    },
    {
        "id": 5,
        "question": "What is the value of 'c' in E=mc^2?",
        "options": ["Speed of sound", "Speed of light", "Mass of Earth", "Gravitational constant"],
        "answer": "Speed of light"
    }
]


# --- Routes ---

@app.route('/')
def index():
    """Renders the main quiz page."""
    # The main page, renders the quiz interface.
    return render_template('index.html', questions=QUIZ_QUESTIONS)

@app.route('/submit', methods=['POST'])
def submit():
    """Handles quiz submission, calculates score, and saves it."""
    try:
        # Get the submitted data (user's answers and name)
        data = request.get_json()
        answers = data.get('answers')
        name = data.get('name', 'Anonymous') # Default to 'Anonymous' if no name is provided
        
        if not answers:
            return jsonify({"error": "No answers provided"}), 400

        score = 0
        # Iterate through the correct answers and check against user's submission
        for question in QUIZ_QUESTIONS:
            question_id = str(question["id"])
            correct_answer = question["answer"]
            # Check if the user's answer matches the correct answer
            if question_id in answers and answers[question_id] == correct_answer:
                score += 1
        
        # Save the score to the database
        with sqlite3.connect('quiz.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
            conn.commit()
            
        # Return the final score and total number of questions
        return jsonify({
            'score': score,
            'total': len(QUIZ_QUESTIONS)
        })

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error in /submit: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/history')
def history():
    """Fetches and displays the quiz history."""
    with sqlite3.connect('quiz.db') as conn:
        conn.row_factory = sqlite3.Row # This allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT name, score FROM scores ORDER BY id DESC LIMIT 10")
        scores = [dict(row) for row in cursor.fetchall()]
    return render_template('history.html', scores=scores)


# --- Main execution block ---
if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(debug=True) # Runs the app in debug mode for development
