from flask import Flask, render_template_string, request, redirect, Response

app = Flask(__name__)

# List to hold patients
queue = []

# Counter for total patients served
total_served = 0

# Homepage showing queue + next patient + total served + add/remove/reset/search/sort/export
@app.route('/')
def home():
    queue_list = "<br>".join([f"{i+1}. {name} <a href='/remove/{name}'>Remove</a>"
                              for i, name in enumerate(queue)])
    next_patient = queue[0] if queue else "No patients in queue"
    return render_template_string("""
        <h1>Welcome to the Clinic Queue System</h1>
        <h2>Next Patient: {{ next_patient }}</h2>
        <h2>Current Queue:</h2>
        <p>{{ queue_list|safe }}</p>

        <h3>Add Patient:</h3>
        <form action="/add_form" method="post">
            <input type="text" name="patient_name" placeholder="Patient Name" required>
            <input type="submit" value="Add">
        </form>

        <h3>Search Patient:</h3>
        <form action="/search_form" method="post">
            <input type="text" name="patient_name" placeholder="Patient Name" required>
            <input type="submit" value="Search">
        </form>

        <h3>Sort Queue:</h3>
        <form action="/sort" method="post">
            <input type="submit" value="Sort Alphabetically">
        </form>

        <h3>Export Queue / Report:</h3>
        <form action="/export" method="get">
            <input type="submit" value="Download Report">
        </form>

        <h3>Total Patients Served: {{ total_served }}</h3>

        <h3>Reset Queue:</h3>
        <form action="/reset" method="post">
            <input type="submit" value="Reset Queue">
        </form>
    """, queue_list=queue_list, total_served=total_served, next_patient=next_patient)

# Add patient via URL
@app.route('/add/<patient_name>')
def add_patient(patient_name):
    queue.append(patient_name)
    return f"Patient {patient_name} added! Current queue length: {len(queue)}"

# Add patient via form
@app.route('/add_form', methods=['POST'])
def add_form():
    patient_name = request.form['patient_name']
    queue.append(patient_name)
    return redirect('/')

# Remove patient
@app.route('/remove/<patient_name>')
def remove_patient(patient_name):
    global total_served
    if patient_name in queue:
        queue.remove(patient_name)
        total_served += 1
        return f"Patient {patient_name} removed! Current queue length: {len(queue)}"
    return f"Patient {patient_name} not found in the queue."

# View full queue
@app.route('/queue')
def view_queue():
    if not queue:
        return "The queue is currently empty."
    return "<br>".join([f"{i+1}. {name}" for i, name in enumerate(queue)])

# Reset the queue
@app.route('/reset', methods=['POST'])
def reset_queue():
    global queue, total_served
    queue = []
    total_served = 0
    return redirect('/')

# Search for a patient via form
@app.route('/search_form', methods=['POST'])
def search_form():
    patient_name = request.form['patient_name']
    if patient_name in queue:
        position = queue.index(patient_name) + 1
        return f"Patient {patient_name} is in the queue at position {position}."
    return f"Patient {patient_name} is not in the queue."

# Sort the queue alphabetically
@app.route('/sort', methods=['POST'])
def sort_queue():
    global queue
    queue.sort()
    return redirect('/')

# Export queue as a text report
@app.route('/export')
def export_queue():
    report = "Clinic Queue Report\n\n"
    report += "Total Patients Served: " + str(total_served) + "\n\n"
    if queue:
        report += "Current Queue:\n"
        for i, name in enumerate(queue, 1):
            report += f"{i}. {name}\n"
    else:
        report += "The queue is currently empty.\n"
    
    return Response(
        report,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=clinic_queue_report.txt"}
    )

if __name__ == '__main__':
    app.run(debug=True)