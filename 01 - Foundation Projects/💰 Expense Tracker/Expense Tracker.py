"""
Project : Expense Tracker
Module  : Foundations
Author  : Aman Kumar
Repository : Python-Projects

Description:
A command-line expense tracker that allows users to record,
view, calculate, and delete daily expenses.

This project demonstrates Python fundamentals including
functions, lists, dictionaries, loops, input validation,
and exception handling.
"""


# ----------------------------------------------------
# Data Storage
# ----------------------------------------------------

expenses = []


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
    Add a new expense.
    """

    print("\nAdd New Expense")
    print("-" * 30)

    category = input("Category    : ")
    description = input("Description : ")

    amount = get_positive_number("Amount (₹) : ")

    expense = {
        "category": category,
        "description": description,
        "amount": amount
    }

    expenses.append(expense)

    print("\n✅ Expense added successfully.")


def view_expenses():
    """
    Display all recorded expenses.
    """

    if len(expenses) == 0:

        print("\nNo expenses recorded.\n")
        return

    print("\n" + "=" * 60)
    print("No.  Category      Description           Amount")
    print("=" * 60)

    number = 1

    for expense in expenses:

        print(
            f"{number:<4}"
            f"{expense['category']:<14}"
            f"{expense['description']:<22}"
            f"₹{expense['amount']}"
        )

        number += 1


def show_total():
    """
    Display the total amount spent.
    """

    if len(expenses) == 0:

        print("\nNo expenses recorded.\n")
        return

    total = 0

    for expense in expenses:

        total += expense["amount"]

    print("\n------------------------------")
    print(f"Total Expenses : ₹{total}")
    print("------------------------------")


def delete_expense():
    """
    Delete an expense.
    """

    if len(expenses) == 0:

        print("\nNo expenses recorded.\n")
        return

    view_expenses()

    while True:

        try:

            expense_number = int(
                input("\nEnter expense number to delete: ")
            )

            if 1 <= expense_number <= len(expenses):

                deleted = expenses.pop(expense_number - 1)

                print(
                    f"\n✅ '{deleted['description']}' deleted successfully."
                )

                break

            print("❌ Invalid expense number.")

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
