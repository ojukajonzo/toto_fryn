#!/usr/bin/env python3
"""
Toto Fryn - Interactive Learning System
Main orchestration module that coordinates all components
"""

import sys
import os
from typing import Optional
from datetime import datetime

# Import all modules
from teacher import Teacher
from database import LearningDatabase
from curriculum_validator import CurriculumValidator
from learning_engine import LearningEngineController, LearningSession
from analytics import ProgressAnalytics
from difficulty_adaptor import DifficultyAdaptor
from ollama_client import test_model


class TotoFryn:
    """Main Toto Fryn learning system controller."""

    def __init__(self, db_path: str = "data/toto_learning.db", 
                 curriculum_dir: str = "data/curriculum",
                 tts_enabled: bool = True,
                 ollama_model_evaluator: str = None,
                 ollama_model_questioner: str = None):
        """Initialize Toto Fryn system."""
        self.db_path = db_path
        self.curriculum_dir = curriculum_dir
        self.tts_enabled = tts_enabled
        # Allow model names to be passed or set via environment variables
        import os
        self.ollama_model_evaluator = ollama_model_evaluator or os.getenv('OLLAMA_EVALUATOR_MODEL', 'llama3.2:1b')
        self.ollama_model_questioner = ollama_model_questioner or os.getenv('OLLAMA_QUESTIONER_MODEL', 'llama3.2:1b')

        # Initialize components
        self.db = LearningDatabase(db_path)
        self.learning_engine = LearningEngineController(db_path, curriculum_dir,
                                ollama_evaluator=self.ollama_model_evaluator,
                                ollama_questioner=self.ollama_model_questioner)
        self.analytics = ProgressAnalytics(self.db)
        self.curriculum_validator = CurriculumValidator(curriculum_dir)

        self.current_student = None
        self.current_session = None

    def create_student(self, name: str, grade: str) -> int:
        """Create a new student."""
        student_id = self.db.add_student(name, grade)
        print(f"✓ Student '{name}' created (ID: {student_id})")
        return student_id

    def load_student(self, student_id: int) -> Optional[dict]:
        """Load student by ID."""
        student = self.db.get_student(student_id)
        if student:
            self.current_student = student
            print(f"✓ Loaded student: {student['name']} (Grade: {student['grade']})")
            return student
        else:
            print(f"✗ Student {student_id} not found")
            return None

    def start_learning(self, level: str, subject: str, theme: str) -> LearningSession:
        """Start an interactive learning session."""
        if not self.current_student:
            raise ValueError("No student loaded. Use load_student() first.")

        print(f"\n📚 Starting {level} {subject.title()} - {theme}")
        print("=" * 60)

        # Validate curriculum
        if not self.curriculum_validator.is_valid_theme(level, subject, theme):
            raise ValueError(f"Invalid theme: {theme}")

        # Start session
        self.current_session = self.learning_engine.start_learning_session(
            self.current_student["student_id"], level, subject, theme
        )

        print(f"✓ Session started. Ready to ask questions!")
        return self.current_session

    def ask_question(self) -> dict:
        """Ask next question in session."""
        if not self.current_session:
            raise ValueError("No active session. Use start_learning() first.")

        question = self.current_session.ask_question()
        self._speak(question["question_text"])

        return question

    def submit_answer(self, answer: str) -> dict:
        """Submit answer to current question."""
        if not self.current_session:
            raise ValueError("No active session.")

        result = self.current_session.submit_answer(answer)

        # Provide audio feedback
        if result["is_correct"]:
            self._speak(f"Correct! {result['feedback']}")
        else:
            self._speak(f"Not quite. {result['feedback']}")

        return result

    def get_hint(self) -> str:
        """Get hint for current question."""
        if not self.current_session:
            raise ValueError("No active session.")

        hint = self.current_session.get_hint()
        self._speak(hint)
        return hint

    def end_session(self) -> dict:
        """End current learning session and get summary."""
        if not self.current_session:
            raise ValueError("No active session.")

        summary = self.current_session.end_session()

        print(f"\n📊 Session Summary")
        print("=" * 60)
        print(f"Questions answered: {summary['questions_answered']}")
        print(f"Correct answers: {summary['correct_answers']}")
        print(f"Accuracy: {summary['accuracy_percentage']}%")
        print(f"Duration: {int(summary['duration_seconds'])} seconds")

        if summary.get("recommendations"):
            print(f"\n💡 Recommendations:")
            for rec in summary["recommendations"][:3]:
                print(f"  • {rec}")

        self.current_session = None
        return summary

    def get_student_progress(self, level: str, subject: str) -> dict:
        """Get student's progress for a subject."""
        if not self.current_student:
            raise ValueError("No student loaded.")

        return self.learning_engine.get_student_progress(
            self.current_student["student_id"], level, subject
        )

    def show_dashboard(self) -> dict:
        """Display student dashboard."""
        if not self.current_student:
            raise ValueError("No student loaded.")

        dashboard = self.analytics.get_student_dashboard(
            self.current_student["student_id"]
        )

        print(f"\n📈 Dashboard - {dashboard['name']} ({dashboard['grade']})")
        print("=" * 60)

        if "level_progress" in dashboard:
            for level, subjects in dashboard["level_progress"].items():
                print(f"\n{level}:")
                for subject, stats in subjects.items():
                    progress_pct = stats.get("progress_percentage", 0)
                    accuracy = stats.get("average_accuracy", 0)
                    print(f"  {subject.title()}: {progress_pct:.0f}% complete, {accuracy:.0f}% accuracy")

        return dashboard

    def get_curriculum_overview(self) -> dict:
        """Get curriculum structure overview."""
        # Return overview of available levels and subjects
        overview = {}
        for level in ["P1", "P2", "P3"]:
            overview[level] = self.curriculum_validator.get_curriculum_summary(level)

        return overview

    def _speak(self, text: str) -> None:
        """Speak text using TTS if enabled."""
        if not self.tts_enabled:
            return

        try:
            # Try to use existing mouth module if available
            from mouth import TotoMouth
            mouth = TotoMouth()
            mouth.speak(text)
        except ImportError:
            print(f"[Audio] {text}")
        except Exception as e:
            print(f"[Audio - Error: {e}] {text}")

    def close(self) -> None:
        """Close system and cleanup resources."""
        if self.learning_engine:
            self.learning_engine.close()
        if self.db:
            self.db.close()
        print("✓ Toto Fryn closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def interactive_learning_mode():
    """Run Toto Fryn in interactive learning mode."""
    with TotoFryn(tts_enabled=True) as toto:
        print("=" * 60)
        print("🎓 TOTO FRYN - Interactive Learning System")
        print("=" * 60)

        # Get or create student, reprompt on invalid entries
        print("\n👤 Student Management")
        while True:
            student_id = input("Enter student ID (or press Enter for new student): ").strip()
            if student_id == "":
                name = input("Student name: ").strip()
                grade = input("Grade (P1/P2/P3): ").strip().upper()
                if not name:
                    print("Name required. Try again.")
                    continue
                if grade not in ("P1", "P2", "P3"):
                    print("Invalid grade. Use P1, P2 or P3.")
                    continue
                sid = toto.create_student(name, grade)
                toto.load_student(sid)
                break
            elif student_id.isdigit():
                loaded = toto.load_student(int(student_id))
                if loaded:
                    break
                else:
                    print("Student ID not found. Try again or press Enter to create a new student.")
                    continue
            else:
                print("Invalid input. Enter a numeric student ID, or press Enter to create a new student.")
                continue

        # Start learning
        print("\n📚 Learning Management")
        toto.show_dashboard()

        # Reprompt until valid level and subject provided
        while True:
            level = input("\nSelect level (P1/P2/P3): ").strip().upper()
            if level in ("P1", "P2", "P3"):
                break
            print("Invalid level. Enter P1, P2 or P3.")

        while True:
            subject = input("Select subject (mathematics/english): ").strip().lower()
            if subject in ("mathematics", "english"):
                break
            print("Invalid subject. Enter 'mathematics' or 'english'.")

        # Show available themes
        themes = toto.curriculum_validator.get_all_themes(level, subject)
        print("\nAvailable themes:")
        for i, theme in enumerate(themes, 1):
            print(f"  {i}. {theme}")

        theme_idx = input("Select theme number: ").strip()
        # Default to first theme if input is empty or invalid
        if not theme_idx or not theme_idx.isdigit() or not (0 < int(theme_idx) <= len(themes)):
            print("No valid theme selected. Defaulting to first theme.")
            theme = themes[0]
        else:
            theme = themes[int(theme_idx) - 1]

        # Start session
        session = toto.start_learning(level, subject, theme)

        # Ask questions in loop
        question_count = 0
        max_questions = 5

        while question_count < max_questions:
            try:
                question = toto.ask_question()
                print(f"\n❓ {question['question_text']}")
                print(f"(Difficulty: {question['difficulty']}/5)")

                answer = input("\nYour answer (or 'hint' for help, 'quit' to end): ").strip()

                if answer.lower() == "quit":
                    break
                elif answer.lower() == "hint":
                    hint = toto.get_hint()
                    print(f"💡 Hint: {hint}")
                    continue
                else:
                    result = toto.submit_answer(answer)
                    print(f"\n✓ Accuracy so far: {result['current_accuracy']}%")
                    question_count += 1

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                break

        # End session
        summary = toto.end_session()

        # Show next recommendation
        if summary.get("next_suggested_theme"):
            print(f"\n🎯 Next theme to study: {summary['next_suggested_theme']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command-line interface
        cmd = sys.argv[1]

        # model-check command: python toto_main.py model-check <model-name>
        if cmd == "model-check":
            model_name = sys.argv[2] if len(sys.argv) > 2 else "llama3.2:1b"
            try:
                print(f"Testing model: {model_name} ...")
                resp = test_model(model_name)
                print(f"Model responded successfully: {resp}")
            except Exception as e:
                print(f"Model check failed: {e}")
        else:
            # Other commands
            with TotoFryn() as toto:
                if cmd == "dashboard":
                    student_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
                    toto.load_student(student_id)
                    dashboard = toto.show_dashboard()
                    print(f"\nDashboard data: {dashboard}")

                elif cmd == "curriculum":
                    overview = toto.get_curriculum_overview()
                    print(f"\nCurriculum Overview:")
                    for level, data in overview.items():
                        print(f"\n{level}: {data}")

                else:
                    print(f"Unknown command: {cmd}")
            
            # Populate database with demo students if empty
            db = LearningDatabase()
            cursor = db.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            count = cursor.fetchone()[0]
            if count == 0:
                db.add_student("Akello", "P1")
                db.add_student("Bukenya", "P2")
                db.add_student("Namutebi", "P3")
                print("✓ Demo students added: Akello (P1), Bukenya (P2), Namutebi (P3)")
            db.close()
    else:
        # Interactive mode (default)
        try:
            interactive_learning_mode()
        except KeyboardInterrupt:
            print("\n\nExiting Toto Fryn...")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
