from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

# DB setup
def init_db():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
        acc_no INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        balance REAL NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create", methods=["POST"])
def create_account():
    acc_no = request.form["acc_no"]
    name = request.form["name"]
    balance = request.form["balance"]

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?)", (acc_no, name, balance))
        conn.commit()
        flash("✅ Account created successfully!", "success")
    except sqlite3.IntegrityError:
        flash("❌ Account number already exists!", "error")
    conn.close()
    return redirect("/")

@app.route("/deposit", methods=["POST"])
def deposit():
    acc_no = request.form["acc_no"]
    amount = float(request.form["amount"])

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE acc_no = ?", (acc_no,))
    data = cursor.fetchone()
    if data:
        new_balance = data[0] + amount
        cursor.execute("UPDATE accounts SET balance = ? WHERE acc_no = ?", (new_balance, acc_no))
        conn.commit()
        flash(f"✅ Deposited ₹{amount}. New Balance: ₹{new_balance}", "success")
    else:
        flash("❌ Account not found!", "error")
    conn.close()
    return redirect("/")

@app.route("/withdraw", methods=["POST"])
def withdraw():
    acc_no = request.form["acc_no"]
    amount = float(request.form["amount"])

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE acc_no = ?", (acc_no,))
    data = cursor.fetchone()
    if data:
        if data[0] >= amount:
            new_balance = data[0] - amount
            cursor.execute("UPDATE accounts SET balance = ? WHERE acc_no = ?", (new_balance, acc_no))
            conn.commit()
            flash(f"✅ Withdrawn ₹{amount}. New Balance: ₹{new_balance}", "success")
        else:
            flash("❌ Insufficient balance!", "error")
    else:
        flash("❌ Account not found!", "error")
    conn.close()
    return redirect("/")

@app.route("/balance", methods=["POST"])
def check_balance():
    acc_no = request.form["acc_no"]

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, balance FROM accounts WHERE acc_no = ?", (acc_no,))
    data = cursor.fetchone()
    conn.close()

    if data:
        flash(f"👤 {data[0]} | 💰 Balance: ₹{data[1]}", "success")
    else:
        flash("❌ Account not found!", "error")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
