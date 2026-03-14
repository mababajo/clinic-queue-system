from flask import Flask, render_template_string

app = Flask(__name__)

# List to hold patients in the queue
queue = []

@app.route('/')
def home():
    # Simple homepage showing queue message
    return render_template_string("""
        <h1>Welcome to the Clinic Queue System</h1>
        <p>Current queue: {{ queue_length }} patients</p>
    """, queue_length=len(queue))

@app.route('/add/<patient_name>')
def add_patient(patient_name):
    queue.append(patient_name)
    return f"Patient {patient_name} added! Current queue length: {len(queue)}"

@app.route('/queue')
def view_queue():
    if not queue:
        return "The queue is currently empty."
    return "<br>".join([f"{i+1}. {name}" for i, name in enumerate(queue)])
    
if __name__ == '__main__':
    app.run(debug=True)