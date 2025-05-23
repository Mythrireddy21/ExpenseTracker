from flask import Flask, render_template, request, redirect, session, flash, url_for, send_file
import csv
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import io
from forex_python.converter import CurrencyRates


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# File paths
USERS_FILE = 'users.csv'
EXPENSES_FILE = 'expenses.csv'
BUDGET_FILE = 'budget.csv'
EXPENSE_FIELDS = ['id', 'username', 'date', 'amount', 'currency', 'category', 'description']


# ---------------------- CSV Utility Functions ----------------------

def read_csv(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, newline='') as f:
        return list(csv.DictReader(f))

def write_csv(file_path, data, fieldnames):
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def append_csv(file_path, row, fieldnames):
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# ---------------------- Helper Functions ----------------------

def get_user_budget(username):
    budgets = read_csv(BUDGET_FILE)
    for b in budgets:
        if b['username'] == username:
            return float(b['budget'])
    return None

# Currency conversion helper
def convert_to_base_currency(amount, from_currency, base_currency='USD'):
    c = CurrencyRates()
    if from_currency == base_currency:
        return amount
    try:
        converted = c.convert(from_currency, base_currency, float(amount))
        return round(converted, 2)
    except:
        return 0.0  # If conversion fails

# ---------------------- Routes ----------------------

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/home')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    users = read_csv(USERS_FILE)
    for user in users:
        if user['username'] == username and user['password'] == password:
            session['user'] = username
            flash(f"Welcome back, {username}!", 'success')
            return redirect('/home')
    flash("Invalid username or password.", 'danger')
    return redirect('/')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    username = request.form.get('username').strip()
    email = request.form.get('email').strip()
    password = request.form.get('password').strip()
    confirm_password = request.form.get('confirm_password').strip()

    if password != confirm_password:
        flash("Passwords do not match.", 'danger')
        return redirect('/register')

    if not username or not email or not password:
        flash("All fields are required.", 'danger')
        return redirect('/register')

    users = read_csv(USERS_FILE)
    for user in users:
        if user['username'] == username:
            flash("Username already exists.", 'danger')
            return redirect('/register')

    append_csv(USERS_FILE, {'username': username, 'email': email, 'password': password}, ['username', 'email', 'password'])
    flash("Registration successful! Please login.", 'success')
    return redirect('/')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    username = session['user']
    budget = get_user_budget(username)
    return render_template('home.html', username=username, budget=budget)


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    username = session['user']
    expenses = read_csv(EXPENSES_FILE)

    # Filter only current user's expenses
    user_expenses = [e for e in expenses if e['username'] == username]

    # Fetch filter values from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category', '').strip().lower()
    min_amount = request.args.get('min_amount')
    max_amount = request.args.get('max_amount')
    keyword = request.args.get('keyword', '').strip().lower()

    filtered = []
    total_expense_usd = 0.0
    category_sums = {}

    for exp in user_expenses:
        try:
            exp_date = datetime.strptime(exp['date'], '%Y-%m-%d')
            exp_amount = float(exp['amount'])
            currency = exp.get('currency', 'USD')
            description = exp.get('description', '').lower()
        except:
            continue

        # Apply filters
        if start_date and exp_date < datetime.strptime(start_date, '%Y-%m-%d'):
            continue
        if end_date and exp_date > datetime.strptime(end_date, '%Y-%m-%d'):
            continue
        if category and category not in exp['category'].lower():
            continue
        if min_amount and exp_amount < float(min_amount):
            continue
        if max_amount and exp_amount > float(max_amount):
            continue
        if keyword and keyword not in description:
            continue

        # Passed filters, convert amount to USD and accumulate
        amt_usd = convert_to_base_currency(exp_amount, currency)
        total_expense_usd += amt_usd

        # Track category-wise sums
        cat = exp['category']
        category_sums[cat] = category_sums.get(cat, 0) + amt_usd

        filtered.append(exp)

    # Get user's budget
    budget_str = get_user_budget(username)
    budget = None
    try:
        if budget_str is not None:
            budget = float(budget_str)
    except ValueError:
        budget = None

    # Budget alert system
    budget_alert = None
    budget_alert_class = None

    if budget is not None:
        if total_expense_usd > budget:
            budget_alert = "❌ Alert: You have exceeded your budget!"
            budget_alert_class = "budget-exceeded"
        elif total_expense_usd > 0.75 * budget:
            percent_used = round((total_expense_usd / budget) * 100)
            budget_alert = f"⚠️ Warning: You’ve used {percent_used}% of your budget."
            budget_alert_class = "budget-warning"
        else:
            budget_alert = "✅ You are within your budget."
            budget_alert_class = "budget-positive"

    return render_template(
        'dashboard.html',
        username=username,
        expenses=filtered,
        total_expense=total_expense_usd,
        category_sums=category_sums,
        budget=budget,
        budget_alert=budget_alert,
        budget_alert_class=budget_alert_class
    )

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        username = session['user']
        category = request.form.get('category', '').strip()
        amount = request.form.get('amount', '').strip()
        date = request.form.get('date', '').strip()
        description = request.form.get('description', '').strip()
        currency = request.form.get('currency', '').strip()

        # Validate all fields
        if not category or not amount or not date or not description or not currency:
            flash("All fields are required.", 'danger')
            return redirect('/add_expense')

        try:
            amount_val = float(amount)
            datetime.strptime(date, '%Y-%m-%d')  # validate date format
        except ValueError:
            flash("Invalid amount or date format.", 'danger')
            return redirect('/add_expense')

        # Generate new ID
        expenses = read_csv(EXPENSES_FILE)
        max_id = max([int(exp['id']) for exp in expenses if exp.get('id', '').isdigit()] or [0])
        new_id = max_id + 1

        # Prepare new row
        new_expense = {
            'id': str(new_id),
            'username': username,
            'date': date,
            'amount': f"{amount_val:.2f}",
            'currency': currency,
            'category': category,
            'description': description
        }

        append_csv(EXPENSES_FILE, new_expense, EXPENSE_FIELDS)

        flash("Expense added successfully.", 'success')
        return redirect('/dashboard')

    return render_template('add_expense.html')

@app.route('/edit_expense/<int:index>', methods=['GET', 'POST'])
def edit_expense(index):
    if 'user' not in session:
        return redirect('/')
    
    username = session['user']
    expenses = read_csv(EXPENSES_FILE)
    user_expenses = [e for e in expenses if e['username'] == username]
    user_indices = [i for i, e in enumerate(expenses) if e['username'] == username]

    if index < 0 or index >= len(user_expenses):
        flash("Invalid expense index.", 'danger')
        return redirect('/dashboard')

    actual_index = user_indices[index]
    expense = expenses[actual_index]

    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        amount = request.form.get('amount', '').strip()
        date = request.form.get('date', '').strip()
        description = request.form.get('description', '').strip()
        currency = request.form.get('currency', '').strip()

        if not category or not amount or not date or not description or not currency:
            flash("All fields are required.", 'danger')
            return render_template('edit_expense.html', expense=expense, index=index)

        try:
            amount_val = float(amount)
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            flash("Invalid amount or date format.", 'danger')
            return render_template('edit_expense.html', expense=expense, index=index)

        # Update expense
        expenses[actual_index] = {
            'id': expense['id'],
            'username': username,
            'date': date,
            'amount': f"{amount_val:.2f}",
            'currency': currency,
            'category': category,
            'description': description
        }

        write_csv(EXPENSES_FILE, expenses, EXPENSE_FIELDS)
        flash("Expense updated successfully.", 'success')
        return redirect('/dashboard')

    return render_template('edit_expense.html', expense=expense, index=index)

@app.route('/delete_expense/<int:index>', methods=['POST'])
def delete_expense(index):
    if 'user' not in session:
        return redirect('/')

    username = session['user']
    expenses = read_csv(EXPENSES_FILE)
    user_indices = [i for i, e in enumerate(expenses) if e['username'] == username]

    if index < 0 or index >= len(user_indices):
        flash("Invalid expense index.", "danger")
        return redirect(url_for('dashboard'))

    actual_index = user_indices[index]
    deleted = expenses.pop(actual_index)

    if expenses:
        fieldnames = expenses[0].keys()
        write_csv(EXPENSES_FILE, expenses, fieldnames)
    else:
        # If all expenses are deleted, clear the file but preserve headers
        fieldnames = deleted.keys()
        write_csv(EXPENSES_FILE, [], fieldnames)

    flash("Expense deleted successfully.", "success")
    return redirect(url_for('dashboard'))




@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        return redirect('/')
    username = session['user']
    users = read_csv(USERS_FILE)
    user_data = next((u for u in users if u['username'] == username), None)

    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        confirm_password = request.form.get('confirm_password').strip()

        if not email:
            flash("Email cannot be empty.", 'danger')
            return redirect('/edit_profile')

        if password and password != confirm_password:
            flash("Passwords do not match.", 'danger')
            return redirect('/edit_profile')

        for user in users:
            if user['username'] == username:
                user['email'] = email
                if password:
                    user['password'] = password
                break

        write_csv(USERS_FILE, users, ['username', 'email', 'password'])
        flash("Profile updated successfully.", 'success')
        return redirect('/home')

    return render_template('edit_profile.html', user=user_data)

@app.route('/set_budget', methods=['POST'])
def set_budget():
    if 'user' not in session:
        return redirect('/')
    username = session['user']
    budget = request.form.get('budget').strip()

    try:
        budget_val = float(budget)
        if budget_val < 0:
            raise ValueError
    except:
        flash("Invalid budget amount.", 'danger')
        return redirect('/home')

    budgets = read_csv(BUDGET_FILE)
    budgets = [b for b in budgets if b['username'] != username]
    budgets.append({'username': username, 'budget': str(budget_val)})
    write_csv(BUDGET_FILE, budgets, ['username', 'budget'])
    flash("Budget limit set successfully.", 'success')
    return redirect('/home')


@app.route('/graphs')
def graphs():
    if 'user' not in session:
        return redirect('/')
    return render_template('graphs.html')

# Chart routes for graphs.html buttons
@app.route('/chart/bar')
def chart_bar():
    if 'user' not in session:
        return redirect('/')
    username = session['user']
    expenses = read_csv(EXPENSES_FILE)
    user_expenses = [e for e in expenses if e['username'] == username]

    if not user_expenses:
        return '', 404

    # Aggregate category sums
    category_sums = {}
    for exp in user_expenses:
        amt = float(exp['amount'])
        cat = exp['category']
        category_sums[cat] = category_sums.get(cat, 0) + amt

    categories = list(category_sums.keys())
    values = list(category_sums.values())

    fig, ax = plt.subplots()
    ax.bar(categories, values, color='skyblue')
    ax.set_title('Bar Chart - Expenses by Category')
    ax.set_ylabel('Amount')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/chart/pie')
def chart_pie():
    if 'user' not in session:
        return redirect('/')
    username = session['user']
    expenses = read_csv(EXPENSES_FILE)
    user_expenses = [e for e in expenses if e['username'] == username]

    if not user_expenses:
        return '', 404

    category_sums = {}
    for exp in user_expenses:
        amt = float(exp['amount'])
        cat = exp['category']
        category_sums[cat] = category_sums.get(cat, 0) + amt

    categories = list(category_sums.keys())
    values = list(category_sums.values())

    fig, ax = plt.subplots()
    ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.set_title('Pie Chart - Expenses by Category')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/chart/donut')
def chart_donut():
    if 'user' not in session:
        return redirect('/')
    username = session['user']
    expenses = read_csv(EXPENSES_FILE)
    user_expenses = [e for e in expenses if e['username'] == username]

    if not user_expenses:
        return '', 404

    category_sums = {}
    for exp in user_expenses:
        amt = float(exp['amount'])
        cat = exp['category']
        category_sums[cat] = category_sums.get(cat, 0) + amt

    categories = list(category_sums.keys())
    values = list(category_sums.values())

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3))
    ax.set_title('Donut Chart - Expenses by Category')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/chart/line')
def chart_line():
    if 'user' not in session:
        return redirect('/')
    username = session['user']
    expenses = read_csv(EXPENSES_FILE)
    user_expenses = [e for e in expenses if e['username'] == username]

    if not user_expenses:
        return '', 404

    # Prepare date-wise sums
    df = pd.DataFrame(user_expenses)
    df['amount'] = df['amount'].astype(float)
    df['date'] = pd.to_datetime(df['date'])
    df_sorted = df.sort_values('date')
    daily_sums = df_sorted.groupby('date')['amount'].sum()

    fig, ax = plt.subplots()
    ax.plot(daily_sums.index, daily_sums.values, marker='o', color='green')
    ax.set_title('Line Chart - Expense Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount')
    fig.autofmt_xdate()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/chart/<chart_type>')
def generate_chart(chart_type):
    username = session.get('user')
    if not username:
        return redirect('/')

    expenses = read_csv(EXPENSES_FILE)
    user_expenses = [e for e in expenses if e['username'] == username]

    if not user_expenses:
        return "No data", 404

    fig, ax = plt.subplots(figsize=(10, 6))
    
    dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in user_expenses]
    amounts = [float(e['amount']) for e in user_expenses]

    if chart_type == 'scatter':
        ax.scatter(dates, amounts, c='blue', edgecolors='black')
        ax.set_title("Scatterplot of Expenses Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount")
        ax.grid(True)
    else:
        # Handle other charts (bar, pie, line, etc.)
        pass

    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')

@app.route('/chart/heatmap')
def chart_heatmap():
    username = session.get('user')
    if not username:
        return redirect('/')

    expenses = read_csv(EXPENSES_FILE)
    user_expenses = [e for e in expenses if e['username'] == username]

    if not user_expenses:
        return "No expenses available to generate heatmap.", 400

    df = pd.DataFrame(user_expenses)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['date', 'amount', 'category'])

    pivot = df.pivot_table(values='amount', index='date', columns='category', aggfunc='sum', fill_value=0)

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGnBu")
    plt.title("Heatmap of Expenses by Category and Date")
    plt.xlabel("Category")
    plt.ylabel("Date")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')




@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", 'info')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)                             