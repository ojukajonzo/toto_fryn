# Toto Fryn - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database (automatic on first run)
python3 toto_main.py
```

### Running Toto Fryn

**Interactive Mode (Recommended):**
```bash
python3 toto_main.py
```

**Command Line:**
```bash
# Show student dashboard
python3 toto_main.py dashboard 1

# Show curriculum overview
python3 toto_main.py curriculum
```

## 📚 The Learning System

### What Toto Fryn Does

1. **Keeps Kids On Track** 
   - All content strictly from Uganda NCDC curriculum
   - Cannot venture beyond P1-P3 scope
   - Questions aligned to curriculum themes

2. **Asks Interactive Questions**
   - Curriculum-based questions
   - Provides hints when needed
   - Gives feedback automatically

3. **Adjusts Difficulty Automatically**
   - Monitors accuracy
   - Increases difficulty if accuracy > 85%
   - Decreases difficulty if accuracy < 60%
   - Maintains difficulty if 60-85%

4. **Tracks Everything**
   - Records every question and answer
   - Calculates accuracy and mastery
   - Identifies weak topics
   - Shows learning trends

5. **Works Offline**
   - No internet needed
   - Everything stored locally
   - Self-contained system

## 🎯 Features

### For Students

- **Interactive Lessons**: Questions + Feedback + Hints
- **Adaptive Learning**: Difficulty matches your level
- **Encouragement**: Audio feedback on performance
- **Clear Progress**: See what you've learned

### For Teachers

- **Student Dashboards**: See who's struggling
- **Progress Reports**: Track learning over time
- **Weak Area Identification**: Know what to review
- **Recommendations**: Suggested interventions

### For Parents

- **Progress Reports**: Simple, actionable language
- **Suggested Activities**: Home learning ideas
- **Performance Trends**: How your child is improving
- **Areas to Focus**: What needs more practice

## 📊 Sample Learning Session

```
1. Start System
   python3 toto_main.py

2. Enter Student Name
   "Akello"
   
3. Select Grade
   "P2"
   
4. Choose Subject
   "mathematics"
   
5. Pick Theme
   "Food and Nutrition"
   
6. Answer Questions
   ❓ How many mangoes do we have if we pick 12 and gather 8 more?
   📝 Your answer: 20
   ✅ Correct! Great job!
   
7. Get Summary
   Questions: 5
   Accuracy: 80%
   Next Topic: Water Conservation
```

## 💾 Database

The system uses SQLite - no setup needed!

**Stored Data:**
- Student profiles
- Learning sessions
- Question responses
- Progress tracking
- Difficulty levels
- Learning recommendations

**Database Location:** `data/toto_learning.db`

## 🔧 Configuration

### Enable/Disable Audio
```python
# In toto_main.py
toto = TotoFryn(tts_enabled=True)   # Audio on
toto = TotoFryn(tts_enabled=False)  # Audio off
```

### Change Difficulty Thresholds
```python
# In difficulty_adaptor.py
ACCURACY_THRESHOLD_UP = 85.0      # When to increase
ACCURACY_THRESHOLD_DOWN = 60.0    # When to decrease
```

### Add More Questions
```python
# In question_generator.py
# Add templates to _get_math_questions() or _get_english_questions()
```

## 📋 Available Themes

### P1 (12 themes)
1. Alphabet and Letters
2. Numbers and Counting
3. Shapes and Sizes
4. My Family
5. My School
6. Food I Eat
7. Animals Around Me
8. Plants and Nature
9. My Community
10. Days and Weather
11. Games and Play
12. Keeping Safe

### P2 (12 themes)
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

### P3 (12 themes)
1. Our Sub-county/Division
2. Livelihood in Our Sub-county/Division
3. Our Environment
4. Environment and Weather
5. Living Things: Animals
6. Living Things: Plants
7. Water and Natural Resources
8. Cultural Heritage
9. Peace, Rights and Responsibilities
10. Energy and Movement
11. Communication and Technology
12. Trade and Commerce

## 🐛 Troubleshooting

### Q: "No module named 'vosk'"
**A:** Run `pip install -r requirements.txt`

### Q: "Database file not found"
**A:** Run `python3 toto_main.py` to create it automatically

### Q: "Curriculum files not found"
**A:** Ensure `data/curriculum/` folder exists with P1, P2, P3 subdirectories

### Q: "Audio not working"
**A:** Install pyttsx3: `pip install pyttsx3`

### Q: How do I see student progress?
**A:** Use `python3 toto_main.py dashboard <student_id>`

## 📖 Documentation

- **SYSTEM_README.md** - Complete system documentation
- **data/curriculum/P*/README.md** - Curriculum details per level
- **Code Comments** - Extensive documentation in source files

## 🎓 Learning Flow

```
Student Starts
     ↓
Load/Create Student Profile
     ↓
Select Level (P1/P2/P3)
     ↓
Select Subject (Mathematics/English)
     ↓
Choose Theme from Curriculum
     ↓
Generate Curriculum-Aligned Question
     ↓
Student Answers
     ↓
Check Correctness
     ↓
Adjust Difficulty if Needed
     ↓
Record Progress
     ↓
Next Question or End Session
     ↓
Generate Summary & Recommendations
```

## 🚀 Next Steps

1. **First Run**: `python3 toto_main.py`
2. **Create Student**: Enter name and grade
3. **Start Learning**: Pick level, subject, and theme
4. **Answer Questions**: 5+ questions per session
5. **Review Progress**: Check dashboard after each session

## 📞 Support

**Common Issues:**
1. Check `data/curriculum/` folder exists
2. Verify Python 3.7+ installed
3. Run `pip install -r requirements.txt`
4. Delete `data/toto_learning.db` to reset (starts fresh)

**System Components:**
- `database.py` - Data storage
- `curriculum_validator.py` - Content boundaries
- `question_generator.py` - Creates questions
- `difficulty_adaptor.py` - Adjusts difficulty
- `learning_engine.py` - Main learning system
- `analytics.py` - Progress reporting
- `toto_main.py` - User interface

---

**Ready to start?**
```bash
python3 toto_main.py
```

Enjoy learning with Toto Fryn! 🎉
