from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from typing import Dict, List, Optional
import os
import datetime
import pytz
import asyncio
import aiohttp
from login import *
from database import *
from markit import *
from qr import *

BASE_DIR = os.path.abspath("../../")

app = Flask(__name__)
app.secret_key = os.urandom(24)

flag = True

def get_file_list(directory: str) -> List[Dict[str, str]]:
    """List files and directories recursively."""
    file_list = []
    for root, dirs, files in os.walk(directory):
        relative_path = os.path.relpath(root, BASE_DIR)
        if relative_path == ".":
            relative_path = "Root Directory"
        file_list.append({'type': 'folder', 'name': relative_path})
        for file in files:
            file_list.append({'type': 'file', 'name': os.path.join(relative_path, file)})
    return file_list

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/connect')
def connect():
    return render_template("connect.html")

@app.route('/donate')
def donate():
    return render_template("donate.html")

@app.route('/signout')
def signout():
    session.pop('user', None)
    return redirect("/")

@app.route('/files', methods=['GET', 'POST'])
def files():
    if session.get('user') != 'admin':
        return redirect('/')
    return render_template('files.html', files=get_file_list(BASE_DIR))

@app.route('/download/<path:filename>')
def download_file(filename: str):
    if session.get('user') != 'admin':
        return 'Access Denied', 403
    
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if session.get('user') != 'admin':
        return redirect('/')
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        if email == 'admin' and password == 'password':
            session['user'] = "admin"
            return redirect('admin')

        if db_login(email, password):
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials. Try again.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        if login_and_save_data(email, password):
            session['user'] = email
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials. Try again.', 'danger')
    return render_template("signup.html")

@app.route('/scan')
def scan():
    if not flag:
        return 'Contact Admin Service Forbidden!!', 403
    return render_template('scan.html', title="Scan QR Code")

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
async def upload_image():
    if not session.get('user'):
        return "Unauthorized", 401

    if "image" not in request.files:
        return "No image file found", 400

    try:
        image = request.files["image"]
        ist = pytz.timezone('Asia/Kolkata')
        timestamp = datetime.datetime.now(ist).strftime("%Y%m%d%H%M%S")
        filename = f"qr_{timestamp}.jpg"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

        qr_id = scan_it(filename)
        if not qr_id:
            return "Failed to scan QR code", 400

        sid = get_sid(session['user'], get_pass(session['user']))
        student_id = get_stu(session['user'])
        
        async with aiohttp.ClientSession() as client_session:
            attendance_marked = await mark_attendance(sid, qr_id, student_id, client_session)
            if attendance_marked:
                l = await start_mark(qr_id)
                session['qr'] = qr_id
                session['responsi'] = l
                flash("Attendance marked!!")
                return "Image saved successfully", 200
            return "Failed to mark attendance", 400

    except Exception as e:
        app.logger.error(f"Error processing upload: {str(e)}")
        return "Internal server error", 500

if __name__ == "__main__":
    app.run(debug=False, port=6969, host='0.0.0.0')