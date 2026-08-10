"""
Flask Expense Tracker - main application file.
Handles web routes, form validation, and connects the UI to CSV storage.
"""

from flask import Flask, render_template, request, redirect, url_for, flash

import expense_store as store

app = Flask(__name__)
app.secret_key = "expense-tracker-secret-key-change-in-production"

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
def dashboard():
    """Dashboard with totals, recent expenses, and category breakdown."""
    expenses = store.load_expenses()
    totals = store.calculate_totals(expenses)

    # Show the 5 most recent expenses
    recent_expenses = store.filter_and_sort_expenses(expenses, sort="newest")[:5]

    return render_template(
        "index.html",
        totals=totals,
        recent_expenses=recent_expenses,
        categories=DEFAULT_CATEGORIES,
    )


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    """Show the add-expense form or save a new expense."""

    if request.method == "POST":

        label = request.form.get("label", "").strip()
        description = request.form.get("description", "").strip()
        amount_raw = request.form.get("amount", "")

        # Validate the form
        amount, amount_error = validate_expense_form(
            amount_raw,
            label
        )

        if amount_error:
            flash(amount_error, "error")

            return render_template(
                "add_expense.html",
                form_data=request.form,
            )

        # Try to save the expense
        try:
            store.add_expense(
                label,
                description,
                amount
            )

        except PermissionError:
            flash(
                "Please close the expenses.csv file before adding an expense.",
                "permission_error"
            )

            return render_template(
                "add_expense.html",
                form_data=request.form,
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

        # Successfully saved
        flash(
            "Expense added successfully!",
            "success"
        )

        return redirect(url_for("dashboard"))

    return render_template(
        "add_expense.html",
        form_data={},
    )

@app.route("/expenses")
def view_expenses():
    """View all expenses with search, filter, and sort options."""
    expenses = store.load_expenses()

    search = request.args.get("search", "").strip()
    label_filter = request.args.get("label", "").strip()
    date_filter = request.args.get("date", "").strip()
    month_filter = request.args.get("month", "").strip()
    sort = request.args.get("sort", "newest").strip()

    filtered_expenses = store.filter_and_sort_expenses(
        expenses,
        search=search,
        label_filter=label_filter,
        date_filter=date_filter,
        month_filter=month_filter,
        sort=sort,
    )

    all_labels = store.get_unique_labels(expenses)

    return render_template(
        "expenses.html",
        expenses=filtered_expenses,
        all_labels=all_labels,
        categories=DEFAULT_CATEGORIES,
        search=search,
        label_filter=label_filter,
        date_filter=date_filter,
        month_filter=month_filter,
        sort=sort,
        total_count=len(expenses),
        filtered_count=len(filtered_expenses),
    )


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    """Edit an existing expense."""

    expense = store.get_expense_by_id(expense_id)

    if not expense:
        flash("Expense not found.", "error")
        return redirect(url_for("view_expenses"))

    if request.method == "POST":

        label = request.form.get("label", "").strip()
        description = request.form.get("description", "").strip()
        amount_raw = request.form.get("amount", "")

        amount, amount_error = validate_expense_form(
            amount_raw,
            label
        )

        if amount_error:
            flash(amount_error, "error")

            return render_template(
                "edit_expense.html",
                expense=expense,
                form_data=request.form,
            )

        try:
            store.update_expense(
                expense_id,
                label,
                description,
                amount
            )

        except PermissionError:
            flash(
                "Please close the expenses.csv file before editing an expense.",
                "permission_error"
            )

            return render_template(
                "edit_expense.html",
                expense=expense,
                form_data=request.form,
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

        return redirect(url_for("view_expenses"))

    return render_template(
        "edit_expense.html",
        expense=expense,
        form_data={},
    )
    
@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    """Delete an expense."""

    try:
        deleted = store.delete_expense(expense_id)

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

    except PermissionError:
        flash(
            "Please close the expenses.csv file before deleting an expense.",
            "permission_error"
        )

    except Exception:
        flash(
            "Something went wrong while deleting the expense.",
            "error"
        )

    return redirect(url_for("view_expenses"))
if __name__ == "__main__":
    store.ensure_csv_exists()
    app.run(debug=True)
