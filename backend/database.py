"""
database.py - SQLite database for storing user sessions, plans, and feedback.
Uses a simple SQLite database — no heavy ORMs, just raw SQL.
"""

import sqlite3
import json
import os
from datetime import datetime

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "house_planner.db")


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return conn


def init_db():
    """
    Initialize the database by creating all required tables.
    Called once when the Flask app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Sessions table - stores each user's planning session
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            user_inputs TEXT,       -- JSON: original user inputs
            constraints TEXT,       -- JSON: parsed AI constraints
            feedback_history TEXT   -- JSON: list of feedback messages
        )
    """)

    # Plans table - stores each generated floor plan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            plan_name TEXT NOT NULL,    -- e.g., "Plan A", "Plan B", "Plan C"
            plan_data TEXT,             -- JSON: room layout data
            image_path TEXT,            -- Path to generated SVG/PNG image
            pdf_path TEXT,              -- Path to generated PDF
            created_at TEXT NOT NULL,
            iteration INTEGER DEFAULT 1 -- Which regeneration iteration
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


def save_session(session_id: str, user_inputs: dict, constraints: dict) -> int:
    """
    Save or update a user session with their inputs and parsed constraints.
    Returns the session row ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    # Check if session exists
    cursor.execute("SELECT id FROM sessions WHERE session_id = ?", (session_id,))
    existing = cursor.fetchone()

    if existing:
        # Update existing session
        cursor.execute("""
            UPDATE sessions 
            SET updated_at = ?, user_inputs = ?, constraints = ?
            WHERE session_id = ?
        """, (now, json.dumps(user_inputs), json.dumps(constraints), session_id))
        row_id = existing["id"]
    else:
        # Insert new session
        cursor.execute("""
            INSERT INTO sessions (session_id, created_at, updated_at, user_inputs, constraints, feedback_history)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, now, now, json.dumps(user_inputs), json.dumps(constraints), json.dumps([])))
        row_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return row_id


def save_plan(session_id: str, plan_name: str, plan_data: dict, image_path: str, iteration: int = 1):
    """Save a generated floor plan to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO plans (session_id, plan_name, plan_data, image_path, created_at, iteration)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, plan_name, json.dumps(plan_data), image_path, now, iteration))

    conn.commit()
    conn.close()


def get_session(session_id: str) -> dict:
    """Retrieve a session by its ID. Returns None if not found."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "session_id": row["session_id"],
            "user_inputs": json.loads(row["user_inputs"] or "{}"),
            "constraints": json.loads(row["constraints"] or "{}"),
            "feedback_history": json.loads(row["feedback_history"] or "[]"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
    return None


def add_feedback(session_id: str, feedback: str):
    """Append a feedback message to the session's feedback history."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT feedback_history FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()

    if row:
        history = json.loads(row["feedback_history"] or "[]")
        history.append({
            "text": feedback,
            "timestamp": datetime.now().isoformat()
        })
        cursor.execute("""
            UPDATE sessions SET feedback_history = ?, updated_at = ?
            WHERE session_id = ?
        """, (json.dumps(history), datetime.now().isoformat(), session_id))
        conn.commit()

    conn.close()


def update_session_constraints(session_id: str, constraints: dict):
    """Update the constraints for an existing session (used after feedback)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions SET constraints = ?, updated_at = ?
        WHERE session_id = ?
    """, (json.dumps(constraints), datetime.now().isoformat(), session_id))

    conn.commit()
    conn.close()
