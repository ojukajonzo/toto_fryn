import os
import json
from typing import Optional, Dict, Any

class Teacher:
    def __init__(self, grade: str, subject: str, curriculum_dir: str = "data/curriculum"):
        self.grade = grade.upper()
        self.subject = subject.lower()
        self.curriculum_dir = curriculum_dir
        self.context = None
        self._load_context()

    def _get_curriculum_path(self) -> str:
        """Return the path to the curriculum JSON file for the current grade and subject."""
        return os.path.join(
            self.curriculum_dir,
            self.grade,
            f"{self.subject}.json"
        )

    def _load_context(self):
        path = self._get_curriculum_path()
        if not os.path.exists(path):
            self.context = None
        else:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.context = json.load(f)
            except Exception as e:
                self.context = None
                print(f"Error loading curriculum file: {e}")

    def set_grade(self, grade: str):
        self.grade = grade.upper()
        self._load_context()

    def set_subject(self, subject: str):
        self.subject = subject.lower()
        self._load_context()

    def get_context(self) -> Optional[Dict[str, Any]]:
        """Return the loaded curriculum context, or None if not available."""
        return self.context

    def get_learning_outcomes(self) -> Optional[list]:
        if self.context and "learning_outcomes" in self.context:
            return self.context["learning_outcomes"]
        return None

    def get_topics(self) -> Optional[list]:
        if self.context and "topics" in self.context:
            return self.context["topics"]
        return None

    def curriculum_exists(self) -> bool:
        return self.context is not None

    def __repr__(self):
        return f"<Teacher grade={self.grade} subject={self.subject} curriculum_exists={self.curriculum_exists()}>"
