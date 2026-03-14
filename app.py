from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
   # Simple homepage showing queue message
    return render_template_string("""
        <h1>Welcome to the Clinic Queue System</h1>
        <p>Current queue: 0 patients</p>
    """)

if __name__ == '__main__':
    app.run(debug=True)