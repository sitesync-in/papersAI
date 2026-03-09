import json
from django.conf import settings
from google import genai
from google.genai import types


def generate_paper(board: str, class_name: str, subject: str,
                   difficulty: str = 'balanced', topics: str = '',
                   adhere_marking_scheme: bool = True, preferred_language: str = 'English') -> dict:
    """
    Core Gemini AI paper generation function.
    Returns dict with keys: title, paper_text, answer_key_text, sections
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    difficulty_map = {
        'easy': 'easy and foundational',
        'balanced': 'balanced mix of easy, medium and hard questions',
        'hard': 'challenging and conceptual questions',
    }

    marking_note = (
        "Follow the official Rajasthan State Marking Scheme (2023-24) with sections: "
        "Section A (1 mark MCQs), Section B (2 mark short answers), Section C (3 mark), Section D (5 mark long answers)."
        if adhere_marking_scheme else
        "Use a general question paper format with mixed question types."
    )

    topics_note = f"\nFocus especially on these topics: {topics}." if topics.strip() else ""

    language_note = f"\nCRITICAL INSTRUCTION: You MUST generate the ENTIRE QUESTION PAPER AND ANSWER KEY entirely in {preferred_language}. This includes instructions, section headers, questions, options, and answers. Do NOT use English unless the subject itself is English.\n"

    prompt = f"""You are an expert curriculum designer for {board} board ({class_name}, {subject}).
{language_note}
Generate a complete examination question paper with the following requirements:
- Board: {board}
- Class: {class_name}
- Subject: {subject}
- Difficulty: {difficulty_map.get(difficulty, 'balanced')}
- {marking_note}{topics_note}

Return your response as a valid JSON object with this exact structure:
{{
  "title": "Paper title (e.g., SECONDARY EXAMINATION 2024 - MATHEMATICS)",
  "board": "{board}",
  "class_name": "{class_name}",
  "subject": "{subject}",
  "total_marks": 80,
  "duration": "3 Hours",
  "sections": [
    {{
      "name": "SECTION A",
      "marks_per_question": 1,
      "type": "MCQ",
      "instructions": "Choose the correct option.",
      "questions": [
        {{
          "number": 1,
          "text": "Question text here?",
          "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
          "answer": "A) option1",
          "marks": 1
        }}
      ]
    }},
    {{
      "name": "SECTION B",
      "marks_per_question": 2,
      "type": "Short Answer",
      "instructions": "Answer the following questions in 2-3 sentences.",
      "questions": [
        {{
          "number": 6,
          "text": "Question text here?",
          "answer": "Complete answer here.",
          "marks": 2
        }}
      ]
    }},
    {{
      "name": "SECTION C",
      "marks_per_question": 3,
      "type": "Short Answer",
      "instructions": "Answer the following questions.",
      "questions": [
        {{
          "number": 11,
          "text": "Question text here?",
          "answer": "Complete answer here.",
          "marks": 3
        }}
      ]
    }},
    {{
      "name": "SECTION D",
      "marks_per_question": 5,
      "type": "Long Answer",
      "instructions": "Answer the following questions in detail.",
      "questions": [
        {{
          "number": 16,
          "text": "Question text here?",
          "answer": "Complete detailed answer here.",
          "marks": 5
        }}
      ]
    }}
  ]
}}

Generate exactly 5 MCQs in Section A, 5 short answer questions in Section B, 4 questions in Section C, and 3 long answer questions in Section D. Use real curriculum-appropriate questions for {board} {class_name} {subject}. Return ONLY the JSON, no markdown fences."""

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=4000,
        )
    )

    raw = response.text.strip()
    # Strip markdown fences if present
    if raw.startswith('```'):
        raw = raw.split('\n', 1)[1] if '\n' in raw else raw
        raw = raw.rsplit('```', 1)[0].strip()

    data = json.loads(raw)

    # Build plain-text paper and answer key
    paper_lines = [
        f"{'='*60}",
        f"{data['title']}",
        f"Board: {data['board']}  |  Class: {data['class_name']}  |  Subject: {data['subject']}",
        f"Total Marks: {data['total_marks']}  |  Duration: {data['duration']}",
        f"{'='*60}\n",
    ]
    answer_lines = [
        f"ANSWER KEY — {data['title']}",
        f"{'='*60}\n",
    ]

    for section in data.get('sections', []):
        paper_lines.append(f"\n{section['name']} ({section['marks_per_question']} Mark Each)")
        paper_lines.append(f"Instructions: {section['instructions']}\n")
        answer_lines.append(f"\n{section['name']}")

        for q in section.get('questions', []):
            paper_lines.append(f"Q{q['number']}. {q['text']}")
            if 'options' in q:
                for opt in q['options']:
                    paper_lines.append(f"    {opt}")
            paper_lines.append('')
            answer_lines.append(f"Q{q['number']}. {q['answer']}")

    data['paper_text'] = '\n'.join(paper_lines)
    data['answer_key_text'] = '\n'.join(answer_lines)

    return data
