from flask import Flask, render_template, redirect, url_for, request, session, flash
from database import add_user, verify_user
import os
import requests
from datetime import datetime
from config import OPENWEATHER_API_KEY, CITY, COUNTRY
from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')

def home():
    user = session.get('user')

    # Prayer times
    prayer_url = f"https://api.aladhan.com/v1/timingsByCity?city={CITY}&country={COUNTRY}&method=2"
    prayer_response = requests.get(prayer_url).json()
    timings = prayer_response['data']['timings']

    # Weather
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
    weather_response = requests.get(weather_url).json()

    weather = {
        "description": weather_response['weather'][0]['description'].title(),
        "temp": weather_response['main']['temp'],
        "feels_like": weather_response['main']['feels_like'],
    }

    return render_template('home.html', timings=timings, weather=weather, user=user, CITY=CITY, COUNTRY=COUNTRY)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = verify_user(username, password)
        if user:
            session['user'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if add_user(username, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.', 'danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/reminder', methods=['POST'])
def reminder():
    reminder_text = request.form['reminder']
    session['reminder'] = reminder_text
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
