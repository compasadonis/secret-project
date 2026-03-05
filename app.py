from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import json, os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Load lessons and quizzes from JSON file
DATA_FILE = os.path.join(app.root_path, 'data', 'lessons.json')
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    LESSONS = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', lessons=LESSONS)

@app.route('/lesson/<lesson_id>')
def lesson(lesson_id):
    lesson = next((l for l in LESSONS if l['id']==lesson_id), None)
    if not lesson:
        return redirect(url_for('index'))
    return render_template('lesson.html', lesson=lesson)

@app.route('/quiz/<lesson_id>')
def quiz(lesson_id):
    lesson = next((l for l in LESSONS if l['id']==lesson_id), None)
    if not lesson:
        return redirect(url_for('index'))
    return render_template('quiz.html', lesson=lesson)

@app.route('/submit-quiz/<lesson_id>', methods=['POST'])
def submit_quiz(lesson_id):
    data = request.json
    answers = data.get('answers', {})
    lesson = next((l for l in LESSONS if l['id']==lesson_id), None)
    if not lesson:
        return jsonify({'error':'lesson not found'}), 404
    score = 0
    total = len(lesson.get('quiz', []))
    feedback = []
    for q in lesson.get('quiz', []):
        qid = str(q['id'])
        user_ans = answers.get(qid, '')
        correct = q['answer']
        if user_ans == correct:
            score += 1
            feedback.append({'id': qid, 'correct': True, 'correct_answer': correct})
        else:
            feedback.append({'id': qid, 'correct': False, 'correct_answer': correct})
    return jsonify({'score': score, 'total': total, 'feedback': feedback})

# Enhanced chatbot endpoint with suggested questions
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    q = data.get('message','').lower()

    # Default suggestions for user
    suggestions = ['Climate change', 'Causes', 'Effects', 'Mitigation', 'Adaptation', 'Quiz']

    # Simple rule-based responses
    if any(w in q for w in ['climate', 'change', 'global warming']):
        resp = ("Climate change refers to long-term shifts in temperatures and weather patterns, "
                "caused by natural processes and human activities.")
    elif any(w in q for w in ['greenhouse', 'co2', 'methane']):
        resp = ("Greenhouse gases like CO2 and methane trap heat in the atmosphere, causing warming.")
    elif any(w in q for w in ['causes', 'reason', 'why']):
        resp = ("Major human causes of global warming include burning fossil fuels, deforestation, "
                "and intensive agriculture.")
    elif any(w in q for w in ['effects', 'impact', 'consequence']):
        resp = ("Effects include rising sea levels, stronger storms, heatwaves, and threats to food supply.")
    elif any(w in q for w in ['mitigation', 'reduce', 'reduce emissions']):
        resp = ("Mitigation means reducing greenhouse gases — e.g., using renewable energy, "
                "planting trees, and improving energy efficiency.")
    elif any(w in q for w in ['adapt', 'adaptation']):
        resp = ("Adaptation means adjusting to the impacts of climate change — "
                "like building flood defenses, early warning systems, and diversifying crops.")
    elif 'quiz' in q:
        resp = ("Each lesson has a short quiz — go to a lesson page and click 'Take Quiz'.")
    elif 'hello' in q or 'hi' in q:
        resp = "Hi! I'm EcoBot — your climate guide."
    elif any(w in q for w in ['thanks', 'thank you']):
        resp = "You're welcome! I'm here to help with climate topics and lessons."
    else:
        resp = "Sorry, I don't understand that yet."

    # Return reply + suggestions for frontend
    return jsonify({'reply': resp, 'suggestions': suggestions})

# Serve static files
@app.route('/static/<path:path>')
def static_proxy(path):
    return send_from_directory(os.path.join(app.root_path, 'static'), path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)