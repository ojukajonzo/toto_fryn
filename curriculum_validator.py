"""
Curriculum validator module for Toto Fryn.
Ensures all learning content stays within NCDC Uganda curriculum boundaries.
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from teacher import Teacher


class CurriculumValidator:
    """Validates learning content against NCDC curriculum standards."""

    def __init__(self, curriculum_dir: str = "data/curriculum"):
        """Initialize validator with curriculum structure."""
        self.curriculum_dir = curriculum_dir
        self.curriculum_cache = {}
        self._load_curriculum_structure()

    def _load_curriculum_structure(self):
        """Load all curriculum files into memory for validation."""
        for level in ["P1", "P2", "P3"]:
            self.curriculum_cache[level] = {}
            for subject in ["mathematics", "english"]:
                try:
                    teacher = Teacher(level, subject, self.curriculum_dir)
                    if teacher.curriculum_exists():
                        self.curriculum_cache[level][subject] = teacher.get_context()
                except Exception as e:
                    print(f"Warning: Could not load {level} {subject}: {e}")

    def is_valid_level(self, level: str) -> bool:
        """Check if level exists in curriculum."""
        return level.upper() in self.curriculum_cache

    def is_valid_subject(self, level: str, subject: str) -> bool:
        """Check if subject exists for level."""
        level = level.upper()
        subject = subject.lower()
        return level in self.curriculum_cache and subject in self.curriculum_cache[level]

    def is_valid_theme(self, level: str, subject: str, theme: str) -> bool:
        """Check if theme exists in curriculum."""
        level = level.upper()
        subject = subject.lower()

        if not self.is_valid_subject(level, subject):
            return False

        curriculum = self.curriculum_cache[level][subject]
        if "themes" not in curriculum:
            return False

        theme_names = [t["name"] for t in curriculum["themes"]]
        return theme in theme_names

    def get_curriculum_boundaries(self, level: str, subject: str) -> Dict:
        """Get allowed curriculum boundaries for a level/subject."""
        level = level.upper()
        subject = subject.lower()

        if not self.is_valid_subject(level, subject):
            return {"valid": False, "error": f"Invalid level or subject"}

        curriculum = self.curriculum_cache[level][subject]

        return {
            "valid": True,
            "level": level,
            "subject": subject,
            "themes": [t["name"] for t in curriculum.get("themes", [])],
            "learning_outcomes": curriculum.get("learning_outcomes", []),
            "total_themes": len(curriculum.get("themes", []))
        }

    def get_theme_competences(self, level: str, subject: str, theme: str) -> List[str]:
        """Get competences for a specific theme."""
        level = level.upper()
        subject = subject.lower()

        if not self.is_valid_theme(level, subject, theme):
            return []

        curriculum = self.curriculum_cache[level][subject]
        for t in curriculum.get("themes", []):
            if t["name"] == theme:
                return t.get("competences", [])

        return []

    def validate_content(self, level: str, subject: str, content: str) -> Dict:
        """
        Validate that content/question is within curriculum scope.
        Returns validation result with warnings if content exceeds scope.
        """
        level = level.upper()
        subject = subject.lower()

        result = {
            "is_valid": self.is_valid_subject(level, subject),
            "level": level,
            "subject": subject,
            "warnings": [],
            "recommendations": []
        }

        if not result["is_valid"]:
            result["warnings"].append(f"Invalid level or subject combination")
            return result

        # Check for advanced terminology not in curriculum
        advanced_terms = self._detect_advanced_terms(level, subject, content)
        if advanced_terms:
            result["warnings"].append(f"Content includes terms possibly beyond {level} scope: {advanced_terms}")
            result["recommendations"].append("Simplify content or add explanations")

        return result

    def _detect_advanced_terms(self, level: str, subject: str, content: str) -> List[str]:
        """Detect if content includes terms beyond appropriate level."""
        # Define prohibited advanced terms per level
        prohibited_terms = {
            "P1": {
                "mathematics": ["calculus", "derivative", "integral", "algebra", "quadratic"],
                "english": ["thesis", "seminar", "academic", "philosophical"]
            },
            "P2": {
                "mathematics": ["calculus", "derivative", "integral"],
                "english": ["thesis", "seminar"]
            },
            "P3": {
                "mathematics": ["differential", "integral"],
                "english": ["post-graduate", "thesis"]
            }
        }

        level = level.upper()
        subject = subject.lower()

        if level not in prohibited_terms or subject not in prohibited_terms[level]:
            return []

        content_lower = content.lower()
        found_terms = [
            term for term in prohibited_terms[level][subject]
            if term in content_lower
        ]

        return found_terms

    def get_recommended_next_theme(self, level: str, subject: str, current_theme: str) -> Optional[str]:
        """Suggest next theme in curriculum progression."""
        level = level.upper()
        subject = subject.lower()

        if not self.is_valid_subject(level, subject):
            return None

        curriculum = self.curriculum_cache[level][subject]
        themes = [t["name"] for t in curriculum.get("themes", [])]

        try:
            current_idx = themes.index(current_theme)
            if current_idx + 1 < len(themes):
                return themes[current_idx + 1]
        except (ValueError, IndexError):
            pass

        return None

    def get_all_themes(self, level: str, subject: str) -> List[str]:
        """Get all themes for a level and subject."""
        level = level.upper()
        subject = subject.lower()

        if not self.is_valid_subject(level, subject):
            return []

        curriculum = self.curriculum_cache[level][subject]
        return [t["name"] for t in curriculum.get("themes", [])]

    def get_all_competences(self, level: str, subject: str) -> List[str]:
        """Get all competences for a level and subject."""
        level = level.upper()
        subject = subject.lower()

        if not self.is_valid_subject(level, subject):
            return []

        curriculum = self.curriculum_cache[level][subject]
        return curriculum.get("learning_outcomes", [])

    def validate_student_learning_path(self, level: str, subject: str, themes_completed: List[str]) -> Dict:
        """Validate that student is following approved curriculum path."""
        level = level.upper()
        subject = subject.lower()

        all_themes = self.get_all_themes(level, subject)

        result = {
            "valid_path": True,
            "themes_on_track": themes_completed,
            "themes_pending": all_themes[len(themes_completed):],
            "progress_percentage": round(100 * len(themes_completed) / len(all_themes), 2) if all_themes else 0,
            "warnings": []
        }

        # Check if themes are in order
        for i, theme in enumerate(themes_completed):
            if i < len(all_themes) and theme != all_themes[i]:
                result["valid_path"] = False
                result["warnings"].append(f"Theme order incorrect at position {i}")

        return result

    def suggest_review_areas(self, level: str, subject: str, weak_topics: List[str]) -> List[str]:
        """Suggest curriculum areas to review based on weak topics."""
        level = level.upper()
        subject = subject.lower()

        suggestions = []
        for theme in self.get_all_themes(level, subject):
            competences = self.get_theme_competences(level, subject, theme)
            relevant = [c for c in competences if any(topic in c.lower() for topic in weak_topics)]
            if relevant:
                suggestions.append(f"Review {theme}: {', '.join(relevant[:2])}")

        return suggestions[:5]  # Return top 5 suggestions

    def get_curriculum_summary(self, level: str) -> Dict:
        """Get summary of curriculum for a level."""
        level = level.upper()

        if level not in self.curriculum_cache:
            return {"valid": False, "error": f"Level {level} not found"}

        summary = {
            "level": level,
            "subjects": {},
            "total_themes": 0
        }

        for subject, curriculum in self.curriculum_cache[level].items():
            themes = curriculum.get("themes", [])
            summary["subjects"][subject] = {
                "themes": len(themes),
                "theme_names": [t["name"] for t in themes],
                "competences": len(curriculum.get("learning_outcomes", []))
            }
            summary["total_themes"] += len(themes)

        return summary
