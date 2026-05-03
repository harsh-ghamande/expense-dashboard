from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()
init_db()
# -------------------------------------------------------------------
@app.route('/')
def home():
    category = request.args.get('category')
    conn = sqlite3.connect('database.db')
    c  = conn.cursor()

    if category:
        c.execute("SELECT * FROM expenses WHERE category = ? ORDER BY date DESC", (category,))
    else:
        c.execute("SELECT * FROM expenses ORDER BY date DESC")
    data = c.fetchall()
    transaction_count = len(data)
    category_totals = {}

    for row in data:
        category = row[2]
        amount = row[1]

        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

    top_category = None
    max_amount = 0

    for category, amount in category_totals.items():
        if amount > max_amount:
            max_amount = amount
            top_category = category

    total = sum([row[1] for row in data if row[1]])
    conn.close()

    return render_template(
        'index.html',
        expenses=data, 
        total=total, 
        category_totals=category_totals,
        top_category=top_category,
        max_amount=max_amount,
        transaction_count=transaction_count
        )


# --------------------------------------------------------------------
@app.route('/add', methods=['POST'])
def add():
    print("ADD ROUTE HIT")

    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']

    if not amount or not category:
        return "Invalid input! Fill all fields"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("INSERT INTO expenses (amount, category, date) VALUES (?,?,?)", 
                (amount, category, date))

    conn.commit()
    conn.close()

    return redirect('/')
# --------------------------------------------------------------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("DELETE FROM expenses WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect('/')
# --------------------------------------------------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        c.execute("UPDATE expenses SET amount = ?, category = ?, date=?  WHERE id = ?",
                    (amount, category, date,  id))
        conn.commit()
        conn.close()

        return redirect('/')
    
    c.execute("SELECT * FROM expenses WHERE id = ?", (id,))
    data = c.fetchone()
    conn.close()

    return render_template('edit.html', expense=data)

    if request.method == 'POST':
        print("EDIT POST HIT")
# --------------------------------------------------------------------
if __name__ == '__main__':
    app.run()