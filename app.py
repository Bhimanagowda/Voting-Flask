from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

# PostgreSQL Database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname="voting_system",
        user="postgres",  
        password="12345",  
        host="localhost",
        port="5432"
    )
    return conn

# Initialize candidates and create necessary tables in PostgreSQL
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create table for votes if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id SERIAL PRIMARY KEY,
            candidate VARCHAR(255) NOT NULL,
            vote_count INT DEFAULT 0
        );
    ''')

    # Create a list of candidates if they don't exist in the DB
    candidates = ["Amith", "Deepak", "Navya", "Viraj", "Lavanya", "Divya"]
    for candidate in candidates:
        cursor.execute(
            'INSERT INTO votes (candidate, vote_count) SELECT %s, 0 WHERE NOT EXISTS (SELECT 1 FROM votes WHERE candidate = %s);',
            (candidate, candidate)
        )
    
    conn.commit()
    cursor.close()
    conn.close()

class VotingSystem:
    def __init__(self):
        self.candidates = self.get_candidates()
  
    def get_candidates(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT candidate FROM votes')
        candidates = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return candidates

    def add_vote(self, candidate):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE votes SET vote_count = vote_count + 1 WHERE candidate = %s', (candidate,))
        conn.commit()
        cursor.close()
        conn.close()

    def get_results(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT candidate, vote_count FROM votes')
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return {row[0]: row[1] for row in results}

    def get_winner(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT candidate FROM votes ORDER BY vote_count DESC LIMIT 1')
        winner = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return winner

# Initialize DB and candidates on server start
initialize_db()

voting_system = VotingSystem()

@app.route('/')
def index():
    return render_template('index.html', candidates=voting_system.candidates)

@app.route('/vote', methods=['POST'])
def vote():
    candidate = request.json.get("candidate")
    voting_system.add_vote(candidate)
    return jsonify({"message": f"Vote for {candidate} recorded successfully!"})

@app.route('/results')
def results():
    votes = voting_system.get_results()
    winner = voting_system.get_winner()
    winner_votes = votes[winner]
    return jsonify({"votes": votes, "winner": winner, "winner_votes": winner_votes})

if __name__ == '__main__':
    app.run(debug=True)
