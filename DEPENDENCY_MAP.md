# Toto Fryn - File Dependency and Usage Map

## Entry Point: `toto_main.py` (Primary)

When you call `python3 toto_main.py`, this file is executed and orchestrates the entire system.

---

## File Dependencies Chart

### `toto_main.py` (MAIN ENTRY POINT)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** User runs `python3 toto_main.py`

**Uses these files:**
- `teacher.py` → `Teacher` class (loads curriculum data)
- `database.py` → `LearningDatabase` class (manages student data, progress, sessions)
- `curriculum_validator.py` → `CurriculumValidator` class (validates curriculum themes and competences)
- `learning_engine.py` → `LearningEngineController, LearningSession` (manages learning sessions and questions)
- `analytics.py` → `ProgressAnalytics` class (generates dashboards and reports)
- `difficulty_adaptor.py` → `DifficultyAdaptor` class (adjusts difficulty based on performance)
- `ollama_client.py` → `test_model()` function (tests Ollama model availability for CLI commands)

**Key functions in toto_main.py:**
- `TotoFryn` class: Main orchestrator
  - `create_student()` - Creates new students
  - `load_student()` - Loads existing students
  - `start_learning()` - Initiates learning session
  - `ask_question()` - Gets next question
  - `submit_answer()` - Submits and evaluates answer
  - `show_dashboard()` - Displays progress dashboard
  - `end_session()` - Ends session and shows summary
- `interactive_learning_mode()` - Interactive CLI loop for students
- CLI handlers: `dashboard`, `curriculum`, `model-check`

---

### `learning_engine.py` (CORE LOGIC)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** `toto_main.py`

**Uses these files:**
- `database.py` → `LearningDatabase` (stores responses, progress, difficulty profiles)
- `curriculum_validator.py` → `CurriculumValidator` (validates curriculum content)
- `question_generator.py` → `QuestionGenerator` (generates questions)
- `difficulty_adaptor.py` → `DifficultyAdaptor, PerformanceAnalyzer` (analyzes performance, adjusts difficulty)
- `ollama_client.py` → `query_model()` (evaluates student answers using Ollama)

**Key classes and functions:**
- `LearningSession` class: Manages single learning session
  - `ask_question()` - Generates and returns a question
  - `submit_answer()` - Processes answer, evaluates with Ollama, records feedback
  - `get_hint()` - Returns hint for current question
  - `end_session()` - Finalizes session, generates summary
- `LearningEngineController` class: Controller for sessions
  - `start_learning_session()` - Creates new learning session
  - `get_student_progress()` - Retrieves progress data
  - `get_curriculum_overview()` - Gets curriculum structure

---

### `question_generator.py` (QUESTION CREATION)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** `learning_engine.py` → `LearningSession.ask_question()`

**Uses these files:**
- `ollama_client.py` → `query_model()` (generates questions via Ollama LLM with fallback to local templates)
- Needs: `curriculum_validator.py` (passed as `validator` parameter to access learning outcomes)

**Key classes and functions:**
- `QuestionGenerator` class:
  - `generate_question()` - Main method; tries Ollama first, falls back to local templates
    - Calls `query_model()` for Ollama-based generation
    - Caches Ollama results to reduce repeated API calls
    - Falls back to local template generator if Ollama fails
  - `_get_math_questions()` - Local math templates
  - `_get_english_questions()` - Local English templates
  - `_fill_template()` - Fills template with random values
  - `_generate_math_values()` / `_generate_english_values()` - Generates question values
  - `adjust_difficulty_for_question()` - Changes difficulty level

**Workflow in generate_question():**
1. Checks cache for previously generated questions
2. Tries Ollama: sends prompt with level, subject, theme, learning outcomes
3. If Ollama succeeds: parses JSON response, caches extra questions, returns first question
4. If Ollama fails: prints `[Ollama question generation failed — using local generator]`, uses local templates
5. On normal operation: prints `[Using local question generator]`

---

### `database.py` (DATA PERSISTENCE)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** `toto_main.py`, `learning_engine.py`, `analytics.py`

**Uses:** Standard library only (sqlite3, os, datetime)

**Key classes and functions:**
- `LearningDatabase` class:
  - `add_student()` - Creates new student
  - `get_student()` - Retrieves student by ID
  - `create_session()` - Starts new session
  - `record_response()` - Stores question/answer record
  - `update_progress()` - Updates theme-level progress
  - `update_topic_mastery()` - Updates topic mastery percentage
  - `get_progress()` - Retrieves progress data
  - `get_topic_mastery()` - Gets mastery data
  - `get_weak_topics()` - Identifies topics below threshold
  - `update_difficulty_level()` - Updates difficulty profile
  - `get_difficulty_profile()` - Retrieves difficulty settings

**Database tables:**
- `students` - Student profiles
- `sessions` - Learning sessions
- `responses` - Q&A records
- `progress` - Theme-level progress
- `topic_mastery` - Topic-specific mastery
- `difficulty_profile` - Difficulty history
- `recommendations` - Auto-generated suggestions

---

### `curriculum_validator.py` (CONTENT VALIDATION)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** `toto_main.py`, `learning_engine.py`, `question_generator.py`

**Uses these files:**
- `teacher.py` → `Teacher` class (loads curriculum JSON data)
- Standard library: json, os, typing

**Key classes and functions:**
- `CurriculumValidator` class:
  - `is_valid_level()` - Checks if level (P1/P2/P3) exists
  - `is_valid_subject()` - Checks if subject (mathematics/english) is valid
  - `is_valid_theme()` - Validates theme exists for level/subject
  - `get_all_themes()` - Returns all themes for level/subject
  - `get_all_competences()` - Returns learning outcomes
  - `get_curriculum_summary()` - Returns curriculum overview
  - `validate_content()` - Validates curriculum boundaries
  - `suggest_review_areas()` - Recommends next topics

**Usage in flow:**
- `toto_main.py` uses it to get available themes for student selection
- `learning_engine.py` uses it to validate student's chosen theme
- `question_generator.py` uses it to get learning outcomes for Ollama context

---

### `analytics.py` (PROGRESS REPORTING)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** `toto_main.py` → `show_dashboard()`

**Uses these files:**
- `database.py` → `LearningDatabase` (retrieves progress data)
- Standard library: typing, datetime

**Key classes and functions:**
- `ProgressAnalytics` class:
  - `get_student_dashboard()` - Student overview with accuracy and progress
  - `get_subject_analysis()` - Subject-level analytics
  - `get_learning_trends()` - Progress trends over time
  - `get_parent_report()` - Parent-friendly report
  - `get_teacher_insights()` - Teacher recommendations
  - `_identify_strengths()` - Detects strong topics
  - `_identify_improvements()` - Detects weak topics
  - `_suggest_activities()` - Recommends next steps

---

### `difficulty_adaptor.py` (ADAPTIVE ALGORITHM)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** `learning_engine.py` (during session)

**Uses:** Standard library only (typing, datetime)

**Key classes and functions:**
- `DifficultyAdaptor` class:
  - `record_performance()` - Logs correctness, response time, difficulty
  - `get_recommended_difficulty()` - Returns difficulty level 1-5
  - `should_adjust_difficulty()` - Checks if threshold crossed
  - `update_difficulty()` - Updates difficulty in database
  - `get_performance_report()` - Generates performance summary
  - **Thresholds:**
    - ≥ 85% accuracy → increase difficulty
    - < 60% accuracy → decrease difficulty
    - 60-85% → maintain difficulty
- `PerformanceAnalyzer` class:
  - `identify_weak_areas()` - Finds topics < 70% mastery
  - `identify_learning_patterns()` - Classifies learning state (struggling, improving, proficient, etc.)
  - `_classify_learning_state()` - Determines student's learning trajectory

---

### `ollama_client.py` (AI MODEL INTEGRATION)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** `question_generator.py`, `learning_engine.py`, `toto_main.py` (for model-check)

**Uses:** External `ollama` Python package

**Key functions:**
- `query_model(prompt, model="llama3.2:1b")` - Sends prompt to Ollama LLM, returns response
  - Used by `question_generator.py` for question generation
  - Used by `learning_engine.py` for answer evaluation
- `test_model(model="llama3.2:1b")` - Quick model availability test
  - Used by `toto_main.py` CLI for `model-check` command

**Current model:** `llama3.2:1b` (configured as default, can be overridden via environment variables)

---

### `teacher.py` (CURRICULUM LOADER)
**Status:** ✅ **ACTIVE & USED**  
**Called by:** `curriculum_validator.py`

**Uses:** Standard library only (os, json, typing)

**Key classes and functions:**
- `Teacher` class:
  - `load_curriculum()` - Loads curriculum JSON files from `data/curriculum/` directory
  - Reads P1, P2, P3 syllabi, mathematics, english, and science JSON files
  - Returns curriculum data as Python dictionaries

---

## Files NOT Used When Calling `toto_main.py`

### `main.py` (OLD LEGACY ENTRY POINT)
**Status:** ❌ **NOT USED**  
**Reason:** This is the old entry point that calls `ears`, `brain`, and `mouth` modules for a speech-based interface.

**When toto_main.py is the entry point:** `main.py` is completely ignored.

**Uses:**
- `ears.py` → `TotoEars` (speech input)
- `brain.py` → `TotoBrain` (old Ollama integration)
- `mouth.py` → `TotoMouth` (speech output)

**Note:** `brain.py` is NOT imported by `toto_main.py`; instead, Ollama is accessed via `ollama_client.py`.

---

### `ears.py`, `brain.py`, `mouth.py` (OLD LEGACY MODULES)
**Status:** ❌ **NOT USED** (when using toto_main.py)

- `ears.py` - Old speech recognition module (only used by `main.py`)
- `brain.py` - Old Ollama interface (superseded by `ollama_client.py`)
- `mouth.py` - Text-to-speech module (TTS is optional in toto_main.py; imported but not required)

**Note:** `toto_main.py` tries to import `mouth.py` in the `_speak()` method but gracefully handles if it's missing.

---

## Call Flow Diagram

When user runs: `python3 toto_main.py`

```
toto_main.py (ENTRY POINT)
│
├─→ TotoFryn.__init__()
│   ├─→ database.py (LearningDatabase)
│   ├─→ curriculum_validator.py (CurriculumValidator)
│   │   └─→ teacher.py (Teacher.load_curriculum)
│   ├─→ learning_engine.py (LearningEngineController)
│   └─→ analytics.py (ProgressAnalytics)
│
├─→ interactive_learning_mode()
│   │
│   ├─→ Student input/creation
│   │   └─→ database.py (add_student, get_student)
│   │
│   ├─→ Load student
│   │   └─→ database.py (get_student)
│   │
│   ├─→ Show dashboard
│   │   └─→ analytics.py (get_student_dashboard)
│   │       └─→ database.py (get progress data)
│   │
│   ├─→ Select level/subject
│   │   └─→ curriculum_validator.py (get_all_themes)
│   │
│   ├─→ Start learning session
│   │   └─→ learning_engine.py (start_learning_session)
│   │       └─→ database.py (create_session)
│   │
│   ├─→ Ask question (loop)
│   │   └─→ learning_engine.py (ask_question)
│   │       └─→ question_generator.py (generate_question)
│   │           ├─→ ollama_client.py (query_model) [Ollama generation]
│   │           │   └─→ Ollama LLM (llama3.2:1b)
│   │           └─→ [LOCAL FALLBACK if Ollama fails]
│   │
│   ├─→ Submit answer
│   │   └─→ learning_engine.py (submit_answer)
│   │       ├─→ Local answer check
│   │       ├─→ ollama_client.py (query_model) [Ollama evaluation]
│   │       │   └─→ Ollama LLM (llama3.2:1b)
│   │       ├─→ database.py (record_response, update_progress, update_topic_mastery)
│   │       ├─→ difficulty_adaptor.py (record_performance, adjust difficulty)
│   │       └─→ database.py (update_difficulty_level)
│   │
│   └─→ End session
│       └─→ learning_engine.py (end_session)
│           ├─→ database.py (end_session, get_progress, get_weak_topics)
│           └─→ difficulty_adaptor.py (get_performance_report)
│
└─→ CLI Commands (if args provided)
    ├─→ dashboard: Show student dashboard
    ├─→ curriculum: Show curriculum overview
    └─→ model-check: Test Ollama model availability
        └─→ ollama_client.py (test_model)
```

---

## Summary Table

| File | Status | Used By | Function |
|------|--------|---------|----------|
| `toto_main.py` | ✅ ACTIVE | User | Main entry point, orchestration |
| `learning_engine.py` | ✅ ACTIVE | toto_main | Session management, Q&A orchestration |
| `question_generator.py` | ✅ ACTIVE | learning_engine | Question generation (Ollama + local) |
| `database.py` | ✅ ACTIVE | toto_main, learning_engine, analytics | Data persistence |
| `curriculum_validator.py` | ✅ ACTIVE | toto_main, learning_engine, question_generator | Curriculum validation |
| `analytics.py` | ✅ ACTIVE | toto_main | Progress reporting |
| `difficulty_adaptor.py` | ✅ ACTIVE | learning_engine | Adaptive difficulty |
| `ollama_client.py` | ✅ ACTIVE | question_generator, learning_engine | Ollama LLM calls |
| `teacher.py` | ✅ ACTIVE | curriculum_validator | Curriculum loading |
| `main.py` | ❌ NOT USED | — | Old entry point (legacy) |
| `ears.py` | ❌ NOT USED | — | Old speech input (legacy) |
| `brain.py` | ❌ NOT USED | — | Old Ollama interface (legacy) |
| `mouth.py` | ⚠️ OPTIONAL | toto_main (optional TTS) | Text-to-speech (optional) |

---

## Key Points

1. **`toto_main.py` is the ONLY active entry point** when you run the tutoring system.
2. **`main.py` is legacy** and not used by toto_main.py; it's a separate old interface.
3. **`brain.py` is superseded** by `ollama_client.py` for Ollama interactions.
4. **`ears.py` is not used** — student input comes from keyboard interactive prompts in toto_main.py.
5. **`mouth.py` is optional** — TTS is attempted but gracefully skipped if module missing.
6. **All 8 core modules are active and required:**
   - toto_main.py (orchestration)
   - learning_engine.py (session logic)
   - question_generator.py (questions)
   - database.py (storage)
   - curriculum_validator.py (validation)
   - analytics.py (reporting)
   - difficulty_adaptor.py (adaptation)
   - ollama_client.py (AI model)
   - teacher.py (curriculum loading)
