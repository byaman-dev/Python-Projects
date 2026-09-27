"""
Project : Expense Tracker (SQLite version)
Module  : Foundations -> Automation (storage upgrade)
Author  : Aman Kumar (upgraded for review)
Repository : Python-Projects

Description:
A command-line expense tracker that allows users to record,
view, calculate, and delete daily expenses.

Changes from the original version:
- Expenses are now stored in a local SQLite database
  (expenses.db) instead of an in-memory Python list, so data
  survives between runs.
- Add / View / Delete / Total all operate against the database
  using SQL instead of list operations.
- Delete now works by a permanent expense ID rather than a
  position in the currently displayed list, so numbers don't
  shift around after a delete.
- A "date" field was added, since a real expense tracker needs
  one and SQLite makes it easy to store.

Everything else — the menu, the prompts, the input validation,
the look of the output — is kept exactly as it was, so this
still reads like the same project, just with real storage.
"""

import sqlite3
from datetime import date


DB_FILE = "expenses.db"


# ----------------------------------------------------
# Database Setup
# ----------------------------------------------------

def get_connection():
    """
    Open a connection to the SQLite database.
    """
    return sqlite3.connect(DB_FILE)


def init_db():
    """
    Create the expenses table if it doesn't already exist.
    Runs once at program start; safe to call every time.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT NOT NULL,
            description TEXT,
            amount      REAL NOT NULL,
            date        TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ----------------------------------------------------
# Utility Functions
# ----------------------------------------------------

def get_positive_number(prompt):
    """
    Prompt the user until a valid positive number is entered.
    """

    while True:

        try:

            amount = float(input(prompt))

            if amount > 0:
                return amount

            print("❌ Please enter a number greater than zero.\n")

        except ValueError:

            print("❌ Invalid input. Please enter a valid number.\n")


def get_menu_choice():
    """
    Prompt the user until a valid menu option is selected.
    """

    while True:

        choice = input("Select an option (1-5): ")

        if choice in ("1", "2", "3", "4", "5"):
            return choice

        print("\n❌ Invalid menu option.\n")


# ----------------------------------------------------
# Expense Functions
# ----------------------------------------------------

def add_expense():
    """
    Add a new expense to the database.
    """

    print("\nAdd New Expense")
    print("-" * 30)

    category = input("Category    : ")
    description = input("Description : ")

    amount = get_positive_number("Amount (₹) : ")
    today = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (category, description, amount, date) "
        "VALUES (?, ?, ?, ?)",
        (category, description, amount, today)
    )

    conn.commit()
    conn.close()

    print("\n✅ Expense added successfully.")


def fetch_all_expenses():
    """
    Return all expenses from the database, oldest first.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, category, description, amount, date "
        "FROM expenses ORDER BY id"
    )
    rows = cursor.fetchall()

    conn.close()
    return rows


def view_expenses():
    """
    Display all recorded expenses.
    """

    rows = fetch_all_expenses()

    if len(rows) == 0:

        print("\nNo expenses recorded.\n")
        return

    print("\n" + "=" * 70)
    print("ID    Date        Category      Description           Amount")
    print("=" * 70)

    for row in rows:

        expense_id, category, description, amount, expense_date = row

        print(
            f"{expense_id:<6}"
            f"{expense_date:<12}"
            f"{category:<14}"
            f"{(description or ''):<22}"
            f"₹{amount}"
        )


def show_total():
    """
    Display the total amount spent.
    """

    rows = fetch_all_expenses()

    if len(rows) == 0:

        print("\nNo expenses recorded.\n")
        return

    total = sum(row[3] for row in rows)

    print("\n------------------------------")
    print(f"Total Expenses : ₹{total}")
    print("------------------------------")


def delete_expense():
    """
    Delete an expense by its ID.
    """

    rows = fetch_all_expenses()

    if len(rows) == 0:

        print("\nNo expenses recorded.\n")
        return

    view_expenses()

    while True:

        try:

            expense_id = int(
                input("\nEnter expense ID to delete: ")
            )

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT description FROM expenses WHERE id = ?",
                (expense_id,)
            )
            match = cursor.fetchone()

            if match is None:
                print("❌ Invalid expense ID.")
                conn.close()
                continue

            cursor.execute(
                "DELETE FROM expenses WHERE id = ?",
                (expense_id,)
            )
            conn.commit()
            conn.close()

            print(f"\n✅ '{match[0]}' deleted successfully.")
            break

        except ValueError:

            print("❌ Please enter a valid number.")


# ----------------------------------------------------
# Display Menu
# ----------------------------------------------------

def display_menu():
    """
    Display application menu.
    """

    print("\n" + "=" * 45)
    print("          EXPENSE TRACKER")
    print("=" * 45)
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Show Total Expenses")
    print("4. Delete Expense")
    print("5. Exit")
    print("=" * 45)


# ----------------------------------------------------
# Main Program
# ----------------------------------------------------

def main():

    init_db()

    while True:

        display_menu()

        choice = get_menu_choice()

        if choice == "1":

            add_expense()

        elif choice == "2":

            view_expenses()

        elif choice == "3":

            show_total()

        elif choice == "4":

            delete_expense()

        else:

            print("\nThank you for using Expense Tracker.")
            print("Goodbye!\n")

            break

        input("\nPress Enter to continue...")


# ----------------------------------------------------
# Program Entry Point
# ----------------------------------------------------

if __name__ == "__main__":
    main()
