from flask import Flask, jsonify, request
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "notesdb")   

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

@app.route("/health")
def health():
    return jsonify({"status":"ok"})

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS notes (\
        id SERIAL PRIMARY KEY,\
        content TEXT NOT NULL,\
        created_at TIMESTAMP DEFAULT NOW()\
    )")
    conn.commit()
    cur.close()
    conn.close()

@app.route("/notes")
def get_notes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, created_at FROM notes ORDER BY id")
    notes = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(notes)

@app.route("/notes", methods=["POST"])
def create_note():
    data=request.get_json()
    content=data.get("content")

    if not content:
        return jsonify({"error": "Content is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (content) VALUES (%s) RETURNING id, content, created_at", (content,))
    new_note = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify(new_note), 201
    

     
if __name__=="__main__":
    init_db()
    app.run(host="0.0.0.0",port=8000,debug=True)


