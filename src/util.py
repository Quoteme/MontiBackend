"""
Utility functions and classes for the Flask app.
"""
from flask import Flask, render_template, request, redirect, session
from datetime import datetime

def session_expired():
    login_time = datetime.strptime(session['login_time'], '%Y-%m-%d %H:%M:%S.%f')
    now = datetime.now()
    return (now - login_time).seconds > 30 * 60

def require_login(f):
    def wrapper(*args, **kwargs):
        if 'logged_in' in session and not session_expired():
            return f(*args, **kwargs)
        else:
            return redirect('/login')
    return wrapper
