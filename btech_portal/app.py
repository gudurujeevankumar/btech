from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # Path to SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Example OTP (In a real app, this would be dynamically generated or sent via email/SMS)
expected_otp = '1234'  # This should be dynamically generated in a real scenario

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Ensure this exists
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        return redirect(url_for('verify_otp'))  # Redirect to OTP page
    flash('Invalid credentials', 'danger')
    return redirect(url_for('index'))

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == expected_otp:
            return redirect(url_for('dashboard'))  # Redirect to the dashboard after successful OTP verification
        else:
            flash('Invalid OTP', 'danger')
            return redirect(url_for('verify_otp'))  # Stay on the OTP page for retry
    return render_template('verify_otp.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if session.get('is_admin'):
        return render_template('admin_dashboard.html')
    else:
        return render_template('student_dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure that the database is created before starting the app
    with app.app_context():  # Ensure we're in the Flask app context
        if not os.path.exists('db.sqlite'):
            db.create_all()  # Create all tables in the database
            print("Database and tables created successfully!")
    app.run(debug=True)
