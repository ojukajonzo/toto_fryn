# Toto Fryn - Adaptive Learning System

## Overview

Toto Fryn is a modular, adaptive learning system designed for primary school children in Uganda. It delivers **curriculum-aligned lessons** that automatically **adjust difficulty** based on performance, **tracks progress**, and provides **interactive feedback**.

### Key Features

✅ **NCDC Curriculum Compliance** - All content restricted to Uganda Primary Curriculum (P1-P3)  
✅ **Adaptive Difficulty** - Questions automatically adjust based on student performance  
✅ **Interactive Learning** - Questions, hints, and encouraging feedback  
✅ **Progress Tracking** - SQLite database tracks all performance metrics  
✅ **Offline Capable** - Fully functional without internet connection  
✅ **Modular Architecture** - Easy to extend and maintain  
✅ **Text-to-Speech** - Integration with audio feedback  

## Architecture

### Modular Components

```
toto_main.py              # Main orchestration and interactive interface
├── database.py           # SQLite database management
├── curriculum_validator.py # NCDC compliance and curriculum boundaries
├── learning_engine.py    # Core learning session management
├── question_generator.py # Curriculum-aligned question creation
├── difficulty_adaptor.py # Adaptive difficulty algorithm
├── analytics.py          # Progress tracking and reporting
├── teacher.py            # Curriculum data loader
└── mouth.py              # Text-to-speech output
```

### Database Schema

The system uses SQLite with 7 main tables:

- **students** - Student profiles and metadata
- **sessions** - Learning session records
- **responses** - Individual question responses with timing
- **progress** - Theme-level progress tracking
- **topic_mastery** - Topic-specific mastery percentages
- **difficulty_profile** - Current and historical difficulty levels
- **recommendations** - Generated learning recommendations

## Installation

### Requirements
- Python 3.7+
- Dependencies in `requirements.txt`

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create initial database
python3 -c "from database import LearningDatabase; db = LearningDatabase(); db.close()"

# Verify curriculum files
python3 -c "from curriculum_validator import CurriculumValidator; cv = CurriculumValidator(); print(cv.get_curriculum_summary('P1'))"
```

## Usage

### Interactive Mode (Default)

```bash
python3 toto_main.py
```

This launches the interactive learning interface where:
1. Enter student information or load existing student
2. Select learning level (P1, P2, P3)
3. Choose subject (Mathematics, English)
4. Select theme from curriculum
5. Answer questions interactively
6. Get adaptive feedback and recommendations

### Programmatic Usage

```python
from toto_main import TotoFryn

# Initialize system
with TotoFryn() as toto:
    # Create student
    student_id = toto.create_student("Akello", "P2")
    
    # Load student
    toto.load_student(student_id)
    
    # Start learning session
    session = toto.start_learning("P2", "mathematics", "Our School and Neighbourhood")
    
    # Ask questions
    question = toto.ask_question()
    print(question["question_text"])
    
    # Submit answer
    result = toto.submit_answer("15")
    print(f"Correct: {result['is_correct']}")
    print(f"Accuracy: {result['current_accuracy']}%")
    
    # View progress
    progress = toto.get_student_progress("P2", "mathematics")
    
    # End session
    summary = toto.end_session()
    print(summary)
```

### Command-Line Interface

```bash
# Show student dashboard
python3 toto_main.py dashboard 1

# Show curriculum overview
python3 toto_main.py curriculum
```

## How It Works

### 1. Curriculum Compliance (curriculum_validator.py)

The system validates all learning content against the NCDC Uganda Curriculum:

- **Boundaries**: Ensures questions stay within P1-P3 scope
- **Content Validation**: Detects and prevents advanced terminology
- **Theme Progression**: Maintains curriculum sequence
- **Competence Mapping**: Links questions to curriculum competences

```python
validator = CurriculumValidator()
validator.is_valid_theme("P2", "mathematics", "Our School and Neighbourhood")
validator.get_theme_competences("P2", "mathematics", "Our School and Neighbourhood")
```

### 2. Question Generation (question_generator.py)

Questions are generated from templates with curriculum context:

- **Template-Based**: Reusable question structures
- **Difficulty Scaling**: Different number ranges and complexity by level
- **Context-Aware**: Questions relate to curriculum themes and local context
- **Hint Integration**: Built-in hints based on question type

```python
generator = QuestionGenerator("P2", "mathematics", "Food and Nutrition", difficulty=2)
question = generator.generate_question()
# Returns: question_text, type, difficulty, hint, expected_answer
```

### 3. Adaptive Difficulty (difficulty_adaptor.py)

The system monitors performance and adjusts difficulty dynamically:

**Performance Thresholds:**
- Accuracy ≥ 85% → Increase difficulty
- Accuracy < 60% → Decrease difficulty
- 60-85% → Maintain difficulty

**Metrics Tracked:**
- Recent accuracy (last 10 questions)
- Average response time
- Consecutive correct/incorrect
- Topic-specific performance

```python
adaptor = DifficultyAdaptor(student_id, "P2", "mathematics")
adaptor.record_performance(is_correct=True, response_time=12, difficulty_level=2)
new_difficulty = adaptor.get_recommended_difficulty()
adaptor.update_difficulty(db, new_difficulty)
```

### 4. Progress Tracking (database.py)

All learning activity is recorded:

**Recorded Data:**
- Individual question responses with correctness and timing
- Session summaries (duration, accuracy, questions answered)
- Theme-level progress (attempts, accuracy, mastery status)
- Topic-specific mastery percentages
- Difficulty level changes over time

```python
db = LearningDatabase()
db.record_response(session_id, question_id, answer, is_correct, difficulty, response_time)
db.update_progress(student_id, level, subject, theme, is_correct)
db.get_topic_mastery(student_id, level, subject)
```

### 5. Learning Sessions (learning_engine.py)

Interactive sessions manage the question-answer cycle:

- **Session Creation**: Records start time and context
- **Question Asking**: Generates and presents questions
- **Answer Processing**: Checks correctness and timing
- **Feedback Generation**: Provides encouraging feedback
- **Dynamic Adjustment**: Updates difficulty in real-time
- **Session Closure**: Calculates metrics and recommendations

```python
session = LearningSession(student_id, level, subject, theme, db, validator)
question = session.ask_question()
result = session.submit_answer("15")
summary = session.end_session()
```

### 6. Analytics and Reporting (analytics.py)

Comprehensive progress analytics for teachers and parents:

**Dashboard Includes:**
- Overall accuracy and mastery level
- Progress by level and subject
- Weak and strong areas
- Learning trends
- Specific recommendations

**Reports Available:**
- Student dashboard (comprehensive overview)
- Subject analysis (detailed by subject)
- Parent report (simple, actionable language)
- Learning trends (progress over time)

```python
analytics = ProgressAnalytics(db)
dashboard = analytics.get_student_dashboard(student_id)
parent_report = analytics.get_parent_report(student_id)
weak_areas = analytics.get_subject_analysis(student_id, "P2", "mathematics")
```

## Curriculum Structure

### Levels and Subjects

- **P1 (Primary 1)**: Foundation level
  - Mathematics: Counting, basic arithmetic, shapes
  - English: Alphabet, phonics, simple reading

- **P2 (Primary 2)**: Development level
  - Mathematics: Numbers to 100, addition/subtraction, measurement
  - English: Sentence formation, reading comprehension, writing

- **P3 (Primary 3)**: Bridge level
  - Mathematics: Multiplication, division, fractions, data
  - English: Advanced literacy, varied text types, academic writing

### Themes (12 per Level)

Each level includes 12 integrated themes connecting multiple subjects:

**P2 Examples:**
1. Our School and Neighbourhood
2. Our Home and Community
3. The Human Body and Health
4. Food and Nutrition
5. Transport in Our Community
6. Things We Make
7. Accidents and Safety
8. Work and Livelihoods
9. Child Protection
10. Animals and Plants
11. Time and Seasons
12. Water and Cleanliness

## Configuration

### Database Path
```python
toto = TotoFryn(db_path="data/toto_learning.db")
```

### Curriculum Directory
```python
toto = TotoFryn(curriculum_dir="data/curriculum")
```

### Text-to-Speech
```python
toto = TotoFryn(tts_enabled=True)  # Enable audio feedback
```

## Extending the System

### Adding New Question Templates

Edit `question_generator.py`:

```python
def _get_custom_questions(self) -> List[Dict]:
    return [
        {
            "difficulty": 2,
            "type": QuestionType.MULTIPLE_CHOICE,
            "template": "Your custom question template...",
            "context": "your_topic"
        }
    ]
```

### Adding New Analytics Reports

Edit `analytics.py`:

```python
def get_custom_report(self, student_id: int) -> Dict:
    # Implement your custom report logic
    return { ... }
```

### Customizing Difficulty Thresholds

Edit `difficulty_adaptor.py`:

```python
ACCURACY_THRESHOLD_UP = 85.0      # Change to adjust progression
ACCURACY_THRESHOLD_DOWN = 60.0    # Change to adjust regression
```

## Performance Monitoring

The system automatically tracks:

- **Accuracy Metrics**: Percentage of correct answers
- **Speed Metrics**: Average response time (seconds)
- **Mastery Status**: Beginner → Developing → Proficient → Advanced
- **Learning Velocity**: Rate of improvement over time
- **Weak Areas**: Topics with accuracy < 70%

## Troubleshooting

### Database Not Found
```
Error: sqlite3.DatabaseError: database disk image is malformed
Solution: Delete data/toto_learning.db and run setup again
```

### Curriculum Files Not Found
```
Error: CurriculumValidator unable to load curriculum
Solution: Ensure data/curriculum/ folder exists with P1, P2, P3 subdirectories
```

### Import Errors
```
Error: ModuleNotFoundError: No module named 'vosk'
Solution: Run pip install -r requirements.txt
```

## Development Roadmap

- [ ] Collaborative learning (peer-to-peer)
- [ ] Gamification (badges, points, leaderboards)
- [ ] Advanced NLP for open-ended questions
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Teacher dashboard interface
- [ ] Automated lesson planning

## License

© 2026 Toto Fryn Educational System

## Contributing

Contributions welcome! Please ensure:
1. All code follows modular architecture
2. New features tested with curriculum validator
3. Database migrations documented
4. Comments document NCDC alignment

## Support

For issues, questions, or suggestions:
1. Check curriculum files in data/curriculum/
2. Review database schema in database.py
3. Test curriculum_validator for content compliance
4. Enable debug logging for detailed traces

---

**Last Updated**: February 2026  
**Version**: 1.0  
**Status**: Production Ready
