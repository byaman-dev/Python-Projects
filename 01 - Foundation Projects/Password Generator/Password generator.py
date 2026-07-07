"""
Project : Password Generator
Module  : Foundations
Author  : Aman Kumar
Repository : Python-Projects

Description:
A command-line password generator that creates secure, customizable
passwords using uppercase letters, lowercase letters, numbers,
and special characters.

This project demonstrates Python fundamentals including functions,
loops, input validation, string manipulation, and the use of
Python's standard libraries.
"""

import random
import string


# ----------------------------------------------------
# Utility Functions
# ----------------------------------------------------

def get_positive_integer(prompt):
    """
    Prompt the user until a valid positive integer is entered.
    """
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            else:
                print("❌ Please enter a number greater than zero.\n")
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.\n")


def get_yes_no(prompt):
    """
    Prompt the user until Y or N is entered.
    """
    while True:
        choice = input(prompt).strip().upper()

        if choice in ("Y", "N"):
            return choice == "Y"

        print("❌ Please enter Y or N.\n")


# ----------------------------------------------------
# Password Generator
# ----------------------------------------------------

def generate_password(length, upper, lower, numbers, symbols):
    """
    Generate a secure password based on user preferences.
    Ensures that at least one character from every selected
    category is included.
    """

    character_pool = []
    password = []

    if upper:
        character_pool.extend(string.ascii_uppercase)
        password.append(random.choice(string.ascii_uppercase))

    if lower:
        character_pool.extend(string.ascii_lowercase)
        password.append(random.choice(string.ascii_lowercase))

    if numbers:
        character_pool.extend(string.digits)
        password.append(random.choice(string.digits))

    if symbols:
        character_pool.extend(string.punctuation)
        password.append(random.choice(string.punctuation))

    if not character_pool:
        raise ValueError(
            "At least one character type must be selected."
        )

    while len(password) < length:
        password.append(random.choice(character_pool))

    random.shuffle(password)

    return "".join(password)


# ----------------------------------------------------
# Menu
# ----------------------------------------------------

def display_menu():
    """
    Display the application banner.
    """

    print("\n" + "=" * 45)
    print("        PYTHON PASSWORD GENERATOR")
    print("=" * 45)


# ----------------------------------------------------
# Main Program
# ----------------------------------------------------

def main():

    while True:

        display_menu()

        length = get_positive_integer(
            "Password Length: "
        )

        print()

        use_upper = get_yes_no(
            "Include Uppercase Letters? (Y/N): "
        )

        use_lower = get_yes_no(
            "Include Lowercase Letters? (Y/N): "
        )

        use_numbers = get_yes_no(
            "Include Numbers? (Y/N): "
        )

        use_symbols = get_yes_no(
            "Include Special Characters? (Y/N): "
        )

        try:

            password = generate_password(
                length,
                use_upper,
                use_lower,
                use_numbers,
                use_symbols
            )

            print("\n" + "-" * 45)
            print("Generated Password")
            print("-" * 45)
            print(password)
            print("-" * 45)

        except ValueError as error:
            print(f"\n❌ {error}")

        again = get_yes_no(
            "\nGenerate another password? (Y/N): "
        )

        if not again:
            print("\nThank you for using Password Generator.")
            print("Goodbye!\n")
            break


# ----------------------------------------------------
# Program Entry Point
# ----------------------------------------------------

if __name__ == "__main__":
    main()