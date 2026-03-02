from flask import Flask, render_template, request, jsonify, session
import os, json, random, base64, re
from datetime import datetime
import anthropic

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── Question Bank ──────────────────────────────────────────────────────────────
QUESTIONS = {
    "Mathematics": [
        "What is the Pythagorean theorem and give a real-life example?",
        "Explain the difference between area and perimeter.",
        "What is a fraction? Give two examples from daily life.",
        "How do you calculate the average of a set of numbers?",
        "What is a prime number? Name five prime numbers.",
        "Explain what percentage means and how you calculate 20% of 150.",
        "What is the order of operations (BODMAS/PEMDAS)?",
        "Describe what a graph is and when we use it.",
    ],
    "Science": [
        "What is photosynthesis and why is it important?",
        "Explain the water cycle in your own words.",
        "What is the difference between a solid, liquid, and gas?",
        "How does the human digestive system work?",
        "What causes day and night on Earth?",
        "What is the food chain? Give an example.",
        "Explain what gravity is and give an example.",
        "What are the planets in our solar system?",
    ],
    "Language & English": [
        "What is the difference between a noun and a verb? Give examples.",
        "Explain what a metaphor is and give an example.",
        "How do you write a good paragraph? What does it need?",
        "What is the difference between 'their', 'there', and 'they're'?",
        "What is a synonym? Give three synonyms for the word 'happy'.",
        "Describe your favourite book in 3-4 sentences.",
        "What is the difference between fiction and non-fiction?",
        "What are punctuation marks and why are they important?",
    ],
    "History": [
        "Who was Mahatma Gandhi and what is he famous for?",
        "What was the significance of the invention of the printing press?",
        "Describe what the Industrial Revolution was.",
        "Who was the first person to walk on the Moon?",
        "What were the main causes of World War I?",
        "Explain what colonialism means.",
        "What is democracy and which country is known as its birthplace?",
        "Who was Nelson Mandela and what did he fight for?",
    ],
    "Sports & Physical Education": [
        "What are the basic rules of cricket?",
        "Why is regular exercise important for our health?",
        "What is the difference between a team sport and an individual sport?",
        "Name three Olympic sports and explain one of them.",
        "What does 'sportsmanship' mean to you?",
        "How many players are on a football (soccer) team?",
        "What are the benefits of playing sports for mental health?",
        "Describe what a marathon is and how long is the race?",
    ],
}

SUBJECTS = list(QUESTIONS.keys())


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", subjects=SUBJECTS)


@app.route("/api/start", methods=["POST"])
def start_interview():
    data = request.json
    subject = data.get("subject", "Mathematics")
    student_name = data.get("name", "Student")
    num_questions = int(data.get("num_questions", 5))

    questions = random.sample(QUESTIONS.get(subject, QUESTIONS["Mathematics"]),
                              min(num_questions, len(QUESTIONS.get(subject, []))))

    session["interview"] = {
        "subject": subject,
        "student_name": student_name,
        "questions": questions,
        "current_index": 0,
        "answers": [],
        "scores": [],
        "emotions": [],
        "start_time": datetime.now().isoformat(),
    }

    return jsonify({
        "status": "started",
        "question": questions[0],
        "question_number": 1,
        "total_questions": len(questions),
        "subject": subject,
    })


@app.route("/api/evaluate", methods=["POST"])
def evaluate_answer():
    data = request.json
    answer_text = data.get("answer", "")
    emotion_data = data.get("emotion", {})

    interview = session.get("interview", {})
    if not interview:
        return jsonify({"error": "No active interview"}), 400

    idx = interview["current_index"]
    question = interview["questions"][idx]
    subject = interview["subject"]

    # ── AI Evaluation ──────────────────────────────────────────────────────────
    prompt = f"""You are a friendly and encouraging school teacher evaluating a student's answer.

Subject: {subject}
Question: {question}
Student's Answer: {answer_text}

Please evaluate the answer and respond ONLY with a JSON object (no markdown, no extra text):
{{
  "score": <integer 0-10>,
  "grade": "<A/B/C/D/F>",
  "correct_points": ["<point1>", "<point2>"],
  "improvement_tips": ["<tip1>", "<tip2>"],
  "model_answer": "<brief ideal answer in 2-3 sentences>",
  "encouragement": "<one warm encouraging sentence for the student>"
}}

Be age-appropriate, supportive, and constructive."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        feedback = json.loads(raw)
    except Exception as e:
        feedback = {
            "score": 5,
            "grade": "C",
            "correct_points": ["Answer received"],
            "improvement_tips": ["Try to add more detail"],
            "model_answer": "Please refer to your textbook for a complete answer.",
            "encouragement": "Keep practising — you're doing great!"
        }

    # ── Save to session ────────────────────────────────────────────────────────
    interview["answers"].append(answer_text)
    interview["scores"].append(feedback.get("score", 5))
    interview["emotions"].append(emotion_data)
    interview["current_index"] += 1
    session["interview"] = interview

    # Next question?
    next_q = None
    if interview["current_index"] < len(interview["questions"]):
        next_q = interview["questions"][interview["current_index"]]

    return jsonify({
        "feedback": feedback,
        "next_question": next_q,
        "question_number": interview["current_index"] + 1,
        "total_questions": len(interview["questions"]),
        "is_last": next_q is None,
    })


@app.route("/api/report", methods=["GET"])
def get_report():
    interview = session.get("interview", {})
    if not interview:
        return jsonify({"error": "No interview data"}), 400

    scores = interview.get("scores", [])
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    emotions = interview.get("emotions", [])

    # Emotion summary
    emotion_counts = {}
    for e in emotions:
        dom = e.get("dominant", "neutral")
        emotion_counts[dom] = emotion_counts.get(dom, 0) + 1

    # Overall grade
    if avg_score >= 9: overall_grade = "A+"
    elif avg_score >= 8: overall_grade = "A"
    elif avg_score >= 7: overall_grade = "B"
    elif avg_score >= 6: overall_grade = "C"
    elif avg_score >= 5: overall_grade = "D"
    else: overall_grade = "F"

    # AI overall feedback
    prompt = f"""You are a caring school teacher writing a brief end-of-interview report for a student.

Student: {interview.get('student_name', 'Student')}
Subject: {interview.get('subject', 'General')}
Average Score: {avg_score}/10
Number of Questions: {len(scores)}
Individual Scores: {scores}

Write a short, encouraging overall performance summary in 3-4 sentences. Be warm, constructive, and motivating. Mention one specific strength and one area to improve."""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        overall_feedback = resp.content[0].text.strip()
    except:
        overall_feedback = f"Well done on completing the interview! Your average score of {avg_score}/10 shows good effort. Keep practising to improve further."

    return jsonify({
        "student_name": interview.get("student_name"),
        "subject": interview.get("subject"),
        "avg_score": avg_score,
        "overall_grade": overall_grade,
        "scores": scores,
        "questions": interview.get("questions", []),
        "answers": interview.get("answers", []),
        "emotion_summary": emotion_counts,
        "overall_feedback": overall_feedback,
        "total_questions": len(scores),
    })


if __name__ == "__main__":
    print("🎓 AI Mock Interview System starting...")
    print("👉 Open http://localhost:5000 in your browser")
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
