import os
from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return redirect("http://localhost:8000")

@app.route('/<path:path>')
def catch_all(path):
    return redirect(f"http://localhost:8000/{path}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))