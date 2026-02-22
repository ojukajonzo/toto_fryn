"""
Database module for Toto Fryn learning system.
Handles initialization, schema creation, and data persistence.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class LearningDatabase:
    """Manages SQLite database for student progress tracking and analytics."""

    def __init__(self, db_path: str = "data/toto_learning.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self._ensure_db_directory()
        self.conn = None
        self.init_database()

    def _ensure_db_directory(self):
        """Ensure data directory exists."""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)

    def init_database(self):
        """Create database connection and initialize schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create all required tables for learning system."""
        cursor = self.conn.cursor()

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP
            )
        """)

        # Session table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                level TEXT NOT NULL,
                subject TEXT NOT NULL,
                theme TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """)

        # Questions and responses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                expected_answer TEXT,
                student_answer TEXT,
                is_correct BOOLEAN,
                difficulty_level INTEGER,
                response_time_seconds INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Progress tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                level TEXT NOT NULL,
                subject TEXT NOT NULL,
                theme TEXT NOT NULL,
                total_attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                accuracy_rate REAL DEFAULT 0.0,
                last_attempted TIMESTAMP,
                mastery_status TEXT DEFAULT 'beginner',
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE (student_id, level, subject, theme)
            )
        """)

        # Topic mastery table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_mastery (
                mastery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                level TEXT NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                mastery_percentage REAL DEFAULT 0.0,
                attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                last_practiced TIMESTAMP,
                status TEXT DEFAULT 'not_started',
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE (student_id, level, subject, topic)
            )
        """)

        # Difficulty adjustment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS difficulty_profile (
                profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                level TEXT NOT NULL,
                subject TEXT NOT NULL,
                current_difficulty INTEGER DEFAULT 1,
                min_difficulty INTEGER DEFAULT 1,
                max_difficulty INTEGER DEFAULT 5,
                recent_accuracy REAL DEFAULT 0.0,
                adjustment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE (student_id, level, subject)
            )
        """)

        # Learning recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                level TEXT NOT NULL,
                subject TEXT NOT NULL,
                weak_topic TEXT,
                strength_topic TEXT,
                recommendation_text TEXT,
                created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """)

        self.conn.commit()

    def add_student(self, name: str, grade: str) -> int:
        """Add a new student to the database."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO students (name, grade) VALUES (?, ?)", (name, grade))
        self.conn.commit()
        return cursor.lastrowid

    def get_student(self, student_id: int) -> Optional[Dict]:
        """Retrieve student information."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_last_active(self, student_id: int):
        """Update student's last active timestamp."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE students SET last_active = CURRENT_TIMESTAMP WHERE student_id = ?", (student_id,))
        self.conn.commit()

    def create_session(self, student_id: int, level: str, subject: str, theme: str) -> int:
        """Create a new learning session."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (student_id, level, subject, theme) VALUES (?, ?, ?, ?)",
            (student_id, level, subject, theme)
        )
        self.conn.commit()
        return cursor.lastrowid

    def end_session(self, session_id: int):
        """End a learning session and calculate duration."""
        cursor = self.conn.cursor()
        cursor.execute(
            """UPDATE sessions 
               SET end_time = CURRENT_TIMESTAMP,
                   duration_seconds = CAST((julianday('now') - julianday(start_time)) * 86400 AS INTEGER)
               WHERE session_id = ?""",
            (session_id,)
        )
        self.conn.commit()

    def record_response(self, session_id: int, question_id: str, question_text: str,
                       expected_answer: str, student_answer: str, is_correct: bool,
                       difficulty_level: int, response_time_seconds: int):
        """Record student's response to a question."""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO responses 
               (session_id, question_id, question_text, expected_answer, student_answer, 
                is_correct, difficulty_level, response_time_seconds)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, question_id, question_text, expected_answer, student_answer,
             is_correct, difficulty_level, response_time_seconds)
        )
        self.conn.commit()

    def update_progress(self, student_id: int, level: str, subject: str, theme: str, is_correct: bool):
        """Update progress tracking for a theme."""
        cursor = self.conn.cursor()

        # Check if record exists
        cursor.execute(
            "SELECT progress_id FROM progress WHERE student_id = ? AND level = ? AND subject = ? AND theme = ?",
            (student_id, level, subject, theme)
        )
        exists = cursor.fetchone()

        correct_increment = 1 if is_correct else 0

        if exists:
            cursor.execute(
                """UPDATE progress 
                   SET total_attempts = total_attempts + 1,
                       correct_attempts = correct_attempts + ?,
                       accuracy_rate = ROUND(100.0 * (correct_attempts + ?) / (total_attempts + 1), 2),
                       last_attempted = CURRENT_TIMESTAMP
                   WHERE student_id = ? AND level = ? AND subject = ? AND theme = ?""",
                (correct_increment, correct_increment, student_id, level, subject, theme)
            )
        else:
            accuracy = 100.0 if is_correct else 0.0
            cursor.execute(
                """INSERT INTO progress 
                   (student_id, level, subject, theme, total_attempts, correct_attempts, accuracy_rate, last_attempted)
                   VALUES (?, ?, ?, ?, 1, ?, ?, CURRENT_TIMESTAMP)""",
                (student_id, level, subject, theme, correct_increment, accuracy)
            )

        self.conn.commit()

    def update_topic_mastery(self, student_id: int, level: str, subject: str, topic: str, is_correct: bool):
        """Update topic-level mastery tracking."""
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT mastery_id FROM topic_mastery WHERE student_id = ? AND level = ? AND subject = ? AND topic = ?",
            (student_id, level, subject, topic)
        )
        exists = cursor.fetchone()

        correct_increment = 1 if is_correct else 0

        if exists:
            cursor.execute(
                """UPDATE topic_mastery 
                   SET attempts = attempts + 1,
                       correct_attempts = correct_attempts + ?,
                       mastery_percentage = ROUND(100.0 * (correct_attempts + ?) / (attempts + 1), 2),
                       last_practiced = CURRENT_TIMESTAMP
                   WHERE student_id = ? AND level = ? AND subject = ? AND topic = ?""",
                (correct_increment, correct_increment, student_id, level, subject, topic)
            )
        else:
            mastery_pct = 100.0 if is_correct else 0.0
            cursor.execute(
                """INSERT INTO topic_mastery 
                   (student_id, level, subject, topic, mastery_percentage, attempts, correct_attempts, last_practiced, status)
                   VALUES (?, ?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, 'in_progress')""",
                (student_id, level, subject, topic, mastery_pct, correct_increment)
            )

        self.conn.commit()

    def get_progress(self, student_id: int, level: str, subject: str) -> List[Dict]:
        """Get progress for a specific level and subject."""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT * FROM progress 
               WHERE student_id = ? AND level = ? AND subject = ?
               ORDER BY theme""",
            (student_id, level, subject)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_topic_mastery(self, student_id: int, level: str, subject: str) -> List[Dict]:
        """Get topic mastery data."""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT * FROM topic_mastery 
               WHERE student_id = ? AND level = ? AND subject = ?
               ORDER BY mastery_percentage DESC""",
            (student_id, level, subject)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_weak_topics(self, student_id: int, level: str, subject: str, threshold: float = 70.0) -> List[Dict]:
        """Get topics below mastery threshold."""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT * FROM topic_mastery 
               WHERE student_id = ? AND level = ? AND subject = ? AND mastery_percentage < ?
               ORDER BY mastery_percentage ASC""",
            (student_id, level, subject, threshold)
        )
        return [dict(row) for row in cursor.fetchall()]

    def update_difficulty_level(self, student_id: int, level: str, subject: str, new_difficulty: int):
        """Update student's difficulty level based on performance."""
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT profile_id FROM difficulty_profile WHERE student_id = ? AND level = ? AND subject = ?",
            (student_id, level, subject)
        )
        exists = cursor.fetchone()

        if exists:
            cursor.execute(
                """UPDATE difficulty_profile 
                   SET current_difficulty = ?, adjustment_timestamp = CURRENT_TIMESTAMP
                   WHERE student_id = ? AND level = ? AND subject = ?""",
                (new_difficulty, student_id, level, subject)
            )
        else:
            cursor.execute(
                """INSERT INTO difficulty_profile 
                   (student_id, level, subject, current_difficulty)
                   VALUES (?, ?, ?, ?)""",
                (student_id, level, subject, new_difficulty)
            )

        self.conn.commit()

    def get_difficulty_profile(self, student_id: int, level: str, subject: str) -> Optional[Dict]:
        """Get current difficulty profile."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM difficulty_profile WHERE student_id = ? AND level = ? AND subject = ?",
            (student_id, level, subject)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
