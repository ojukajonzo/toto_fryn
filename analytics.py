"""
Analytics and progress tracking for Toto Fryn.
Provides insights for teachers and parents on student performance.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database import LearningDatabase


class ProgressAnalytics:
    """Analyzes and reports student progress."""

    def __init__(self, db: LearningDatabase):
        """Initialize analytics with database."""
        self.db = db

    def get_student_dashboard(self, student_id: int) -> Dict:
        """Get comprehensive dashboard for a student."""
        student = self.db.get_student(student_id)
        if not student:
            return {"error": "Student not found"}

        return {
            "student_id": student_id,
            "name": student["name"],
            "grade": student["grade"],
            "date_joined": student["date_created"],
            "last_active": student["last_active"],
            "level_progress": self._get_level_progress(student_id),
            "learning_summary": self._get_learning_summary(student_id)
        }

    def _get_level_progress(self, student_id: int) -> Dict:
        """Get progress across all levels."""
        levels = {}
        for level in ["P1", "P2", "P3"]:
            for subject in ["mathematics", "english"]:
                progress = self.db.get_progress(student_id, level, subject)
                if not progress:
                    continue

                total_accuracy = sum(p["accuracy_rate"] for p in progress) / len(progress) if progress else 0
                mastered = sum(1 for p in progress if p["accuracy_rate"] >= 80)

                if level not in levels:
                    levels[level] = {}

                levels[level][subject] = {
                    "total_themes": len(progress),
                    "themes_completed": mastered,
                    "average_accuracy": round(total_accuracy, 2),
                    "progress_percentage": round(100 * mastered / len(progress), 2) if progress else 0
                }

        return levels

    def _get_learning_summary(self, student_id: int) -> Dict:
        """Get overall learning summary."""
        total_accuracy = []
        total_attempts = 0
        total_correct = 0

        for level in ["P1", "P2", "P3"]:
            for subject in ["mathematics", "english"]:
                progress = self.db.get_progress(student_id, level, subject)
                for p in progress:
                    total_attempts += p["total_attempts"]
                    total_correct += p["correct_attempts"]
                    total_accuracy.append(p["accuracy_rate"])

        avg_accuracy = sum(total_accuracy) / len(total_accuracy) if total_accuracy else 0

        return {
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "overall_accuracy": round(avg_accuracy, 2),
            "mastery_level": self._classify_mastery(avg_accuracy)
        }

    @staticmethod
    def _classify_mastery(accuracy: float) -> str:
        """Classify mastery level."""
        if accuracy >= 90:
            return "Advanced"
        elif accuracy >= 75:
            return "Proficient"
        elif accuracy >= 60:
            return "Developing"
        else:
            return "Beginning"

    def get_subject_analysis(self, student_id: int, level: str, subject: str) -> Dict:
        """Get detailed analysis for a subject."""
        progress = self.db.get_progress(student_id, level, subject)
        mastery = self.db.get_topic_mastery(student_id, level, subject)

        if not progress:
            return {"error": "No progress data found"}

        return {
            "student_id": student_id,
            "level": level,
            "subject": subject,
            "themes_progress": progress,
            "topic_mastery": mastery,
            "weak_areas": [t for t in mastery if t["mastery_percentage"] < 70],
            "strong_areas": [t for t in mastery if t["mastery_percentage"] >= 80],
            "average_accuracy": round(sum(p["accuracy_rate"] for p in progress) / len(progress), 2),
            "recommendation": self._generate_recommendation(progress, mastery)
        }

    @staticmethod
    def _generate_recommendation(progress: List[Dict], mastery: List[Dict]) -> str:
        """Generate recommendation based on performance."""
        avg_accuracy = sum(p["accuracy_rate"] for p in progress) / len(progress) if progress else 0

        if avg_accuracy >= 85:
            return "Great progress! Ready to move to next level."
        elif avg_accuracy >= 70:
            return "Good progress. Continue practicing to improve accuracy."
        elif avg_accuracy >= 50:
            return "Needs more practice in weak areas. Consider review sessions."
        else:
            return "Significant support needed. Recommend focused intervention."

    def get_learning_trends(self, student_id: int, days: int = 30) -> Dict:
        """Get learning trends over time."""
        # This would analyze session history over specified period
        return {
            "student_id": student_id,
            "period_days": days,
            "sessions_completed": 0,  # Would query from sessions table
            "total_questions": 0,
            "accuracy_trend": [],  # Time-series data
            "difficulty_progression": [],  # How difficulty changed over time
            "learning_velocity": "N/A"  # Rate of improvement
        }

    def get_teacher_insights(self, class_level: str, subject: str) -> Dict:
        """Get insights for teacher about a class."""
        return {
            "level": class_level,
            "subject": subject,
            "class_average_accuracy": "N/A",
            "struggling_students": [],
            "excelling_students": [],
            "common_weak_areas": [],
            "recommended_interventions": []
        }

    def get_parent_report(self, student_id: int) -> Dict:
        """Generate parent-friendly progress report."""
        student = self.db.get_student(student_id)
        if not student:
            return {"error": "Student not found"}

        dashboard = self.get_student_dashboard(student_id)

        return {
            "student_name": student["name"],
            "grade": student["grade"],
            "report_date": datetime.now().isoformat(),
            "overall_progress": "In Progress",
            "strengths": self._identify_strengths(student_id),
            "areas_for_improvement": self._identify_improvements(student_id),
            "recommended_home_activities": self._suggest_activities(student_id),
            "next_steps": self._suggest_next_steps(student_id)
        }

    def _identify_strengths(self, student_id: int) -> List[str]:
        """Identify student's strengths."""
        strengths = []
        for level in ["P1", "P2", "P3"]:
            for subject in ["mathematics", "english"]:
                mastery = self.db.get_topic_mastery(student_id, level, subject)
                strong = [t for t in mastery if t["mastery_percentage"] >= 85]
                if strong:
                    strengths.extend([f"{t['topic']} ({level} {subject.title()})" for t in strong[:2]])

        return strengths[:5]

    def _identify_improvements(self, student_id: int) -> List[str]:
        """Identify areas for improvement."""
        improvements = []
        for level in ["P1", "P2", "P3"]:
            for subject in ["mathematics", "english"]:
                weak = self.db.get_weak_topics(student_id, level, subject, threshold=60)
                if weak:
                    improvements.extend([f"{t['topic']} ({level} {subject.title()})" for t in weak[:2]])

        return improvements[:5]

    def _suggest_activities(self, student_id: int) -> List[str]:
        """Suggest home learning activities."""
        activities = [
            "Practice counting with objects at home (stones, fruits, toys)",
            "Read simple stories together with family members",
            "Play word games or spelling games",
            "Solve simple math problems using daily items",
            "Create a learning journal to record progress",
            "Practice telling stories in English",
            "Do shape activities with household items"
        ]
        return activities[:5]

    def _suggest_next_steps(self, student_id: int) -> List[str]:
        """Suggest next learning steps."""
        return [
            "Complete remaining themes in current level",
            "Review weak areas identified in progress report",
            "Practice at least 3 times per week for best results",
            "Request feedback from teacher on specific challenges"
        ]

    def export_progress_report(self, student_id: int, format: str = "json") -> str:
        """Export progress report in specified format."""
        report = self.get_student_dashboard(student_id)

        if format == "json":
            import json
            return json.dumps(report, indent=2, default=str)
        elif format == "text":
            return self._format_as_text(report)
        else:
            return str(report)

    @staticmethod
    def _format_as_text(report: Dict) -> str:
        """Format report as plain text."""
        lines = []
        lines.append("=" * 60)
        lines.append("STUDENT PROGRESS REPORT")
        lines.append("=" * 60)

        for key, value in report.items():
            if key not in ["level_progress", "learning_summary"]:
                lines.append(f"{key.replace('_', ' ').title()}: {value}")

        return "\n".join(lines)
