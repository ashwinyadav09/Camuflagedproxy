from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from login import *
import time, datetime, base64, pytz
from database import *
from markit import *
from qr import *
import asyncio
import nest_asyncio
import os

BASE_DIR = os.path.abspath("../../")

app = Flask(__name__)
app.secret_key = os.urandom(24)
flag = True

try:
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
        try:
            del session['user']
        except Exception as e:
            print("No Session found")
        return redirect("/")

    @app.route('/files', methods=['GET', 'POST'])
    def files():
        try:
            if session['user'] == 'admin':
                return render_template('files.html', files=get_file_list(BASE_DIR))
        except Exception as e:
            print('False login')
            return redirect('/')

    @app.route('/download/<path:filename>')
    def download_file(filename):
        try:
            if session['user'] == 'admin':
                file_path = os.path.join(BASE_DIR, filename)
                if os.path.exists(file_path):
                    return send_file(file_path, as_attachment=True)
                return "File not found", 404
            return "Unauthorized access", 403
        except Exception as e:
            return "Unauthorized access", 403

    def get_file_list(directory):
        file_list = []
        for root, dirs, files in os.walk(directory):
            relative_path = os.path.relpath(root, BASE_DIR)
            if relative_path == ".":
                relative_path = "Root Directory"
            file_list.append({'type': 'folder', 'name': relative_path})
            for file in files:
                file_list.append({'type': 'file', 'name': os.path.join(relative_path, file)})
        return file_list

    @app.route('/admin', methods=['POST', 'GET'])
    def admin():
        try:
            if session['user'] == 'admin':
                return render_template('admin.html')
        except Exception as e:
            print('False login')
            return redirect('/')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['username']
            password = request.form['password']
            if email == 'admin' and password == 'admin123':
                session['user'] = "admin"
                return redirect('admin')
            elif db_login(email, password):
                session['user'] = email
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials. Try again.', 'danger')
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template("dashboard.html")

    @app.route('/signup', methods=['POST', 'GET'])
    def signup():
        if request.method == 'POST':
            email = request.form.get('username')
            password = request.form.get('password')
            if not email or not password:
                flash('Email and password are required.', 'danger')
                return render_template("signup.html")
            try:
                success = login_and_save_data(email, password)
                if success:
                    session['user'] = email
                    flash('Registration successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Registration failed. Check your credentials or try again later.', 'danger')
            except Exception as e:
                print(f"Signup error: {str(e)}")
                flash(f'Registration failed: {str(e)}', 'danger')
        return render_template("signup.html")

    @app.route('/scan')
    def scan():
        if flag:
            return render_template('scan.html', title="Scan QR Code")
        return 'Contact Admin Service Forbidden!!'

    @app.route('/')
    def index():
        return render_template('index.html')

    UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    @app.route("/upload", methods=["POST"])
    async def upload_image():
        if 'user' not in session:
            flash("Please log in first.", "danger")
            return redirect(url_for('login'))

        if "image" not in request.files:
            flash("No image file provided.", "danger")
            return redirect(url_for('scan'))

        ist = pytz.timezone('Asia/Kolkata')
        t = datetime.datetime.now(ist).strftime("%Y%m%d%H%M%S")
        image = request.files["image"]
        filename = f"qr_{t}.jpg"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        try:
            image.save(image_path)
            qr_id = scan_it(image_path)
            if not qr_id:
                flash("Failed to decode QR code. Please try again with a clear image.", "danger")
                return redirect(url_for('scan'))

            l = run_start_mark(qr_id)
            successful_marks = sum(1 for r in l if r is True)
            session['qr'] = qr_id
            session['responsi'] = l
            flash(f"Attendance marked for {successful_marks} users!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Error in upload_image: {e}")
            flash(f"Failed to process QR code: {str(e)}", "danger")
            return redirect(url_for('scan'))

except Exception as e:
    print(e)

if __name__ == "__main__":
    nest_asyncio.apply()
    app.run(debug=False, port=6969, host='0.0.0.0')