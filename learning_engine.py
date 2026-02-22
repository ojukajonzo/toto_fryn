"""
Interactive learning engine for Toto Fryn.
Manages learning sessions with questioning, feedback, and progress tracking.
"""

import time
from typing import Dict, Optional, Tuple
from datetime import datetime

from database import LearningDatabase
from curriculum_validator import CurriculumValidator
from question_generator import QuestionGenerator
from difficulty_adaptor import DifficultyAdaptor, PerformanceAnalyzer
from ollama_client import query_model


class LearningSession:
    """Manages an interactive learning session."""

    def __init__(self, student_id: int, level: str, subject: str, theme: str,
                 db: LearningDatabase, validator: CurriculumValidator,
                 ollama_evaluator: str = None, ollama_questioner: str = None):
        """Initialize a learning session."""
        self.student_id = student_id
        self.level = level
        self.subject = subject
        self.theme = theme
        self.db = db
        self.validator = validator

        self.session_id = None
        self.question_generator = None
        self.difficulty_adaptor = None
        self.performance_analyzer = PerformanceAnalyzer()

        self.question_count = 0
        self.correct_count = 0
        self.session_start_time = None
        self.question_start_time = None

        # Ollama models (names) for evaluation and questioning
        self.ollama_evaluator = ollama_evaluator
        self.ollama_questioner = ollama_questioner

        self._initialize_session()

    def _initialize_session(self):
        """Initialize session in database and create tools."""
        # Validate curriculum
        if not self.validator.is_valid_theme(self.level, self.subject, self.theme):
            raise ValueError(f"Invalid theme: {self.theme} for {self.level} {self.subject}")

        # Create database session
        self.session_id = self.db.create_session(
            self.student_id, self.level, self.subject, self.theme
        )

        # Initialize difficulty adaptor
        difficulty_profile = self.db.get_difficulty_profile(
            self.student_id, self.level, self.subject
        )
        self.difficulty_adaptor = DifficultyAdaptor(
            self.student_id, self.level, self.subject
        )
        if difficulty_profile:
            self.difficulty_adaptor.current_difficulty = difficulty_profile["current_difficulty"]
        else:
            self.difficulty_adaptor.current_difficulty = 2  # Default to medium

        # Initialize question generator
        self.question_generator = QuestionGenerator(
            self.level, self.subject, self.theme,
            difficulty=self.difficulty_adaptor.current_difficulty,
            validator=self.validator,
            ollama_questioner=self.ollama_questioner
        )

        # Record session start
        self.session_start_time = datetime.now()
        self.db.update_last_active(self.student_id)

    def ask_question(self) -> Dict:
        """Generate and present a question."""
        self.question_start_time = time.time()
        question = self.question_generator.generate_question()

        # Store for later reference
        self.current_question = question

        # Handle type as either enum (from local) or string (from Ollama)
        q_type = question["type"]
        if hasattr(q_type, 'value'):
            q_type = q_type.value
        else:
            q_type = str(q_type)

        return {
            "question_id": question["question_id"],
            "question_text": question["question_text"],
            "type": q_type,
            "difficulty": question["difficulty"],
            "hint_available": True
        }

    def get_hint(self) -> str:
        """Provide hint for current question."""
        if hasattr(self, 'current_question'):
            return self.current_question.get("hint", "Think carefully about the question.")
        return "Ask a question first."

    def submit_answer(self, answer: str) -> Dict:
        """
        Process student's answer.
        Returns feedback and performance metrics.
        """
        if not hasattr(self, 'current_question'):
            return {"error": "No question asked yet"}

        # Calculate response time
        response_time = time.time() - self.question_start_time

        question = self.current_question

        # Basic answer checking (fallback)
        is_correct = self._check_answer(question, answer)

        # Use Ollama model to validate and generate richer feedback where available
        try:
            prompt = (
                f"You are an educational assistant. Evaluate the student's answer.\n"
                f"Level: {self.level}\nSubject: {self.subject}\nTheme: {self.theme}\n"
                f"Question: {question['question_text']}\n"
                f"Expected answer: {question.get('expected_answer','')}\n"
                f"Student answer: {answer}\n"
                f"Respond in JSON with keys: is_correct (true/false), feedback (short), confidence (0-100)."
            )

            model_name = "toto-evaluator"
            resp_text = query_model(prompt, model=model_name)

            # Try to parse JSON from model response
            import re, json
            m = re.search(r"\{.*\}", resp_text, flags=re.S)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                    is_correct = bool(parsed.get("is_correct", is_correct))
                    feedback = parsed.get("feedback", None)
                except Exception:
                    feedback = None
            else:
                # If not JSON, treat model output as feedback text
                feedback = resp_text.strip()
        except Exception:
            # Ollama not available or error; fall back to local check/feedback
            feedback = None

        # Update counters
        self.question_count += 1
        if is_correct:
            self.correct_count += 1

        # Record in database
        self.db.record_response(
            self.session_id,
            question["question_id"],
            question["question_text"],
            question.get("expected_answer", ""),
            answer,
            is_correct,
            question["difficulty"],
            int(response_time)
        )

        # Update progress
        self.db.update_progress(
            self.student_id, self.level, self.subject, self.theme, is_correct
        )

        # Update topic mastery
        topic = self._extract_topic(question)
        self.db.update_topic_mastery(
            self.student_id, self.level, self.subject, topic, is_correct
        )

        # Record performance for adaptive difficulty
        self.difficulty_adaptor.record_performance(is_correct, int(response_time), question["difficulty"])

        # Generate feedback if not provided by model
        if not feedback:
            feedback = self._generate_feedback(is_correct, question, answer)

        # Check if difficulty should be adjusted
        if self.difficulty_adaptor.should_adjust_difficulty():
            new_difficulty = self.difficulty_adaptor.get_recommended_difficulty()
            self.difficulty_adaptor.update_difficulty(self.db, new_difficulty)
            self.question_generator.adjust_difficulty_for_question(new_difficulty)

        return {
            "is_correct": is_correct,
            "feedback": feedback,
            "expected_answer": question.get("expected_answer", ""),
            "response_time": round(response_time, 2),
            "current_accuracy": round(self._calculate_session_accuracy(), 2),
            "difficulty_adjusted": self.difficulty_adaptor.should_adjust_difficulty(),
            "current_difficulty": self.difficulty_adaptor.current_difficulty
        }

    def _check_answer(self, question: Dict, student_answer: str) -> bool:
        """Check if student's answer is correct."""
        expected = str(question.get("expected_answer", "")).strip().lower()
        student = str(student_answer).strip().lower()

        # Exact match
        if student == expected:
            return True

        # Partial matching for word problems
        if len(student) > 0 and len(expected) > 0:
            # Accept if answer contains expected digits
            expected_digits = ''.join(c for c in expected if c.isdigit())
            student_digits = ''.join(c for c in student if c.isdigit())

            if expected_digits and expected_digits == student_digits:
                return True

        return False

    def _extract_topic(self, question: Dict) -> str:
        """Extract topic from question context."""
        return question.get("context", "general")

    def _generate_feedback(self, is_correct: bool, question: Dict, answer: str) -> str:
        """Generate encouraging feedback."""
        if is_correct:
            praise = [
                "Excellent work!",
                "Great job!",
                "That's correct!",
                "Well done!",
                "Perfect!"
            ]
            import random
            return f"{random.choice(praise)} Your understanding of {question['context']} is improving."
        else:
            feedback = f"Not quite right. The correct answer is: {question.get('expected_answer', 'unknown')}. "
            hint = question.get("hint", "")
            if hint:
                feedback += f"\nRemember: {hint}"
            return feedback

    def _calculate_session_accuracy(self) -> float:
        """Calculate accuracy for current session."""
        if self.question_count == 0:
            return 0.0
        return (self.correct_count / self.question_count) * 100

    def end_session(self) -> Dict:
        """End session and return summary."""
        # End session in database
        self.db.end_session(self.session_id)

        # Calculate performance
        accuracy = self._calculate_session_accuracy()
        duration = (datetime.now() - self.session_start_time).total_seconds()

        # Get performance report
        performance_report = self.difficulty_adaptor.get_performance_report()

        # Generate recommendations
        weak_topics = self.db.get_weak_topics(self.student_id, self.level, self.subject)
        recommendations = self.validator.suggest_review_areas(
            self.level, self.subject,
            [t["topic"] for t in weak_topics[:3]]
        )

        summary = {
            "session_id": self.session_id,
            "duration_seconds": duration,
            "questions_answered": self.question_count,
            "correct_answers": self.correct_count,
            "accuracy_percentage": round(accuracy, 2),
            "performance": performance_report,
            "weak_areas": [t["topic"] for t in weak_topics[:3]],
            "recommendations": recommendations,
            "next_suggested_theme": self.validator.get_recommended_next_theme(
                self.level, self.subject, self.theme
            )
        }

        return summary

    def get_session_progress(self) -> Dict:
        """Get current session progress."""
        return {
            "session_id": self.session_id,
            "questions_answered": self.question_count,
            "correct": self.correct_count,
            "accuracy": round(self._calculate_session_accuracy(), 2),
            "current_difficulty": self.difficulty_adaptor.current_difficulty,
            "duration_seconds": (datetime.now() - self.session_start_time).total_seconds()
        }


class LearningEngineController:
    """Main controller for learning sessions."""

    def __init__(self, db_path: str = "data/toto_learning.db",
                 curriculum_dir: str = "data/curriculum",
                 ollama_evaluator: str = None,
                 ollama_questioner: str = None):
        """Initialize learning engine."""
        self.db = LearningDatabase(db_path)
        self.validator = CurriculumValidator(curriculum_dir)
        self.current_session = None
        self.ollama_evaluator = ollama_evaluator
        self.ollama_questioner = ollama_questioner

    def start_learning_session(self, student_id: int, level: str, subject: str, theme: str) -> LearningSession:
        """Start a new learning session."""
        self.current_session = LearningSession(
            student_id, level, subject, theme, self.db, self.validator,
            ollama_evaluator=self.ollama_evaluator,
            ollama_questioner=self.ollama_questioner
        )
        return self.current_session

    def get_student_progress(self, student_id: int, level: str, subject: str) -> Dict:
        """Get student progress for a level and subject."""
        progress_data = self.db.get_progress(student_id, level, subject)
        mastery_data = self.db.get_topic_mastery(student_id, level, subject)

        return {
            "student_id": student_id,
            "level": level,
            "subject": subject,
            "progress": progress_data,
            "topic_mastery": mastery_data,
            "weak_areas": self.db.get_weak_topics(student_id, level, subject)
        }

    def get_curriculum_overview(self, level: str) -> Dict:
        """Get curriculum overview."""
        return self.validator.get_curriculum_summary(level)

    def close(self):
        """Close resources."""
        if self.db:
            self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
