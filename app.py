from flask import Flask, render_template_string, request
from datetime import datetime
import csv

app = Flask(__name__)

# ====== Data Storage ======
queue = []
served_list = []
total_served = 0

# ====== Helper Functions ======
def add_patient(patient_name, priority=False):
    if priority:
        queue.insert(0, patient_name)
    else:
        queue.append(patient_name)

def remove_patient(patient_name):
    if patient_name in queue:
        queue.remove(patient_name)

def next_patient():
    if queue:
        patient = queue.pop(0)
        served_list.append({'name': patient, 'time': datetime.now()})
        global total_served
        total_served += 1
        return patient
    return "No patients in queue"

def search_patient(name):
    return [p for p in queue if name.lower() in p.lower()]

def sort_queue(reverse=False):
    queue.sort(reverse=reverse)

def reset_queue():
    queue.clear()
    served_list.clear()
    global total_served
    total_served = 0

def export_queue(filename="queue_export.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Patient Name", "Time Served"])
        for patient in served_list:
            writer.writerow([patient['name'], patient['time']])

def average_wait():
    if not served_list:
        return 0
    total_time = sum((datetime.now() - p['time']).total_seconds() for p in served_list)
    return total_time / 60 / len(served_list)  # average in minutes

def daily_count():
    today = datetime.now().date()
    return sum(1 for p in served_list if p['time'].date() == today)

# ====== Routes ======
@app.route('/', methods=['GET', 'POST'])
def home():
    global queue, served_list, total_served
    message = ""
    if request.method == 'POST':
        action = request.form.get('action')
        patient_name = request.form.get('patient_name', '').strip()
        priority_flag = request.form.get('priority') == 'on'

        if action == 'add' and patient_name:
            add_patient(patient_name, priority_flag)
            message = f"Added {patient_name}"
        elif action == 'remove' and patient_name:
            remove_patient(patient_name)
            message = f"Removed {patient_name}"
        elif action == 'next':
            patient = next_patient()
            message = f"Next patient served: {patient}"
        elif action == 'reset':
            reset_queue()
            message = "Queue reset"
        elif action == 'export':
            export_queue()
            message = "Queue exported to CSV"
        elif action == 'sort':
            sort_queue()
            message = "Queue sorted"

    # Prepare data for template
    queue_list = ", ".join(queue) if queue else "No patients waiting"
    next_patient_name = queue[0] if queue else "No patients waiting"
    avg_wait_str = f"{average_wait():.2f}"

    return render_template_string("""
        <html>
        <head>
            <title>Clinic Queue System</title>
            <style>
                body {
                    background-color: #1c1c1e;
                    color: #ffffff;
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    margin: 20px;
                }
                h1, h2, h3 {
                    color: #f5f5f7;
                }
                input[type=text] {
                    padding: 8px;
                    border-radius: 5px;
                    border: none;
                    width: 200px;
                }
                button {
                    padding: 8px 12px;
                    margin: 5px;
                    border: none;
                    border-radius: 5px;
                    background-color: #0a84ff;
                    color: white;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #0060df;
                }
                form {
                    margin-bottom: 20px;
                }
                ul {
                    list-style-type: none;
                    padding-left: 0;
                }
                li {
                    padding: 3px 0;
                }
            </style>
        </head>
        <body>
            <h1>Clinic Queue System</h1>
            <p>{{ message }}</p>

            <form method="POST">
                <input type="text" name="patient_name" placeholder="Patient Name">
                <label>Priority <input type="checkbox" name="priority"></label>
                <button name="action" value="add">Add Patient</button>
                <button name="action" value="remove">Remove Patient</button>
                <button name="action" value="next">Next Patient</button>
                <button name="action" value="reset">Reset Queue</button>
                <button name="action" value="export">Export Queue</button>
                <button name="action" value="sort">Sort Queue</button>
            </form>

            <h2>Queue:</h2>
            <p>{{ queue_list }}</p>

            <h2>Total Served: {{ total_served }}</h2>
            <h2>Next Patient: {{ next_patient_name }}</h2>
            <h2>Average Waiting Time: {{ avg_wait_str }} minutes</h2>
            <h2>Today's Served Count: {{ daily_count_val }}</h2>

            <h3>Served Patients History:</h3>
            <ul>
            {% for patient in served_list %}
                <li>{{ patient.name }} - {{ patient.time }}</li>
            {% endfor %}
            </ul>
        </body>
        </html>
    """,
    queue_list=queue_list,
    total_served=total_served,
    next_patient_name=next_patient_name,
    avg_wait_str=avg_wait_str,
    served_list=served_list,
    message=message,
    daily_count_val=daily_count()
    )

# ====== Run Server ======
if __name__ == '__main__':
    app.run(debug=True)