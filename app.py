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

def get_problems():
    """Return the list of problems - shared between routes"""
    return [
        # Divide and Conquer
        {
            "id": 1,
            "title": "Find 7th Smallest Element in Two Sorted Arrays",
            "difficulty": "Hard",
            "completed": False,
            "type": "divide and conquer",
            "content": (
                "You have two sorted arrays: nums1 = [1, 3, 8, 9, 15] and nums2 = [7, 11, 18, 19, 21, 25]. "
                "If you were to merge these arrays into one big sorted array, it would look like: "
                "[1, 3, 7, 8, 9, 11, 15, 18, 19, 21, 25]. Your task is to find the 7th smallest element "
                "in this combined array without actually merging the arrays. Use a divide and conquer approach "
                "that runs in O(log(min(m,n))) time by eliminating half of one array at each step."
            ),
            "answer": 15
        },
        {
            "id": 2,
            "title": "Count Inversions in Array [5, 2, 6, 1]",
            "difficulty": "Medium",
            "completed": False,
            "type": "divide and conquer",
            "content": (
                "Given the array [5, 2, 6, 1], count how many inversions exist. An inversion is when "
                "a larger number appears before a smaller number. For example, (5,2) is an inversion "
                "because 5 > 2 but 5 comes first. Similarly (5,1), (2,1), (6,1), and (5,2) are all "
                "inversions in this array. Use a divide and conquer approach similar to merge sort "
                "to count these efficiently in O(n log n) time rather than checking every pair."
            ),
            "answer": 5
        },

        # Graph Algorithms
        {
            "id": 3,
            "title": "Connected Components in Graph with 6 Nodes",
            "difficulty": "Medium",
            "completed": False,
            "type": "graph algorithms",
            "content": (
                "You have an undirected graph with 6 nodes labeled 0, 1, 2, 3, 4, 5. "
                "The edges are: (0,1), (1,2), and (3,4). This means node 0 connects to node 1, "
                "node 1 connects to node 2, and node 3 connects to node 4. Nodes 5 is completely "
                "isolated with no connections. A connected component is a group of nodes where "
                "you can reach any node from any other node in that group by following edges. "
                "Count how many separate connected components exist in this graph."
            ),
            "answer": 3
        },
        {
            "id": 4,
            "title": "Cycle Detection in Specific Directed Graph",
            "difficulty": "Hard",
            "completed": False,
            "type": "graph algorithms",
            "content": (
                "You have a directed graph with 4 nodes (0, 1, 2, 3) and these directed edges: "
                "0→1 (0 points to 1), 1→2 (1 points to 2), 2→3 (2 points to 3), and 3→1 (3 points back to 1). "
                "A cycle exists if you can start at some node and follow the directed edges to eventually "
                "return to where you started. In this case, you can go 1→2→3→1, which forms a cycle. "
                "Use DFS with a recursion stack to detect if this directed graph contains any cycle. "
                "Return 1 if a cycle exists, 0 if no cycle exists."
            ),
            "answer": 1
        },

        # Dynamic Programming
        {
            "id": 5,
            "title": "LIS Length for [10, 9, 2, 5, 3, 7, 101, 18]",
            "difficulty": "Medium",
            "completed": False,
            "type": "dynamic programming",
            "content": (
                "Find the length of the longest increasing subsequence in [10, 9, 2, 5, 3, 7, 101, 18]. "
                "A subsequence doesn't have to be contiguous - you can skip elements. For example, "
                "[2, 5, 7, 101] is a valid increasing subsequence of length 4, and [2, 3, 7, 18] is "
                "another one. You need to find the longest possible such subsequence. Use dynamic "
                "programming where dp[i] represents the length of the longest increasing subsequence "
                "ending at index i."
            ),
            "answer": 4
        },
        {
            "id": 6,
            "title": "Edit Distance: 'horse' to 'ros'",
            "difficulty": "Hard",
            "completed": False,
            "type": "dynamic programming",
            "content": (
                "Calculate the minimum number of operations needed to transform the string 'horse' "
                "into the string 'ros'. You can perform three types of operations: insert a character, "
                "delete a character, or replace a character. For example, one way is: "
                "horse → rorse (replace h with r) → rose (delete r) → ros (delete e). "
                "That's 3 operations. Use dynamic programming with a 2D table where dp[i][j] represents "
                "the minimum operations to transform the first i characters of 'horse' into the first j "
                "characters of 'ros'."
            ),
            "answer": 3
        },

        # Greedy Algorithms
        {
            "id": 7,
            "title": "Maximum Non-overlapping Intervals",
            "difficulty": "Medium", 
            "completed": False,
            "type": "greedy algorithms", 
            "content": (
                "You have these time intervals: [(1,3), (2,6), (8,10), (15,18)]. Each interval "
                "represents a meeting with a start and end time. Two intervals overlap if one "
                "starts before the other ends. For example, (1,3) and (2,6) overlap because "
                "the second meeting starts at time 2, which is before the first meeting ends at time 3. "
                "Your goal is to select the maximum number of meetings you can attend without any "
                "time conflicts. Use a greedy approach: sort by end time and always pick the meeting "
                "that ends earliest among the remaining options."
            ),
            "answer": 3
        },
        {
            "id": 8,
            "title": "Huffman Tree Total Encoding Length",
            "difficulty": "Hard", 
            "completed": False, 
            "type": "greedy algorithms", 
            "content": (
                "You need to create an optimal Huffman encoding for these characters and their frequencies: "
                "A appears 5 times, B appears 9 times, C appears 12 times, D appears 13 times, "
                "E appears 16 times, and F appears 45 times. In Huffman encoding, more frequent "
                "characters get shorter codes. Build the Huffman tree by repeatedly combining the "
                "two nodes with smallest frequencies. Once you have the tree, calculate the total "
                "encoding length, which is the sum of (frequency × depth) for each character, where "
                "depth is how many bits are needed to encode that character."
            ),
            "answer": 224
        }
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
    problems = get_problems()
    
    # Calculate progress percentage
    completed_count = sum(p['completed'] for p in problems)
    total_problems = len(problems)
    progress = int((completed_count / total_problems) * 100) if total_problems else 0

    return render_template('index.html',
                           username=current_user.username,
                           level=current_user.level,
                           progress=progress,
                           problems=problems)

@app.route('/problems')
@login_required
def problem_page():
    problems = get_problems()
    
    return render_template('problems.html', 
                          username=current_user.username, 
                          level=current_user.level,
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

@app.route('/api/articles', methods=['GET'])
@login_required
def get_articles():
    # Example article list, replace with DB query if needed
    articles = [
        {"id": 1, "title": "Intro to Flask", "content": "Flask is a micro web framework..."},
        {"id": 2, "title": "REST APIs with Flask", "content": "Building APIs is easy with Flask..."}
    ]
    return {"articles": articles}

@app.route('/articles')
@login_required
def articles_page():
    articles = [
        {
            "title": "Introduction to Algorithms", 
            "language": "all",
            "content": "This is an introductory article about algorithms that applies to all programming languages. Algorithms are step-by-step procedures for solving problems. They form the foundation of computer science and are essential for efficient programming."
        },
        {
            "title": "Data Structures in JavaScript", 
            "language": "Javascript",
            "content": "Learn about data structures in JavaScript, including arrays, objects, maps, and sets. Understanding these structures is crucial for writing efficient and maintainable JavaScript code."
        },
        {
            "title": "Python for Beginners", 
            "language": "Python",
            "content": "Get started with Python programming language. Learn syntax, data types, and basic concepts. Python is known for its readability and simplicity, making it an excellent language for beginners."
        },
        {
            "title": "Java Collections Framework", 
            "language": "Java",
            "content": "An overview of Java's Collections Framework including Lists, Sets, Maps and more. The Collections Framework provides a unified architecture for representing and manipulating collections in Java."
        },
        {
            "title": "Memory Management in C++", 
            "language": "Cpp",
            "content": "Understanding memory allocation, pointers, and how to prevent memory leaks in C++. Proper memory management is essential for writing efficient and bug-free C++ programs."
        },
        {
            "title": "Web Development Best Practices", 
            "language": "all",
            "content": "Best practices for web development are essential regardless of your programming language. This article covers key principles like responsive design, accessibility, performance optimization, and security considerations."
        },
        {
            "title": "The Future of AI", 
            "language": "all",
            "content": "Artificial intelligence is rapidly evolving across all programming ecosystems. Learn about current trends, future predictions, and how AI is transforming software development and various industries."
        }
    ]
    
    return render_template('articles.html', 
                          username=current_user.username, 
                          level=current_user.level,
                          articles=articles)

def open_browser():
    webbrowser.open_new("http://localhost:5000/login")

if __name__ == '__main__':
    with app.app_context():
       db.create_all()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
