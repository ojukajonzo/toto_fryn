"""
Adaptive difficulty system for Toto Fryn.
Monitors performance and adjusts question difficulty dynamically.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta


class DifficultyAdaptor:
    """Manages adaptive difficulty based on student performance."""

    # Difficulty levels: 1=Easy, 2=Medium, 3=Hard, 4=Expert, 5=Mastery
    DIFFICULTY_LEVELS = {
        1: {"name": "Easy", "description": "Simple, direct questions"},
        2: {"name": "Medium", "description": "Standard questions with minor complexity"},
        3: {"name": "Hard", "description": "Complex questions requiring reasoning"},
        4: {"name": "Expert", "description": "Advanced problems with multiple steps"},
        5: {"name": "Mastery", "description": "Challenging problems requiring synthesis"}
    }

    MIN_DIFFICULTY = 1
    MAX_DIFFICULTY = 5

    # Performance thresholds
    ACCURACY_THRESHOLD_UP = 85.0  # Increase difficulty if accuracy > 85%
    ACCURACY_THRESHOLD_DOWN = 60.0  # Decrease difficulty if accuracy < 60%
    ACCURACY_THRESHOLD_STABLE = (60.0, 85.0)  # Maintain difficulty

    def __init__(self, student_id: int, level: str, subject: str):
        """Initialize adaptor for a student."""
        self.student_id = student_id
        self.level = level
        self.subject = subject
        self.current_difficulty = 1
        self.performance_history = []

    def record_performance(self, is_correct: bool, response_time_seconds: int, difficulty_level: int):
        """Record student performance metric."""
        self.performance_history.append({
            "timestamp": datetime.now(),
            "is_correct": is_correct,
            "response_time": response_time_seconds,
            "difficulty": difficulty_level
        })

    def calculate_recent_accuracy(self, window_size: int = 10) -> float:
        """Calculate accuracy over recent responses."""
        if not self.performance_history:
            return 0.0

        recent = self.performance_history[-window_size:]
        if not recent:
            return 0.0

        correct = sum(1 for r in recent if r["is_correct"])
        return (correct / len(recent)) * 100

    def calculate_average_response_time(self, window_size: int = 10) -> float:
        """Calculate average response time in seconds."""
        if not self.performance_history:
            return 0.0

        recent = self.performance_history[-window_size:]
        if not recent:
            return 0.0

        total_time = sum(r["response_time"] for r in recent)
        return total_time / len(recent)

    def get_recommended_difficulty(self) -> int:
        """
        Calculate recommended difficulty level based on performance.
        Returns difficulty level (1-5).
        """
        if len(self.performance_history) < 3:
            # Not enough data, suggest starting difficulty
            return self.current_difficulty or 2

        recent_accuracy = self.calculate_recent_accuracy(window_size=10)
        avg_response_time = self.calculate_average_response_time(window_size=10)

        # Performance-based adjustment
        if recent_accuracy >= self.ACCURACY_THRESHOLD_UP:
            # Student is doing well
            if avg_response_time < 15:  # Fast responses indicate mastery
                new_difficulty = min(self.current_difficulty + 1, self.MAX_DIFFICULTY)
            else:
                new_difficulty = self.current_difficulty
        elif recent_accuracy <= self.ACCURACY_THRESHOLD_DOWN:
            # Student is struggling
            new_difficulty = max(self.current_difficulty - 1, self.MIN_DIFFICULTY)
        else:
            # Performance is adequate
            new_difficulty = self.current_difficulty

        return new_difficulty

    def should_adjust_difficulty(self) -> bool:
        """Determine if difficulty should be adjusted."""
        if len(self.performance_history) < 5:
            return False

        recent_accuracy = self.calculate_recent_accuracy(window_size=10)

        # Check if accuracy warrants change
        if recent_accuracy >= self.ACCURACY_THRESHOLD_UP:
            return self.current_difficulty < self.MAX_DIFFICULTY
        elif recent_accuracy <= self.ACCURACY_THRESHOLD_DOWN:
            return self.current_difficulty > self.MIN_DIFFICULTY

        return False

    def update_difficulty(self, db, new_difficulty: Optional[int] = None):
        """Update difficulty in database."""
        if new_difficulty is None:
            new_difficulty = self.get_recommended_difficulty()

        # Clamp to valid range
        new_difficulty = max(self.MIN_DIFFICULTY, min(new_difficulty, self.MAX_DIFFICULTY))

        self.current_difficulty = new_difficulty
        db.update_difficulty_level(self.student_id, self.level, self.subject, new_difficulty)

    def get_performance_report(self) -> Dict:
        """Generate performance report for current session."""
        if not self.performance_history:
            return {
                "accuracy": 0.0,
                "attempts": 0,
                "correct": 0,
                "avg_response_time": 0.0,
                "current_difficulty": self.current_difficulty,
                "recommended_difficulty": self.current_difficulty
            }

        correct = sum(1 for r in self.performance_history if r["is_correct"])
        attempts = len(self.performance_history)
        accuracy = (correct / attempts) * 100 if attempts > 0 else 0.0
        avg_time = sum(r["response_time"] for r in self.performance_history) / attempts

        return {
            "accuracy": round(accuracy, 2),
            "attempts": attempts,
            "correct": correct,
            "incorrect": attempts - correct,
            "avg_response_time": round(avg_time, 2),
            "current_difficulty": self.current_difficulty,
            "current_difficulty_name": self.DIFFICULTY_LEVELS[self.current_difficulty]["name"],
            "recommended_difficulty": self.get_recommended_difficulty(),
            "recommended_difficulty_name": self.DIFFICULTY_LEVELS[self.get_recommended_difficulty()]["name"],
            "should_adjust": self.should_adjust_difficulty()
        }

    def get_difficulty_info(self, difficulty_level: int) -> Dict:
        """Get information about a difficulty level."""
        if difficulty_level not in self.DIFFICULTY_LEVELS:
            return {}

        return {
            "level": difficulty_level,
            "name": self.DIFFICULTY_LEVELS[difficulty_level]["name"],
            "description": self.DIFFICULTY_LEVELS[difficulty_level]["description"]
        }

    def get_all_difficulty_levels(self) -> Dict:
        """Get all available difficulty levels."""
        return self.DIFFICULTY_LEVELS


class PerformanceAnalyzer:
    """Analyzes student performance patterns."""

    def __init__(self):
        """Initialize analyzer."""
        pass

    def identify_weak_areas(self, topic_attempts: List[Dict]) -> List[Dict]:
        """
        Identify weak areas from topic attempts.
        Each attempt dict should have: topic, is_correct, timestamp
        """
        if not topic_attempts:
            return []

        # Group by topic
        topics = {}
        for attempt in topic_attempts:
            topic = attempt.get("topic", "unknown")
            if topic not in topics:
                topics[topic] = {"correct": 0, "total": 0}

            topics[topic]["total"] += 1
            if attempt.get("is_correct"):
                topics[topic]["correct"] += 1

        # Calculate accuracy per topic
        weak_areas = []
        for topic, stats in topics.items():
            accuracy = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            weak_areas.append({
                "topic": topic,
                "accuracy": round(accuracy, 2),
                "attempts": stats["total"],
                "correct": stats["correct"],
                "status": self._get_mastery_status(accuracy)
            })

        # Sort by accuracy (worst first)
        weak_areas.sort(key=lambda x: x["accuracy"])
        return weak_areas

    @staticmethod
    def _get_mastery_status(accuracy: float) -> str:
        """Get mastery status based on accuracy."""
        if accuracy >= 90:
            return "mastered"
        elif accuracy >= 70:
            return "proficient"
        elif accuracy >= 50:
            return "developing"
        else:
            return "beginning"

    def identify_learning_patterns(self, performance_history: List[Dict]) -> Dict:
        """Identify learning patterns from performance history."""
        if not performance_history:
            return {"pattern": "insufficient_data"}

        # Check for improvement trend
        recent_accuracy = self._calculate_window_accuracy(performance_history, window=10)
        overall_accuracy = self._calculate_window_accuracy(performance_history, window=len(performance_history))

        improvement_trend = recent_accuracy - overall_accuracy

        # Check for speed improvement
        recent_times = [r.get("response_time", 0) for r in performance_history[-10:]]
        early_times = [r.get("response_time", 0) for r in performance_history[:10]]

        avg_recent = sum(recent_times) / len(recent_times) if recent_times else 0
        avg_early = sum(early_times) / len(early_times) if early_times else 0

        speed_improvement = avg_early - avg_recent  # Positive = faster

        return {
            "recent_accuracy": round(recent_accuracy, 2),
            "overall_accuracy": round(overall_accuracy, 2),
            "improvement_trend": round(improvement_trend, 2),
            "learning_state": self._classify_learning_state(improvement_trend, recent_accuracy),
            "speed_improvement": round(speed_improvement, 2),
            "total_attempts": len(performance_history)
        }

    @staticmethod
    def _calculate_window_accuracy(history: List[Dict], window: int) -> float:
        """Calculate accuracy within a window of attempts."""
        if not history or window <= 0:
            return 0.0

        window_data = history[-window:] if window >= len(history) else history[-window:]
        correct = sum(1 for r in window_data if r.get("is_correct"))
        return (correct / len(window_data)) * 100 if window_data else 0.0

    @staticmethod
    def _classify_learning_state(improvement_trend: float, recent_accuracy: float) -> str:
        """Classify current learning state."""
        if recent_accuracy < 50:
            return "struggling"
        elif improvement_trend > 10:
            return "rapidly_improving"
        elif improvement_trend > 0:
            return "gradually_improving"
        elif recent_accuracy >= 85:
            return "proficient"
        else:
            return "stable"
