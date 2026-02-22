# P1 Curriculum - Uganda (NCDC)

## Overview
This folder contains the complete **Primary 1 (P1) Thematic Curriculum** based on Uganda's National Curriculum Development Centre (NCDC) framework. The curriculum is organized around **12 themes** that reflect children's everyday experiences and interests.

## Files Included

### 1. **syllabus.json**
- Overall P1 curriculum structure
- All 12 themes with descriptions
- Learning cycle: Cycle 1 (Basic Skills, P1-P3)
- Curriculum approach and assessment strategy
- Teaching methodology and resources

### 2. **mathematics.json**
- Mathematics competences across all 12 themes
- 7 overall learning outcomes for numeracy
- Theme-specific mathematical competences (sorting, counting, measuring, etc.)
- Teaching methodology using manipulatives and real-world contexts
- Assessment focus on practical demonstrations

### 3. **english.json**
- English (Non-Medium) competences across all 12 themes
- 7 overall learning outcomes for English language
- **IMPORTANT**: English is taught as a subject in P1, NOT the medium of instruction
- For each theme: Listening/Speaking, Pre-Reading, Pre-Writing, Structures, Vocabulary
- Assessment through observation and demonstration

### 4. **literacy.json** & **numeracy.json**
- Legacy files from earlier curriculum setup
- Recommend using **mathematics.json** and **english.json** instead (more comprehensive)

## The 12 Themes

| Theme | Title | Focus |
|-------|-------|-------|
| 1 | Our School | School environment, activities, rules |
| 2 | Our Home | Family, household items, routines |
| 3 | Our Community | Community helpers, services, places |
| 4 | The Human Body and Health | Body parts, hygiene, health practices |
| 5 | Weather | Weather elements, seasons, effects |
| 6 | Accidents and Safety | Hazards, safety rules, prevention |
| 7 | Living Together | Relationships, emotions, cooperation |
| 8 | Food And Nutrition | Food types, nutrition, food safety |
| 9 | Our Transport | Types of transport, safety, uses |
| 10 | Things We Make | Crafts, materials, creation |
| 11 | Our Environment | Plants, animals, conservation |
| 12 | Peace And Security | Peaceful behavior, community safety |

## Key Features of This Curriculum

### **Thematic Approach**
- Learning is organized around themes relevant to children's lives
- All subjects (Mathematics, English, Literacy, Science, Social Studies) are integrated within themes
- Not subject-based divisions

### **Language of Instruction**
- **Medium of Instruction**: Local language / Familiar language
- **English**: Taught as a subject (Non-Medium)
- This prepares children for P4-P7 when English becomes the medium of instruction

### **Competence-Based, Not Objective-Based**
- Focuses on what children can DO (competences) rather than abstract objectives
- Competences emphasize transfer of learning and understanding
- Children demonstrate competences through practical activities, not written tests

### **Teaching Methodology**
- Learner-centered (children as active participants)
- Activity-based with play and games
- Group and pair work
- Use of locally available materials
- Teacher-guided exploration

### **Assessment Approach**
- Continuous informal assessment
- Teacher observation and recording
- Work samples and demonstrations
- Formative assessment during activities
- No written exams in P1

## Mathematics in P1

**Focus**: Concrete, practical number work using manipulatives and real-world contexts from themes

**Key Competences**:
- Sorting and classifying
- Counting and number recognition (to 20)
- One-to-one correspondence
- Matching and sequencing
- Simple addition and subtraction (taking away)
- Shape recognition
- Measurement with non-standard units

**Resources**: Counters, blocks, beads, number cards, shapes, real objects from themes

## English in P1

**Important**: This is **English (Non-Medium)** - English as a subject, not as the language of instruction

**Focus**: Developing listening, speaking, pre-reading, and pre-writing skills in English

**Key Competences**:
- Listening and understanding simple English
- Speaking in short phrases and sentences
- Letter recognition and pre-writing
- Vocabulary from themes
- Simple present tense structures
- Songs, rhymes, and role-plays

**Structures Taught** (across themes):
- "What are you doing?" → "I am...", "We are..."
- "This is a..." / "This is my..."
- "I like...", "I have a..."
- "The... is... (adjective)"

**Resources**: Picture cards, flashcards, story books, songs, role-play props

## Integration with Teacher.py

The curriculum files can be accessed programmatically using the `Teacher` class:

```python
from teacher import Teacher

# Load P1 Mathematics curriculum
teacher = Teacher(grade="P1", subject="mathematics")
math_context = teacher.get_context()

# Access learning outcomes
outcomes = teacher.get_learning_outcomes()

# Access themes
themes = math_context['themes']
for theme in themes:
    print(f"Theme {theme['theme_number']}: {theme['theme_title']}")
    print(f"Competences: {theme['competences']}")
```

## Notes for Teachers

1. **Use the Local Language**: Teaching should happen in the child's home language or a familiar language, not English (except for English lesson itself)

2. **Practical Learning**: Children learn through doing. Use games, songs, stories, and hands-on activities

3. **Integration**: Mathematics and English are taught within theme contexts, not as isolated subjects

4. **Assessment**: Observe and record what children CAN DO, not what they know

5. **Flexibility**: This curriculum is flexible. Adapt activities to local context and children's interests

6. **Continuous Learning**: Learning outcomes are achieved over time through multiple competences. Don't rush

## Sources

- National Curriculum Development Centre (NCDC), Uganda
- "The National Primary School Curriculum for Uganda - Primary 1" (2006)
- Ministry of Education, Science, Technology and Sports (MoESTS)

---

**Curriculum Version**: 2.0 (Updated February 2026)  
**Based on**: Official P1 Curriculum PDF from NCDC  
**Language Policy**: Local language as medium of instruction with English as a subject
