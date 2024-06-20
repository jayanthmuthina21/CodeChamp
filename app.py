from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

def load_submissions():
    try:
        with open('submissions.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_submissions(submissions):
    with open('submissions.json', 'w') as file:
        json.dump(submissions, file, indent=4)

def load_questions():
    try:
        with open('questions.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def evaluate_solution(question, solution_code):
    function_name = question['function_name']
    test_cases = question['test_cases']
    local_scope = {}
    try:
        exec(solution_code, {}, local_scope)
        solution_function = local_scope.get(function_name)
        if not solution_function:
            return False
        for test_case in test_cases:
            input_data = test_case['input']
            expected_output = test_case['output']
            if solution_function(*input_data) != expected_output:
                return False
        return True
    except Exception as e:
        print(f"Error evaluating solution: {e}")
        return False

@app.route('/')
def index():
    submissions = load_submissions()
    return render_template('index.html', submissions=submissions)

@app.route('/questions')
def questions():
    questions = load_questions()
    return render_template('questions.html', questions=questions)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        question_id = int(request.form['question_id'])
        solution = request.form['solution']
        questions = load_questions()
        question = next(q for q in questions if q['id'] == question_id)
        is_correct = evaluate_solution(question, solution)
        score = 1 if is_correct else 0
        submission = {'name': name, 'question_id': question_id, 'solution': solution, 'score': score}
        submissions = load_submissions()
        submissions.append(submission)
        save_submissions(submissions)
        return redirect(url_for('index'))
    questions = load_questions()
    return render_template('submit.html', questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
