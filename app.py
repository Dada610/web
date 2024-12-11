from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

# Simulated database
users_db = [{"id": 1, "email": "test@example.com", "password": "1234"}]

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    user = next((u for u in users_db if str(u["id"]) == user_id), None)
    if user:
        return User(id=user["id"], email=user["email"], password=user["password"])
    return None

# Initialize session variables
@app.before_request
def initialize_session():
    if 'orders' not in session:
        session['orders'] = []

# Routes
@app.route('/')
def index():
    return render_template('index.html')



@app.route('/menu')
@login_required
def menu():
    menu_items = [
        {"name": "Grilled Chicken Salad", "price": 12.99, "image": url_for('static', filename='images/Grilled Chicken Salad.jpg')},
        {"name": "Quinoa Power Bowl", "price": 10.99, "image": url_for('static', filename='images/Quinoa Power Bowl.jpg')},
        {"name": "Vegan Buddha Bowl", "price": 11.49, "image": url_for('static', filename='images/Vegan Buddha Bowl.jpg')},
        {"name": "Avocado Toast", "price": 9.99, "image": url_for('static', filename='images/Avocado Toast.jpg')},
        {"name": "Chicken Wrap", "price": 8.99, "image": url_for('static', filename='images/Chicken Wrap.jpg')},
        {"name": "Protein Smoothie", "price": 6.99, "image": url_for('static', filename='images/Protein Smoothie.jpg')}
    ]
    return render_template('menu.html', menu_items=menu_items)


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = next((u for u in users_db if u['email'] == email and u['password'] == password), None)
        if user:
            user_obj = User(id=user["id"], email=user["email"], password=user["password"])
            login_user(user_obj)
            flash("Login successful!", "success")
            return redirect(url_for('menu'))
        else:
            flash("Invalid credentials.", "danger")
    return render_template('auth.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if any(u['email'] == email for u in users_db):
            flash("Email already registered.", "error")
        else:
            new_user = {"id": len(users_db) + 1, "email": email, "password": password}
            users_db.append(new_user)
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('auth'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for('index'))

@app.route('/add_order', methods=['POST'])
@login_required
def add_order():
    item = request.form['item']
    price = float(request.form['price'])
    session['orders'].append({"item": item, "price": price})
    session.modified = True  # Mark session as modified
    flash(f"{item} added to cart!", "success")
    return redirect(url_for('menu'))

@app.route('/orders')
@login_required
def order_summary():
    orders = session.get('orders', [])
    total = sum(order['price'] for order in orders)
    return render_template('orders.html', orders=orders, total=total)

@app.route('/clear_orders')
@login_required
def clear_orders():
    session['orders'] = []
    session.modified = True
    flash("All orders cleared.", "info")
    return redirect(url_for('order_summary'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        flash("Message sent successfully!", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
