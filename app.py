"""
Flask Expense Tracker - main application file.
Handles web routes, form validation, and connects the UI to CSV storage.
"""

import os
import csv
import expense_store as store
from functools import wraps
from io import StringIO, BytesIO
from openpyxl import Workbook
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    Response,
    send_file,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)

def login_required(function):
    """Allow access only to logged-in users."""

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash(
                "Please login to continue.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return decorated_function

def get_filtered_user_expenses():
    """
    Get the currently logged-in user's expenses
    using the same filters as the All Expenses page.
    """

    user_id = session["user_id"]

    expenses = store.load_expenses(user_id)

    search = request.args.get(
        "search",
        ""
    ).strip()

    label_filter = request.args.get(
        "label",
        ""
    ).strip()

    date_filter = request.args.get(
        "date",
        ""
    ).strip()

    month_filter = request.args.get(
        "month",
        ""
    ).strip()

    sort = request.args.get(
        "sort",
        "newest"
    ).strip()

    filtered_expenses = store.filter_and_sort_expenses(
        expenses,
        search=search,
        label_filter=label_filter,
        date_filter=date_filter,
        month_filter=month_filter,
        sort=sort,
    )

    return filtered_expenses

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name:
            flash(
                "Name is required.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        if not email:
            flash(
                "Email is required.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        if len(password) < 6:
            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        # Check existing user
        existing_user = store.get_user_by_email(
            email
        )

        if existing_user:
            flash(
                "An account with this email already exists.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        # Hash password
        hashed_password = generate_password_hash(
            password
        )

        user_id = store.create_user(
            name,
            email,
            hashed_password
        )

        if not user_id:
            flash(
                "Could not create account.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        # Login user immediately
        session["user_id"] = user_id
        session["user_name"] = name
        session["user_email"] = email

        flash(
            "Account created successfully!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "signup.html"
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = store.get_user_by_email(
            email
        )

        if not user:

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        if not check_password_hash(
            user["password"],
            password
        ):

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        # Create session
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        flash(
            "Welcome back!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )
    
@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )

# Default category options shown in forms
DEFAULT_CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Education",
    "Entertainment",
    "Health",
    "Other",
]


def validate_expense_form(amount_raw, label):
    """
    Validate amount and label from a form submission.
    Returns (amount, error_message). amount is None if validation fails.
    """
    if not label or not label.strip():
        return None, "Label/category cannot be empty."

    if not amount_raw or not str(amount_raw).strip():
        return None, "Amount cannot be empty."

    try:
        amount = float(amount_raw)
    except ValueError:
        return None, "Amount must be a valid number."

    if amount <= 0:
        return None, "Amount must be greater than 0."

    return amount, None


@app.route("/")
@login_required
def dashboard():

    user_id = session["user_id"]

    expenses = store.load_expenses(
        user_id
    )

    totals = store.calculate_totals(
        expenses
    )

    recent_expenses = (
        store.filter_and_sort_expenses(
            expenses,
            sort="newest"
        )[:5]
    )

    return render_template(
        "index.html",
        totals=totals,
        recent_expenses=recent_expenses,
        user_name=session.get("user_name"),
    )

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():

    if request.method == "POST":

        label = request.form.get(
            "label",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        amount_raw = request.form.get(
            "amount",
            ""
        )

        amount, amount_error = validate_expense_form(
            amount_raw,
            label
        )

        if amount_error:

            flash(
                amount_error,
                "error"
            )

            return render_template(
                "add_expense.html",
                form_data=request.form,
            )

        try:

            store.add_expense(
                session["user_id"],
                label,
                description,
                amount
            )

        except Exception:

            flash(
                "Something went wrong while saving the expense.",
                "error"
            )

            return render_template(
                "add_expense.html",
                form_data=request.form,
            )

        flash(
            "Expense added successfully!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "add_expense.html",
        form_data={}
    )

@app.route("/expenses")
@login_required
def view_expenses():

    user_id = session["user_id"]

    expenses = store.load_expenses(
        user_id
    )

    search = request.args.get(
        "search",
        ""
    ).strip()

    label_filter = request.args.get(
        "label",
        ""
    ).strip()

    date_filter = request.args.get(
        "date",
        ""
    ).strip()

    month_filter = request.args.get(
        "month",
        ""
    ).strip()

    sort = request.args.get(
        "sort",
        "newest"
    ).strip()

    filtered_expenses = (
        store.filter_and_sort_expenses(
            expenses,
            search=search,
            label_filter=label_filter,
            date_filter=date_filter,
            month_filter=month_filter,
            sort=sort,
        )
    )

    all_labels = store.get_unique_labels(
        expenses
    )

    return render_template(
        "expenses.html",
        expenses=filtered_expenses,
        all_labels=all_labels,
        search=search,
        label_filter=label_filter,
        date_filter=date_filter,
        month_filter=month_filter,
        sort=sort,
        total_count=len(expenses),
        filtered_count=len(filtered_expenses),
    )

@app.route(
    "/edit/<int:expense_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_expense(expense_id):

    user_id = session["user_id"]

    expense = store.get_expense_by_id(
        expense_id,
        user_id
    )

    if not expense:

        flash(
            "Expense not found.",
            "error"
        )

        return redirect(
            url_for("view_expenses")
        )

    if request.method == "POST":

        label = request.form.get(
            "label",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        amount_raw = request.form.get(
            "amount",
            ""
        )

        amount, amount_error = validate_expense_form(
            amount_raw,
            label
        )

        if amount_error:

            flash(
                amount_error,
                "error"
            )

            return render_template(
                "edit_expense.html",
                expense=expense,
                form_data=request.form,
            )

        try:

            updated = store.update_expense(
                expense_id,
                user_id,
                label,
                description,
                amount
            )

            if not updated:

                flash(
                    "Expense not found.",
                    "error"
                )

                return redirect(
                    url_for("view_expenses")
                )

        except Exception:

            flash(
                "Something went wrong while updating the expense.",
                "error"
            )

            return render_template(
                "edit_expense.html",
                expense=expense,
                form_data=request.form,
            )

        flash(
            "Expense updated successfully!",
            "success"
        )

        return redirect(
            url_for("view_expenses")
        )

    return render_template(
        "edit_expense.html",
        expense=expense,
        form_data={}
    )   
    
@app.route("/export/csv")
@login_required
def export_csv():
    """Download filtered expenses as CSV."""

    expenses = get_filtered_user_expenses()

    output = StringIO()

    writer = csv.writer(output)

    # CSV header
    writer.writerow([
        "ID",
        "Date",
        "Time",
        "Label",
        "Description",
        "Amount"
    ])

    # CSV data
    for expense in expenses:

        writer.writerow([
            expense["id"],
            expense["date"],
            expense["time"],
            expense["label"],
            expense["description"],
            f"{expense['amount']:.2f}",
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv",
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=expense_tracker.csv"
    )

    return response    

@app.route("/export/excel")
@login_required
def export_excel():
    """Download filtered expenses as Excel."""

    expenses = get_filtered_user_expenses()

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Expenses"

    # Header
    worksheet.append([
        "ID",
        "Date",
        "Time",
        "Label",
        "Description",
        "Amount"
    ])

    # Data
    for expense in expenses:

        worksheet.append([
            expense["id"],
            expense["date"],
            expense["time"],
            expense["label"],
            expense["description"],
            expense["amount"],
        ])

    # Format amount column
    for cell in worksheet["F"][1:]:
        cell.number_format = '₹#,##0.00'

    # Adjust column widths
    worksheet.column_dimensions["A"].width = 10
    worksheet.column_dimensions["B"].width = 15
    worksheet.column_dimensions["C"].width = 15
    worksheet.column_dimensions["D"].width = 25
    worksheet.column_dimensions["E"].width = 40
    worksheet.column_dimensions["F"].width = 15

    # Create Excel file in memory
    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="expense_tracker.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet"
        ),
    )
    
@app.route(
    "/delete/<int:expense_id>",
    methods=["POST"]
)
@login_required
def delete_expense(expense_id):

    user_id = session["user_id"]

    try:

        deleted = store.delete_expense(
            expense_id,
            user_id
        )

        if deleted:

            flash(
                "Expense deleted successfully!",
                "success"
            )

        else:

            flash(
                "Expense not found.",
                "error"
            )

    except Exception:

        flash(
            "Something went wrong while deleting the expense.",
            "error"
        )

    return redirect(
        url_for("view_expenses")
    )
    
store.ensure_database()
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),
        debug=True
    )