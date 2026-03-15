from flask import Flask, request, redirect, render_template_string, Response
from datetime import datetime
import csv
import io

app = Flask(__name__)

# -----------------------------
# OOP CLASS
# -----------------------------
class Patient:
    def __init__(self, name, priority=False):
        self.name = name
        self.priority = priority
        self.time_added = datetime.now().strftime("%H:%M:%S")

    def display(self):
        return f"{self.name} ({self.time_added})"


# -----------------------------
# DATA STRUCTURES
# -----------------------------
queue = []
served_history = []
total_served = 0


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
        <title>Clinic Queue System</title>
        <style>
            body {
                background-color: #111;
                color: white;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                text-align: center;
                padding: 40px;
            }

            input, button {
                padding: 10px;
                margin: 5px;
                border-radius: 8px;
                border: none;
            }

            button {
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
            }

            a {
                color: #4da6ff;
                text-decoration: none;
                font-size: 18px;
            }

            ul {
                list-style: none;
                padding: 0;
            }
        </style>
    </head>

    <body>

    <h1>Clinic Queue Manager</h1>

    <h3>Add Patient</h3>

    <form action="/add_patient" method="post">
        <input type="text" name="name" placeholder="Enter patient name" required>
        <button type="submit">Add Patient</button>
    </form>

    <form action="/add_priority" method="post">
        <input type="text" name="name" placeholder="Priority patient name" required>
        <button type="submit">Add Priority Patient</button>
    </form>

    <br>

    <form action="/serve_patient" method="post">
        <button type="submit">Next Patient</button>
    </form>

    <form action="/reset_queue" method="post">
        <button type="submit">Reset Queue</button>
    </form>

    <form action="/export" method="get">
        <button type="submit">Export Queue to CSV</button>
    </form>

    <br>

    <h3>Current Queue</h3>

    <ul>
    {% for patient in queue %}
        <li>{{patient.display()}}</li>
    {% endfor %}
    </ul>

    <h3>Total Patients Served: {{total_served}}</h3>

    <br>

    <a href="/history">View Served Patients History</a>

    </body>
    </html>
    """, queue=queue, total_served=total_served)


# -----------------------------
# ADD PATIENT
# -----------------------------
@app.route("/add_patient", methods=["POST"])
def add_patient():
    name = request.form["name"]
    patient = Patient(name)
    queue.append(patient)
    return redirect("/")


# -----------------------------
# PRIORITY PATIENT
# -----------------------------
@app.route("/add_priority", methods=["POST"])
def add_priority():
    name = request.form["name"]
    patient = Patient(name, True)
    queue.insert(0, patient)
    return redirect("/")


# -----------------------------
# SERVE PATIENT
# -----------------------------
@app.route("/serve_patient", methods=["POST"])
def serve_patient():
    global total_served

    if queue:
        patient = queue.pop(0)
        served_history.append(patient.display())
        total_served += 1

    return redirect("/")


# -----------------------------
# RESET QUEUE
# -----------------------------
@app.route("/reset_queue", methods=["POST"])
def reset_queue():
    queue.clear()
    return redirect("/")


# -----------------------------
# EXPORT QUEUE
# -----------------------------
@app.route("/export")
def export():
    csv_data = "Patient Name,Time Added\n"

    # Check if each item is a Patient object or just a string
    for patient in queue:
        if isinstance(patient, Patient):
            csv_data += f"{patient.name},{patient.time_added}\n"
        else:  # fallback if queue stores strings
            csv_data += f"{patient},N/A\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=queue.csv"}
    )


# -----------------------------
# HISTORY PAGE (SECOND ROUTE)
# -----------------------------
@app.route("/history")
def history():
    return render_template_string("""
    <html>
    <head>
        <title>Served Patients History</title>
        <style>
            body {
                background-color: #111;
                color: white;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                text-align: center;
                padding: 40px;
            }

            ul {
                list-style: none;
                padding: 0;
            }

            a {
                color: #4da6ff;
                text-decoration: none;
                font-size: 18px;
            }
        </style>
    </head>

    <body>

    <h1>Served Patients History</h1>

    <ul>
    {% for patient in served_history %}
        <li>{{patient}}</li>
    {% endfor %}
    </ul>

    <br>

    <a href="/">Back to Home</a>

    </body>
    </html>
    """, served_history=served_history)


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)