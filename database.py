
import sqlite3

def connect_db():
    return sqlite3.connect("expenses.db")


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            payment_method TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            month TEXT PRIMARY KEY,
            amount REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_expense(name, amount, category, date, payment_method, description):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (name, amount, category, date, payment_method, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, amount, category, date, payment_method, description))

    conn.commit()
    conn.close()


def get_expenses():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM expenses
        ORDER BY date DESC, id DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def update_expense(expense_id, name, amount, category, date, payment_method, description):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE expenses
        SET name=?, amount=?, category=?, date=?,
            payment_method=?, description=?
        WHERE id=?
    """, (name, amount, category, date, payment_method, description, expense_id))

    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))

    conn.commit()
    conn.close()


def set_budget(month, amount):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO budgets (month, amount)
        VALUES (?, ?)
        ON CONFLICT(month)
        DO UPDATE SET amount=excluded.amount
    """, (month, amount))

    conn.commit()
    conn.close()


def get_budget(month):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT amount FROM budgets WHERE month=?",
        (month,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0
