"""
MySQL storage helpers for the Expense Tracker.

All expenses belong to a specific user.
"""

import os
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "expense_tracker"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# SSL configuration for online MySQL
DB_SSL_CA = os.getenv("DB_SSL_CA")

if DB_SSL_CA:
    DB_CONFIG["ssl_ca"] = DB_SSL_CA
    DB_CONFIG["ssl_verify_cert"] = True


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    """Create and return a MySQL connection."""

    return mysql.connector.connect(**DB_CONFIG)


# ==========================================
# DATABASE SETUP
# ==========================================

def ensure_database():
    """Create required tables if they don't exist."""

    connection = get_connection()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            label VARCHAR(100) NOT NULL,
            description VARCHAR(255),
            amount DECIMAL(10, 2) NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()

    cursor.close()
    connection.close()


# ==========================================
# USER FUNCTIONS
# ==========================================

def create_user(name, email, password):
    """Create a new user."""

    connection = get_connection()
    cursor = connection.cursor()

    sql = """
        INSERT INTO users
        (name, email, password)
        VALUES (%s, %s, %s)
    """

    try:

        cursor.execute(
            sql,
            (
                name.strip(),
                email.strip().lower(),
                password,
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        return user_id

    except mysql.connector.IntegrityError:

        connection.rollback()

        return None

    finally:

        cursor.close()
        connection.close()


def get_user_by_email(email):
    """Find a user by email."""

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name, email, password
        FROM users
        WHERE email = %s
        """,
        (email.strip().lower(),)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


def get_user_by_id(user_id):
    """Find a user by ID."""

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE id = %s
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


# ==========================================
# EXPENSE FUNCTIONS
# ==========================================

def load_expenses(user_id):
    """Load expenses belonging only to the logged-in user."""

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            DATE_FORMAT(date, '%d-%m-%Y') AS date,
            DATE_FORMAT(time, '%h:%i %p') AS time,
            label,
            description,
            amount
        FROM expenses
        WHERE user_id = %s
        ORDER BY id
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    expenses = []

    for row in rows:

        expenses.append({
            "id": int(row["id"]),
            "date": row["date"],
            "time": row["time"],
            "label": row["label"],
            "description": row["description"] or "",
            "amount": float(row["amount"]),
        })

    return expenses


def add_expense(user_id, label, description, amount):
    """Add an expense for a specific user."""

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now()

    sql = """
        INSERT INTO expenses
        (
            user_id,
            date,
            time,
            label,
            description,
            amount
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (
            user_id,
            now.date(),
            now.time(),
            label.strip(),
            description.strip() if description else "",
            amount,
        )
    )

    connection.commit()

    expense_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "id": expense_id,
        "date": now.strftime("%d-%m-%Y"),
        "time": now.strftime("%I:%M %p"),
        "label": label.strip(),
        "description": description.strip() if description else "",
        "amount": amount,
    }


def get_expense_by_id(expense_id, user_id):
    """
    Get an expense only if it belongs to the logged-in user.
    """

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            DATE_FORMAT(date, '%d-%m-%Y') AS date,
            DATE_FORMAT(time, '%h:%i %p') AS time,
            label,
            description,
            amount
        FROM expenses
        WHERE id = %s
        AND user_id = %s
        """,
        (expense_id, user_id)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        return None

    return {
        "id": int(row["id"]),
        "date": row["date"],
        "time": row["time"],
        "label": row["label"],
        "description": row["description"] or "",
        "amount": float(row["amount"]),
    }


def update_expense(
    expense_id,
    user_id,
    label,
    description,
    amount
):
    """
    Update an expense only if it belongs
    to the logged-in user.
    """

    connection = get_connection()
    cursor = connection.cursor()

    sql = """
        UPDATE expenses

        SET
            label = %s,
            description = %s,
            amount = %s

        WHERE id = %s
        AND user_id = %s
    """

    cursor.execute(
        sql,
        (
            label.strip(),
            description.strip() if description else "",
            amount,
            expense_id,
            user_id,
        )
    )

    updated = cursor.rowcount > 0

    connection.commit()

    cursor.close()
    connection.close()

    return updated


def delete_expense(expense_id, user_id):
    """
    Delete an expense only if it belongs
    to the logged-in user.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM expenses

        WHERE id = %s
        AND user_id = %s
        """,
        (
            expense_id,
            user_id,
        )
    )

    deleted = cursor.rowcount > 0

    connection.commit()

    cursor.close()
    connection.close()

    return deleted


# ==========================================
# DATE / FILTER FUNCTIONS
# ==========================================

def parse_expense_datetime(expense):
    """Convert date and time to datetime."""

    return datetime.strptime(
        f"{expense['date']} {expense['time']}",
        "%d-%m-%Y %I:%M %p",
    )


def get_month_year_from_date(date_string):
    """Extract MM-YYYY from DD-MM-YYYY."""

    parts = date_string.split("-")

    if len(parts) == 3:
        return f"{parts[1]}-{parts[2]}"

    return ""


# ==========================================
# DASHBOARD TOTALS
# ==========================================

def calculate_totals(expenses):
    """Calculate dashboard totals."""

    today = datetime.now().strftime("%d-%m-%Y")
    current_month = datetime.now().strftime("%m-%Y")

    total = sum(
        expense["amount"]
        for expense in expenses
    )

    count = len(expenses)

    today_total = sum(
        expense["amount"]
        for expense in expenses
        if expense["date"] == today
    )

    month_total = sum(
        expense["amount"]
        for expense in expenses
        if get_month_year_from_date(
            expense["date"]
        ) == current_month
    )

    category_totals = {}

    for expense in expenses:

        label = expense["label"]

        category_totals[label] = (
            category_totals.get(label, 0)
            + expense["amount"]
        )

    category_totals = dict(
        sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    return {
        "total": total,
        "count": count,
        "today_total": today_total,
        "month_total": month_total,
        "category_totals": category_totals,
    }


# ==========================================
# SEARCH / FILTER
# ==========================================

def filter_and_sort_expenses(
    expenses,
    search="",
    label_filter="",
    date_filter="",
    month_filter="",
    sort="newest",
):
    """Apply search, filters and sorting."""

    results = list(expenses)

    if search:

        search_lower = search.lower()

        results = [
            expense
            for expense in results
            if search_lower in expense["label"].lower()
            or search_lower in expense["description"].lower()
            or search_lower in expense["date"].lower()
        ]

    if label_filter:

        results = [
            expense
            for expense in results
            if expense["label"].lower()
            == label_filter.lower()
        ]

    if date_filter:

        results = [
            expense
            for expense in results
            if expense["date"] == date_filter
        ]

    if month_filter:

        results = [
            expense
            for expense in results
            if get_month_year_from_date(
                expense["date"]
            ) == month_filter
        ]

    if sort == "oldest":

        results.sort(
            key=parse_expense_datetime
        )

    elif sort == "highest":

        results.sort(
            key=lambda expense: expense["amount"],
            reverse=True
        )

    elif sort == "lowest":

        results.sort(
            key=lambda expense: expense["amount"]
        )

    else:

        results.sort(
            key=parse_expense_datetime,
            reverse=True
        )

    return results


def get_unique_labels(expenses):
    """Return sorted unique labels."""

    return sorted({
        expense["label"]
        for expense in expenses
    })