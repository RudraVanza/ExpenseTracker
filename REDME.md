Expense Tracker

A simple web application to track daily expenses. Built with Flask, HTML, Tailwind CSS, and CSV file storage — no database required.

Features





Dashboard — total spent, expense count, today's spending, monthly total, recent expenses, category breakdown



Add Expense — auto-generated ID, date, and time



View All Expenses — responsive table with edit and delete actions



Edit Expense — update amount, label, and description (ID, date, time stay unchanged)



Delete Expense — with confirmation prompt



Search — by label, description, or date (case-insensitive)



Filter — by category, date, or month



Sort — newest, oldest, highest amount, lowest amount



Validation — friendly error messages for invalid input



Flash messages — success and error feedback



Technologies Used





Python 3



Flask



Jinja2 templates



HTML5



Tailwind CSS (via CDN)



CSV file storage (Python csv module)



Installation



1. Clone or download the project

Navigate to the project folder:

cd ExpenseTracker



2. Create a virtual environment

Windows:

python -m venv venv
venv\Scripts\activate

macOS / Linux:

python3 -m venv venv
source venv/bin/activate



3. Install dependencies

pip install -r requirements.txt



4. Run the application

python app.py



5. Open in your browser

Visit:

http://127.0.0.1:5000

You should see the dashboard. Use the sidebar to add expenses and view all records.

Project Structure

ExpenseTracker/
│
├── app.py                 # Flask routes and form handling
├── expense_store.py       # CSV read/write functions
├── expenses.csv           # Data file (created automatically)
├── requirements.txt       # Python dependencies
├── README.md
│
├── templates/
│   ├── base.html          # Layout, navigation, flash messages
│   ├── index.html         # Dashboard
│   ├── add_expense.html   # Add expense form
│   ├── edit_expense.html  # Edit expense form
│   └── expenses.html      # All expenses with search/filter
│
└── static/                # Reserved for future static files



How CSV Storage Works

All expense data is stored in expenses.csv with these columns:

id,date,time,label,description,amount
1,10-08-2026,10:30 AM,Food,Lunch,250
2,10-08-2026,02:15 PM,Travel,Auto,120





The CSV file is created automatically on first run if it does not exist.



Totals are never stored in the CSV — they are calculated in Python each time the dashboard loads.



Functions in expense_store.py handle all file operations:





load_expenses() — read all rows



save_expenses() — write all rows



add_expense() — append a new expense



update_expense() — modify an existing expense



delete_expense() — remove an expense by ID



Default Categories

Food, Travel, Shopping, Bills, Education, Entertainment, Health, Other

You can also enter a custom label by selecting Other.

License

Free to use for learning purposes.