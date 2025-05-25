from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import CSRFProtect
import webbrowser
import threading
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

def calculate_level_from_xp(xp):
    """Calculate level based on XP with exponential scaling"""
    if xp < 10:
        return 1
    elif xp < 30:
        return 2
    elif xp < 60:
        return 3
    elif xp < 100:
        return 4
    elif xp < 150:
        return 5
    elif xp < 220:
        return 6
    elif xp < 300:
        return 7
    elif xp < 400:
        return 8
    elif xp < 520:
        return 9
    else:
        return 10

def get_problems():
    """Return the list of problems with XP values"""
    return [
        # Divide and Conquer
        {
            "id": 1,
            "title": "Find 7th Smallest Element in Two Sorted Arrays",
            "difficulty": "Hard",
            "completed": False,
            "type": "divide and conquer",
            "xp": 25,
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
            "xp": 15,
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
            "xp": 12,
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
            "xp": 20,
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
            "xp": 18,
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
            "xp": 30,
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
            "xp": 14,
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
            "xp": 35,
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
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    completed_problems = db.Column(db.Text, default='[]')  # JSON string of completed problem IDs

    def get_completed_problems(self):
        """Get list of completed problem IDs"""
        try:
            return json.loads(self.completed_problems)
        except:
            return []

    def add_completed_problem(self, problem_id):
        """Add a problem to completed list"""
        completed = self.get_completed_problems()
        if problem_id not in completed:
            completed.append(problem_id)
            self.completed_problems = json.dumps(completed)

    def award_xp(self, xp_amount):
        """Award XP and update level"""
        self.xp += xp_amount
        self.level = calculate_level_from_xp(self.xp)

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
    completed_problem_ids = current_user.get_completed_problems()
    
    # Mark completed problems
    for problem in problems:
        problem['completed'] = problem['id'] in completed_problem_ids
    
    # Calculate progress percentage
    completed_count = len(completed_problem_ids)
    total_problems = len(problems)
    progress = int((completed_count / total_problems) * 100) if total_problems else 0

    return render_template('index.html',
                           username=current_user.username,
                           level=current_user.level,
                           xp=current_user.xp,
                           progress=progress,
                           problems=problems)

@app.route('/problems')
@login_required
def problem_page():
    problems = get_problems()
    completed_problem_ids = current_user.get_completed_problems()
    
    # Mark completed problems
    for problem in problems:
        problem['completed'] = problem['id'] in completed_problem_ids
    
    return render_template('problems.html', 
                          username=current_user.username, 
                          level=current_user.level,
                          xp=current_user.xp,
                          problems=problems)

@app.route('/submit_answer', methods=['POST'])
@login_required
@csrf.exempt
def submit_answer():
    data = request.get_json()
    problem_id = data.get('problem_id')
    user_answer = data.get('answer')
    
    problems = get_problems()
    problem = next((p for p in problems if p['id'] == problem_id), None)
    
    if not problem:
        return jsonify({'success': False, 'message': 'Problem not found'})
    
    completed_problem_ids = current_user.get_completed_problems()
    
    if user_answer == problem['answer']:
        # Award XP only if not already completed
        if problem_id not in completed_problem_ids:
            current_user.add_completed_problem(problem_id)
            current_user.award_xp(problem['xp'])
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'✅ Correct! +{problem["xp"]} XP earned!',
                'new_xp': current_user.xp,
                'new_level': current_user.level
            })
        else:
            return jsonify({
                'success': True,
                'message': '✅ Correct! (Already completed)',
                'new_xp': current_user.xp,
                'new_level': current_user.level
            })
    else:
        return jsonify({'success': False, 'message': '❌ Incorrect. Try again!'})

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
                         level=current_user.level,
                         xp=current_user.xp)

@app.route('/profile/change-username', methods=['POST'])
@login_required
def change_username():
    new_username = request.form.get('new_username', '').strip()
    
    if not new_username:
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             xp=current_user.xp,
                             error_message="Username cannot be empty.")
    
    if User.query.filter_by(username=new_username).first():
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             xp=current_user.xp,
                             error_message="Username already exists. Please choose another.")
    
    current_user.username = new_username
    db.session.commit()
    
    return render_template('profile.html', 
                         username=current_user.username, 
                         level=current_user.level,
                         xp=current_user.xp,
                         success_message="Username updated successfully!")

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(current_user.password, current_password):
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             xp=current_user.xp,
                             error_message="Current password is incorrect.")
    
    if new_password != confirm_password:
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             xp=current_user.xp,
                             error_message="New passwords do not match.")
    
    if len(new_password) < 6:
        return render_template('profile.html', 
                             username=current_user.username, 
                             level=current_user.level,
                             xp=current_user.xp,
                             error_message="Password must be at least 6 characters long.")
    
    current_user.password = generate_password_hash(new_password)
    db.session.commit()
    
    return render_template('profile.html', 
                         username=current_user.username, 
                         level=current_user.level,
                         xp=current_user.xp,
                         success_message="Password updated successfully!")

@app.route('/profile/delete-account', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    logout_user()
    
    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
    
    return redirect(url_for('register'))

@app.route('/api/articles', methods=['GET'])
@login_required
def get_articles():
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
            "title": "Introduction to Divide and Conquer Algorithms",
            "type": "Divide and Conquer",
            "content": (
                "Divide and conquer is a fundamental algorithmic technique that helps solve complex problems by breaking them down into smaller, "
                "more manageable subproblems. The general approach involves three steps: dividing the problem into subproblems, conquering each subproblem "
                "(often recursively), and then combining their solutions to solve the original problem.\n\n"
                "For example, merge sort uses divide and conquer by splitting an array into halves, sorting each half recursively, "
                "and then merging the sorted halves. Binary search divides the search space in half at each step to quickly find an element.\n\n"
                "This method is powerful because it reduces the problem size exponentially, often leading to logarithmic time complexities like O(log n) or O(n log n). "
                "Understanding recursion and how to combine results efficiently is essential when using divide and conquer. This technique is widely used in sorting, searching, "
                "and many other algorithmic challenges."
            )
        },
        {
            "title": "Basics of Graph Algorithms",
            "type": "Graph Algorithms",
            "content": (
                "Graphs are data structures made up of nodes (called vertices) connected by edges. They can represent networks such as social connections, road maps, or communication systems.\n\n"
                "There are two main types of graphs: undirected (edges have no direction) and directed (edges point from one node to another). Understanding how to represent graphs efficiently—"
                "using adjacency lists or adjacency matrices—is important for implementing graph algorithms.\n\n"
                "Key concepts include connected components (groups of nodes reachable from one another), cycles (paths that start and end at the same node), and traversal methods like Depth-First Search (DFS) "
                "and Breadth-First Search (BFS). DFS explores as far as possible along a branch before backtracking, while BFS explores neighbors level by level.\n\n"
                "Graph algorithms help solve problems like finding shortest paths, detecting cycles, or determining connectivity. Mastering these basics enables you to handle a wide range of graph-related challenges."
            )
        },
        {
            "title": "Fundamentals of Dynamic Programming",
            "type": "Dynamic Programming",
            "content": (
                "Dynamic programming (DP) is an optimization technique used to solve problems with overlapping subproblems and optimal substructure. "
                "Instead of solving the same subproblems repeatedly, DP stores their solutions in a table (memoization or tabulation) to avoid redundant work.\n\n"
                "To use dynamic programming effectively, you must:\n"
                "- Define the state clearly: what does each entry in your DP table represent?\n"
                "- Determine the state transitions: how can you build up solutions from smaller subproblems?\n\n"
                "For example, when finding the longest increasing subsequence or computing edit distance between strings, DP tables help track partial results efficiently.\n\n"
                "While DP problems can be tricky at first due to identifying states and transitions, practicing these steps will build your ability to tackle complex optimization tasks."
            )
        },
        {
            "title": "Understanding Greedy Algorithms",
            "type": "Greedy Algorithms",
            "content": (
                "Greedy algorithms solve problems by making a sequence of choices, each of which looks best at that moment without reconsidering previous decisions. "
                "The idea is to pick the locally optimal option at every step with the hope that this leads to a globally optimal solution.\n\n"
                "A classic example is interval scheduling: selecting the maximum number of non-overlapping meetings by always choosing the meeting that finishes earliest next.\n\n"
                "Greedy approaches are usually simpler and faster than dynamic programming but don't work for all problems because they don't consider future consequences. "
                "\"Optimal substructure\" is required—meaning an optimal solution contains optimal solutions to subproblems—but overlapping subproblems are not necessary here.\n\n"
                "Understanding when greedy works versus when more complex methods like dynamic programming are needed is key to applying this technique effectively."
            )
        },
        {
            "title": "Introduction to Algorithms",
            "type": "General",
            "content": (
                "Algorithms are step-by-step instructions designed to perform specific tasks or solve particular problems efficiently. They form the backbone of computer science "
                "and software development.\n\n"
                "'Efficiency' means using minimal time and resources while producing correct results. To achieve this, computer scientists have developed various algorithmic paradigms:\n\n"
                
                "- Divide and Conquer: break problems into smaller parts solved independently.\n"
                "- Dynamic Programming: store intermediate results for overlapping subproblems.\n"
                "- Greedy Algorithms: make locally optimal choices aiming for global optimum.\n"
                "- Graph Algorithms: explore data structured as nodes connected by edges.\n\n"

                "*Learning these paradigms provides a toolkit for approaching many computational challenges.*\n\n"

                "When solving problems:\n"
                 "- Understand what type it belongs to;\n"
                 "- Learn its key ideas;\n"
                 "- Practice applying them step-by-step;\n"
                 "- Analyze time and space complexity for efficiency."
                 "\nThis foundation will empower you to confidently tackle diverse algorithmic problems."
            )
        }
    ]
    
    return render_template('articles.html', 
                          username=current_user.username, 
                          level=current_user.level,
                          xp=current_user.xp,
                          articles=articles)

def open_browser():
    webbrowser.open_new("http://localhost:5000/login")

if __name__ == '__main__':
    with app.app_context():
       db.create_all()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
