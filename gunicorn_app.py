# Import the flask app from main.py
from main import flask_app

# This is what gunicorn will import
app = flask_app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)