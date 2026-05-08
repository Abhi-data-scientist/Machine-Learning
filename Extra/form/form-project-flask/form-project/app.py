"""
app.py  —  Flask Backend
Form data receive karo aur MySQL mein save karo
"""

from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
from mysql.connector import Error
import re
import os

app = Flask(__name__, static_folder=".", template_folder=".")

# ── MySQL Config — apna password yahan daalo ───────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",           # apna MySQL username
    "password": "mr.abhi1149",   # apna MySQL password
    "database": "python_db"
}

# ── Database & Table auto-create ───────────────────────────────────────
def init_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id         INT AUTO_INCREMENT PRIMARY KEY,
                name       VARCHAR(100)  NOT NULL,
                phone      VARCHAR(15)   NOT NULL,
                email      VARCHAR(150)  NOT NULL,
                city       VARCHAR(100)  NOT NULL,
                created_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅  Database 'python_db' and table 'entries' are ready.")
    except Error as e:
        print(f"❌  DB init failed: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

# ── Serve index.html at / ──────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ── Serve static files (style.css, script.js) ─────────────────────────
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

# ── POST /api/submit — save entry to MySQL ────────────────────────────
@app.route("/api/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "message": "No JSON data received"}), 400

    # Read fields
    name  = str(data.get("name",  "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip()
    city  = str(data.get("city",  "")).strip()

    # Server-side validation
    errors = {}
    if len(name) < 2:
        errors["name"] = "Please enter your full name"
    if not re.match(r"^\d{10}$", phone):
        errors["phone"] = "Enter a valid 10-digit phone number"
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        errors["email"] = "Enter a valid email address"
    if len(city) < 2:
        errors["city"] = "Please enter your city name"

    if errors:
        return jsonify({"success": False, "errors": errors}), 422

    # Insert into MySQL
    try:
        conn   = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entries (name, phone, email, city) VALUES (%s, %s, %s, %s)",
            (name, phone, email, city)
        )
        conn.commit()
        new_id = cursor.lastrowid
        print(f"✅  New entry saved — ID: {new_id}, Name: {name}")
        return jsonify({
            "success": True,
            "message": "Entry saved successfully!",
            "id": new_id
        }), 201

    except Error as e:
        print(f"❌  DB insert error: {e}")
        return jsonify({"success": False, "message": "Database error. Please try again."}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ── GET /api/entries — fetch all saved entries ────────────────────────
@app.route("/api/entries", methods=["GET"])
def get_entries():
    try:
        conn   = get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM entries ORDER BY created_at DESC")
        rows = cursor.fetchall()
        for row in rows:
            if row.get("created_at"):
                row["created_at"] = row["created_at"].strftime("%d %b %Y, %I:%M %p")
        return jsonify({"success": True, "entries": rows})

    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ── Run ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("🚀  Server running at http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
