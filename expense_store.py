"""
CSV storage helpers for the Expense Tracker.
All expense data is read from and written to expenses.csv.
"""

import csv
import os
from datetime import datetime

# Path to the CSV file (same folder as this script)
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.csv")

# Column names used in the CSV file
FIELDNAMES = ["id", "date", "time", "label", "description", "amount"]


def ensure_csv_exists():
    """Create expenses.csv with a header row if it does not exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def load_expenses():
    """Read all expenses from the CSV file and return them as a list of dictionaries."""
    ensure_csv_exists()
    expenses = []

    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip empty rows
                if not row.get("id"):
                    continue
                try:
                    expenses.append({
                        "id": int(row["id"]),
                        "date": row["date"],
                        "time": row["time"],
                        "label": row["label"],
                        "description": row.get("description", ""),
                        "amount": float(row["amount"]),
                    })
                except (ValueError, KeyError):
                    # Skip rows with invalid data
                    continue
    except FileNotFoundError:
        return []

    return expenses


def save_expenses(expenses):
    """Write the full list of expenses back to the CSV file."""
    ensure_csv_exists()

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        for expense in expenses:
            writer.writerow({
                "id": expense["id"],
                "date": expense["date"],
                "time": expense["time"],
                "label": expense["label"],
                "description": expense["description"],
                "amount": expense["amount"],
            })


def get_next_id(expenses):
    """Return the next available expense ID."""
    if not expenses:
        return 1
    return max(expense["id"] for expense in expenses) + 1


def add_expense(label, description, amount):
    """Add a new expense with auto-generated id, date, and time."""
    expenses = load_expenses()
    now = datetime.now()

    new_expense = {
        "id": get_next_id(expenses),
        "date": now.strftime("%d-%m-%Y"),
        "time": now.strftime("%I:%M %p"),
        "label": label.strip(),
        "description": description.strip() if description else "",
        "amount": amount,
    }

    expenses.append(new_expense)
    save_expenses(expenses)
    return new_expense


def get_expense_by_id(expense_id):
    """Find and return a single expense by its ID, or None if not found."""
    for expense in load_expenses():
        if expense["id"] == expense_id:
            return expense
    return None


def update_expense(expense_id, label, description, amount):
    """Update label, description, and amount for an existing expense."""
    expenses = load_expenses()

    for expense in expenses:
        if expense["id"] == expense_id:
            expense["label"] = label.strip()
            expense["description"] = description.strip() if description else ""
            expense["amount"] = amount
            save_expenses(expenses)
            return True

    return False


def delete_expense(expense_id):
    """Remove an expense and re-number remaining IDs starting from 1."""

    expenses = load_expenses()

    # Check whether the expense exists
    updated = [
        expense
        for expense in expenses
        if expense["id"] != expense_id
    ]

    # Expense was not found
    if len(updated) == len(expenses):
        return False

    # Re-number all remaining expenses
    for index, expense in enumerate(updated, start=1):
        expense["id"] = index

    # Save the updated list
    save_expenses(updated)

    return True


def parse_expense_datetime(expense):
    """Convert an expense's date and time strings into a datetime object for sorting."""
    return datetime.strptime(
        f"{expense['date']} {expense['time']}",
        "%d-%m-%Y %I:%M %p",
    )


def get_month_year_from_date(date_string):
    """Extract MM-YYYY from a DD-MM-YYYY date string."""
    parts = date_string.split("-")
    if len(parts) == 3:
        return f"{parts[1]}-{parts[2]}"
    return ""


def calculate_totals(expenses):
    """Calculate dashboard totals from the expense list (not stored in CSV)."""
    today = datetime.now().strftime("%d-%m-%Y")
    current_month = datetime.now().strftime("%m-%Y")

    total = sum(expense["amount"] for expense in expenses)
    count = len(expenses)
    today_total = sum(expense["amount"] for expense in expenses if expense["date"] == today)
    month_total = sum(
        expense["amount"]
        for expense in expenses
        if get_month_year_from_date(expense["date"]) == current_month
    )

    category_totals = {}
    for expense in expenses:
        label = expense["label"]
        category_totals[label] = category_totals.get(label, 0) + expense["amount"]

    # Sort categories by amount (highest first)
    category_totals = dict(
        sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
    )

    return {
        "total": total,
        "count": count,
        "today_total": today_total,
        "month_total": month_total,
        "category_totals": category_totals,
    }


def filter_and_sort_expenses(
    expenses,
    search="",
    label_filter="",
    date_filter="",
    month_filter="",
    sort="newest",
):
    """Apply search, filters, and sorting to the expense list."""
    results = list(expenses)

    # Case-insensitive search by label, description, or date
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
            if expense["label"].lower() == label_filter.lower()
        ]

    if date_filter:
        results = [expense for expense in results if expense["date"] == date_filter]

    if month_filter:
        results = [
            expense
            for expense in results
            if get_month_year_from_date(expense["date"]) == month_filter
        ]

    if sort == "oldest":
        results.sort(key=parse_expense_datetime)
    elif sort == "highest":
        results.sort(key=lambda expense: expense["amount"], reverse=True)
    elif sort == "lowest":
        results.sort(key=lambda expense: expense["amount"])
    else:
        # Default: newest first
        results.sort(key=parse_expense_datetime, reverse=True)

    return results


def get_unique_labels(expenses):
    """Return a sorted list of unique expense labels."""
    labels = sorted({expense["label"] for expense in expenses})
    return labels
