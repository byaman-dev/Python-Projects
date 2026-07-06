"""
Project : Calculator
Module  : Foundations
Author  : Aman Kumar
Repository : Python-Projects

Description:
A simple command-line calculator that performs basic arithmetic
operations while demonstrating Python fundamentals such as
functions, conditional statements, loops, and exception handling.
"""


# -------------------------------
# Arithmetic Functions
# -------------------------------

def add(a, b):
    """Return the sum of two numbers."""
    return a + b


def subtract(a, b):
    """Return the difference of two numbers."""
    return a - b


def multiply(a, b):
    """Return the product of two numbers."""
    return a * b


def divide(a, b):
    """Return the quotient of two numbers."""
    if b == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")
    return a / b


# -------------------------------
# Utility Functions
# -------------------------------

def get_number(prompt):
    """
    Prompt the user until a valid number is entered.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.\n")


def display_menu():
    """Display calculator menu."""
    print("\n" + "=" * 40)
    print("         PYTHON CALCULATOR")
    print("=" * 40)
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Exit")
    print("=" * 40)


# -------------------------------
# Main Program
# -------------------------------

def main():
    """Main program loop."""

    while True:

        display_menu()

        choice = input("Select an option (1-5): ")

        if choice == "5":
            print("\nThank you for using the calculator.")
            print("Goodbye!\n")
            break

        if choice not in ["1", "2", "3", "4"]:
            print("\n❌ Invalid menu option.\n")
            continue

        num1 = get_number("Enter first number : ")
        num2 = get_number("Enter second number: ")

        try:

            if choice == "1":
                result = add(num1, num2)
                operation = "+"

            elif choice == "2":
                result = subtract(num1, num2)
                operation = "-"

            elif choice == "3":
                result = multiply(num1, num2)
                operation = "*"

            else:
                result = divide(num1, num2)
                operation = "/"

            print("\n------------------------------")
            print(f"Result : {num1} {operation} {num2} = {result}")
            print("------------------------------")

        except ZeroDivisionError as error:
            print(f"\n❌ {error}")

        input("\nPress Enter to continue...")


# -------------------------------
# Program Entry Point
# -------------------------------

if __name__ == "__main__":
    main()
