from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import CSRFProtect
import webbrowser
import threading
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

problems = [
    {"id": 1, "title": "Two Sum", "difficulty": "Easy", "completed": True, "language": "javascript"},
    {"id": 2, "title": "Add Two Numbers", "difficulty": "Medium", "completed": False, "language": "python"},
    {"id": 3, "title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "completed": True, "language": "java"},
    {"id": 4, "title": "Median of Two Sorted Arrays", "difficulty": "Hard", "completed": False, "language": "cpp"},
    {"id": 5, "title": "Palindrome Number", "difficulty": "Easy", "completed": False, "language": "javascript"},
    {"id": 6, "title": "Regular Expression Matching", "difficulty": "Hard", "completed": False, "language": "python"},
    {"id": 7, "title": "Container With Most Water", "difficulty": "Medium", "completed": True, "language": "java"},
    {"id": 8, "title": "Longest Palindromic Substring", "difficulty": "Medium", "completed": False, "language": "python"},
    {"id": 9, "title": "String to Integer (atoi)", "difficulty": "Medium", "completed": False, "language": "cpp"},
    {"id": 10, "title": "Merge k Sorted Lists", "difficulty": "Hard", "completed": False, "language": "java"},
    {"id": 11, "title": "4Sum", "difficulty": "Medium", "completed": False, "language": "python"},
    {"id": 12, "title": "Remove Nth Node From End of List", "difficulty": "Medium", "completed": False, "language": "javascript"}
]

login_manager = LoginManager()
login_manager.login_view = 'login'  # Redirect to login if not authenticated
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    level = db.Column(db.Integer, default=1)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            error = "Username already exists. Please choose another."
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            error = "The username or password you entered is incorrect. Please try again."
        else:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)

@app.route('/dashboard')
@login_required
def dashboard():
    # Example: problems could come from DB; here is a static list for demo
    def index():
        return render_template('your_template.html', problems=problems, username='Alice', level=5)

    # Calculate progress percentage
    completed_count = sum(p['completed'] for p in problems)
    total_problems = len(problems)
    progress = int((completed_count / total_problems) * 100) if total_problems else 0

    return render_template('index.html',
                           username=current_user.username,
                           level=current_user.level,
                           progress=progress,
                           problems=problems)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', 
                         username=current_user.username, 
                         level=current_user.level)

@app.route('/profile/change-username', methods=['POST'])
@login_required
def change_username():
    new_username = request.form.get('new_username', '').strip()
    
    if not new_username:
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             error_message="Username cannot be empty.")
    
    # Check if username already exists
    if User.query.filter_by(username=new_username).first():
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             error_message="Username already exists. Please choose another.")
    
    # Update username
    current_user.username = new_username
    db.session.commit()
    
    return render_template('profile.html', 
                         username=current_user.username, 
                         level=current_user.level,
                         success_message="Username updated successfully!")

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Verify current password
    if not check_password_hash(current_user.password, current_password):
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             error_message="Current password is incorrect.")
    
    # Check if new passwords match
    if new_password != confirm_password:
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             error_message="New passwords do not match.")
    
    # Check password length
    if len(new_password) < 6:
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             error_message="Password must be at least 6 characters long.")
    
    # Update password
    current_user.password = generate_password_hash(new_password)
    db.session.commit()
    
    return render_template('profile.html', 
                         username=current_user.username, 
                         level=current_user.level,
                         success_message="Password updated successfully!")

@app.route('/profile/delete-account', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    logout_user()
    
    # Delete the user from database
    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
    
    return redirect(url_for('register'))

def open_browser():
    webbrowser.open_new("http://localhost:5000/login")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
