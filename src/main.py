from flask import Flask, render_template, request, redirect, session
import pandas as pd
from User import User

app = Flask(__name__, template_folder='./html/', static_folder='./static/')
app.secret_key = "hier ist ein geheimer Schlüssel, der verwendet wird, um sessions zu verschlüsseln"

@app.route('/')
def landing_page():
    return render_template("landing_page.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not User.is_valid(username, password):
            return "Login fehlgeschlagen"
        else:
            session['username'] = username
            session['password'] = password
            session['logged_in'] = True
            return redirect('/dashboard')
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    session['username'] = None
    session['password'] = None
    session['logged_in'] = None
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    else:
        return redirect('/login')

@app.route('/api', methods=['POST'])
def api():
    return 'API'
