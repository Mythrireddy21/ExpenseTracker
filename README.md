# 💸 Expense Tracker

An interactive, user-friendly web application that helps you **track expenses**, **manage budgets**, and **analyze spending patterns**. Built with **Flask (Python)** for the backend, **CSV** for storage, and powerful visualization using **Matplotlib**, **Seaborn**, **Pandas**, and **NumPy**. The UI is designed with **HTML, CSS, and JavaScript** for a clean and colorful experience.

---

## 🚀 Features

- 🔐 **User Authentication** – Register, Login, Logout securely
- 🧾 **Expense Management** – Add and edit your daily expenses
- 👤 **Profile Editing** – Update your user email or password
- 💰 **Set Budget Limit** – Define and monitor your monthly expense cap
- 📈 **Generate Graphs**:
  - Bar, Pie, Donut, and Line charts (using Matplotlib)
  - Scatter plots and Heatmaps (using Seaborn)
- 🌍 **Multi-Currency Support** – Convert expenses using real-time exchange rates
- ⚠️ **Budget Alerts** – Notifies users when spending exceeds their set budget

---

## 🛠️ Technologies Used

| Layer         | Tools/Libraries                                                                 |
|---------------|----------------------------------------------------------------------------------|
| Backend       | Python 3, Flask                                                                 |
| Frontend      | HTML5, CSS3, JavaScript                                                          |
| Data Storage  | CSV files (`users.csv`, `expenses.csv`, `budget.csv`)                           |
| Visualization | Matplotlib, Seaborn, Pandas, NumPy                                               |

---

## 📁 Project Structure

```

ExpenseTracker/
│
├── app.py                      # Main Flask app
├── users.csv                   # User credentials
├── expenses.csv                # Expense entries
├── budget.csv                  # Monthly budget per user
│
├── static/
│   ├── css/
│   │   └── style.css           # Styling
│   ├── js/
│   │   └── script.js           # JavaScript for interactivity
│   └── images/                 # Icons / Screenshots
│
├── templates/
│   ├── login.html              # Login Page
│   ├── register.html           # User Registration
│   ├── dashboard.html          # Expense Summary Dashboard
│   ├── add\_expense.html        # Add Expense Form
│   ├── edit\_expense.html       # Edit Expense Page
│   ├── edit\_profile.html       # Profile Edit Page
│   └── graphs.html             # Charts Visualization
│
├── requirements.txt            # Required Python packages
└── .gitignore                  # Git ignore rules

````

---

## ⚙️ Installation and Running the App

### ✅ Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional)

---

### 🧭 Step-by-Step Guide

1. **Clone the repository**

```bash
git clone https://github.com/Mythrireddy21/ExpenseTracker.git
cd ExpenseTracker
````

2. **Create a virtual environment (optional but recommended)**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install the required packages**

```bash
pip install -r requirements.txt
```

4. **Run the Flask app**

```bash
python app.py
```

5. **Open your browser**

Visit:

```
http://127.0.0.1:5000
```

---

## 👨‍💻 Usage

* ✅ Register a new account
* 🔐 Log in with your credentials
* ➕ Add new expenses and track them
* 💼 Set a monthly budget
* 🧮 Convert between currencies
* 📊 Generate detailed financial graphs (bar, pie, donut, line, scatter, heatmap)
* ✏️ Edit your profile and expenses
* 🚪 Logout when you're done

---

## 📊 Graphs & Charts Overview

| Chart Type   | Description                            |
| ------------ | -------------------------------------- |
| Bar Chart    | Total expenses per category            |
| Pie Chart    | Category distribution of spending      |
| Donut Chart  | Variant of pie chart for emphasis      |
| Line Chart   | Expense trends over time               |
| Scatter Plot | Expense amounts over dates             |
| Heatmap      | Category vs. Day density visualization |

---

## 🔮 Future Enhancements

* 🔒 Password hashing & secure storage
* 📱 Mobile-responsive design
* 📤 Export reports (PDF/Excel)
* 🤖 AI-based budget insights and savings tips
* 🔎 Filter/sort/search expenses

---

## 🤝 Contributing

Contributions are welcome! Fork this repository and open a pull request for new features, bug fixes, or improvements.

---

## 📜 License

Licensed under the **MIT License**. Feel free to use and modify with attribution.

---

## 📬 Contact

* 👤 Name: Mythri Reddy
* 📧 Email: [mythrireddybuttemgari@gmail.com](mailto:mythrireddybuttemgari@gmail.com)
* 🌐 GitHub: [@Mythrireddy21](https://github.com/Mythrireddy21)

---

💡 **Tip:** Track smart, spend smarter! Thank you for using **ExpenseTracker** 💰📊

##live demo :
 https://expensetracker-mythrireddy.onrender.com
```

