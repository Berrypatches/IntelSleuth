"""
Gunicorn configuration for Flask
"""
import multiprocessing

# Gunicorn config
bind = "0.0.0.0:5000"
workers = 1
reload = True
wsgi_app = "flask_wsgi:application"