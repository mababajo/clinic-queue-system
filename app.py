from flask import Flask, render_template_string, request, redirect, Response
from datetime import datetime, date

app = Flask(__name__)

# Lists to hold patients and their timestamps
queue = []  # Each item: {"name": str, "time": str, "date": str}
served_history = []  # Each item: {"name": str, "time": str, "date": str}

# Counter for total patients served
total_served = 0

# Dictionary to track daily patient count
daily_count = {}  # key = 'YYYY-MM-DD', value = int

# Homepage showing queue + next patient + total served + daily count + add/remove/reset/search/sort/export/served history/priority/timestamps
@app.route('/')
def home():
    queue_list = "<br>".join([f"{i+1}. {p['name']} (added at {p['time']}) <a href='/remove/{p['name']}'>Remove</a>"
                              for i, p in enumerate(queue)])
    next_patient = f"{queue[0]['name']} (added at {queue[0]['time']})" if queue else "No patients in queue"
    served_list = "<br>".join([f"{p['name']} (added at {p['time']})" for p in served_history]) if served_history else "No patients served yet"
    today = date.today().isoformat()
    today_count = daily_count.get(today, 0)
    
    return render_template_string("""
        <h1>Welcome to the Clinic Queue System</h1>
        <h2>Next Patient: {{ next_patient }}</h2>
        <h2>Current Queue:</h2>
        <p>{{ queue_list|safe }}</p>

        <h3>Today's Patient Count: {{ today_count }}</h3>

        <h3>Add Patient:</h3>
        <form action="/add_form" method="post">
            <input type="text" name="patient_name" placeholder="Patient Name" required>
            <input type="submit" value="Add">
        </form>

        <h3>Add Urgent Patient (Front of Queue):</h3>
        <form action="/add_urgent_form" method="post">
            <input type="text" name="patient_name" placeholder="Patient Name" required>
            <input type="submit" value="Add Urgent">
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

        <h3>Served History:</h3>
        <p>{{ served_list|safe }}</p>

        <h3>Reset Queue:</h3>
        <form action="/reset" method="post">
            <input type="submit" value="Reset Queue">
        </form>
    """, queue_list=queue_list, total_served=total_served, next_patient=next_patient, served_list=served_list, today_count=today_count)

# Helper to add patient and update daily count
def add_patient_to_queue(patient_name, urgent=False):
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S %d-%m-%Y")
    today = now.date().isoformat()
    
    patient = {"name": patient_name, "time": timestamp, "date": today}
    
    if urgent:
        queue.insert(0, patient)
    else:
        queue.append(patient)
    
    # Update daily count
    daily_count[today] = daily_count.get(today, 0) + 1

# Add patient via URL
@app.route('/add/<patient_name>')
def add_patient(patient_name):
    add_patient_to_queue(patient_name)
    return f"Patient {patient_name} added! Current queue length: {len(queue)}"

# Add patient via form
@app.route('/add_form', methods=['POST'])
def add_form():
    patient_name = request.form['patient_name']
    add_patient_to_queue(patient_name)
    return redirect('/')

# Add urgent patient to the front of the queue via form
@app.route('/add_urgent_form', methods=['POST'])
def add_urgent_form():
    patient_name = request.form['patient_name']
    add_patient_to_queue(patient_name, urgent=True)
    return redirect('/')

# Remove patient and mark as served
@app.route('/remove/<patient_name>')
def remove_patient(patient_name):
    global total_served, served_history
    for p in queue:
        if p['name'] == patient_name:
            queue.remove(p)
            total_served += 1
            served_history.append(p)
            return f"Patient {patient_name} removed and marked as served!"
    return f"Patient {patient_name} not found in the queue."

# View full queue
@app.route('/queue')
def view_queue():
    if not queue:
        return "The queue is currently empty."
    return "<br>".join([f"{i+1}. {p['name']} (added at {p['time']})" for i, p in enumerate(queue)])

# Reset the queue
@app.route('/reset', methods=['POST'])
def reset_queue():
    global queue, total_served, served_history, daily_count
    queue = []
    total_served = 0
    served_history = []
    daily_count = {}
    return redirect('/')

# Search for a patient via form
@app.route('/search_form', methods=['POST'])
def search_form():
    patient_name = request.form['patient_name']
    for i, p in enumerate(queue):
        if p['name'] == patient_name:
            position = i + 1
            return f"Patient {patient_name} is in the queue at position {position}, added at {p['time']}."
    return f"Patient {patient_name} is not in the queue."

# Sort the queue alphabetically (based on name)
@app.route('/sort', methods=['POST'])
def sort_queue():
    global queue
    queue.sort(key=lambda x: x['name'])
    return redirect('/')

# Export queue as a text report including timestamps, served history, and daily count
@app.route('/export')
def export_queue():
    report = "Clinic Queue Report\n\n"
    report += "Total Patients Served: " + str(total_served) + "\n\n"
    
    today = date.today().isoformat()
    report += f"Today's Patient Count ({today}): {daily_count.get(today,0)}\n\n"
    
    if queue:
        report += "Current Queue:\n"
        for i, p in enumerate(queue, 1):
            report += f"{i}. {p['name']} (added at {p['time']})\n"
    else:
        report += "The queue is currently empty.\n"
    
    if served_history:
        report += "\nServed Patients History:\n"
        for i, p in enumerate(served_history, 1):
            report += f"{i}. {p['name']} (added at {p['time']})\n"

    return Response(
        report,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=clinic_queue_report.txt"}
    )

if __name__ == '__main__':
    app.run(debug=True)