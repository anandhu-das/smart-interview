# 🎓 SmartPrep — AI-Powered Mock Interview System

An AI-powered mock interview system for school students, featuring:
- 🤖 AI answer evaluation (powered by Claude)
- 😊 Facial emotion analysis via webcam
- 🎙️ Voice-to-text speech recognition
- 📊 Detailed performance reports
- 📚 5 subjects: Maths, Science, English, History, Sports

---

## 🚀 Setup Instructions

### Step 1 — Install Python
Make sure Python 3.9+ is installed: https://www.python.org/downloads/

### Step 2 — Install dependencies
Open a terminal/command prompt in this folder and run:
```
pip install -r requirements.txt
```

### Step 3 — Get your Anthropic API Key
1. Go to https://console.anthropic.com/
2. Sign up / log in
3. Click "API Keys" → "Create Key"
4. Copy your key

### Step 4 — Set your API key

**On Windows (Command Prompt):**
```
set ANTHROPIC_API_KEY=your-key-here
```

**On Mac/Linux (Terminal):**
```
export ANTHROPIC_API_KEY=your-key-here
```

### Step 5 — Run the app
```
python app.py
```

### Step 6 — Open your browser
Go to: **http://localhost:5000**

---

## 📁 Project Structure
```
mock_interview/
├── app.py              ← Flask backend (Python)
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
└── templates/
    └── index.html      ← Frontend (HTML/CSS/JS)
```

---

## 🌟 Features

| Feature | Details |
|---------|---------|
| Subjects | Mathematics, Science, Language, History, Sports |
| Questions | 3, 5, or 8 per session |
| Answer Mode | Type or Voice (Chrome browser) |
| AI Feedback | Score /10, Grade, Correct points, Tips, Model answer |
| Webcam | Live feed with emotion bars |
| Report | Full performance dashboard with charts |

---

## 💡 Tips for Students
- Use **Google Chrome** for best voice recognition support
- Allow webcam access when prompted
- Take 5 seconds to think before answering
- Structure answers: explain → give an example

---

## 🛠️ Tech Stack
- **Backend:** Python + Flask
- **AI:** Anthropic Claude (claude-sonnet-4-6)
- **Frontend:** HTML5 + CSS3 + Vanilla JS
- **Voice:** Web Speech API (browser built-in)
- **Webcam:** WebRTC (browser built-in)
