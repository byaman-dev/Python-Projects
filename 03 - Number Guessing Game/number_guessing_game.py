"""
Project : Number Guessing Game
Module  : Foundations
Author  : Aman Kumar
Repository : Python-Projects

Description:
A command-line number guessing game that allows the user
to choose a difficulty level and guess a randomly generated
number. The project demonstrates Python fundamentals such
as loops, functions, conditional statements, input validation,
and the random module.
"""

import random


# ----------------------------------------------------
# Utility Functions
# ----------------------------------------------------

def get_menu_choice():
    """
    Prompt the user until a valid difficulty level is selected.
    """

    while True:

        print("\nChoose Difficulty")
        print("1. Easy (1 - 10)")
        print("2. Medium (1 - 50)")
        print("3. Hard (1 - 100)")
        print("4. Exit")

        choice = input("\nSelect an option (1-4): ")

        if choice in ("1", "2", "3", "4"):
            return choice

        print("\n❌ Invalid option. Please try again.")


def get_guess(minimum, maximum):
    """
    Prompt the user until a valid number is entered.
    """

    while True:

        try:

            guess = int(
                input(f"Enter your guess ({minimum}-{maximum}): ")
            )

            if minimum <= guess <= maximum:
                return guess

            print(
                f"❌ Please enter a number between {minimum} and {maximum}."
            )

        except ValueError:

            print("❌ Invalid input. Please enter a valid number.")


def get_yes_no(prompt):
    """
    Prompt the user until Y or N is entered.
    """

    while True:

        choice = input(prompt).strip().upper()

        if choice in ("Y", "N"):
            return choice == "Y"

        print("❌ Please enter Y or N.")


# ----------------------------------------------------
# Game Functions
# ----------------------------------------------------

def play_game(minimum, maximum):
    """
    Play one round of the guessing game.
    """

    secret_number = random.randint(minimum, maximum)

    attempts = 0

    print("\nGame Started!")

    while True:

        guess = get_guess(minimum, maximum)

        attempts += 1

        if guess < secret_number:

            print("⬆ Too Low!\n")

        elif guess > secret_number:

            print("⬇ Too High!\n")

        else:

            print("\n🎉 Congratulations!")
            print(f"You guessed the correct number: {secret_number}")
            print(f"Attempts: {attempts}\n")

            break


# ----------------------------------------------------
# Display Banner
# ----------------------------------------------------

def display_banner():

    print("\n" + "=" * 45)
    print("         NUMBER GUESSING GAME")
    print("=" * 45)


# ----------------------------------------------------
# Main Program
# ----------------------------------------------------

def main():

    while True:

        display_banner()

        choice = get_menu_choice()

        if choice == "4":

            print("\nThank you for playing!")
            print("Goodbye!\n")

            break

        if choice == "1":

            play_game(1, 10)

        elif choice == "2":

            play_game(1, 50)

        else:

            play_game(1, 100)

        again = get_yes_no(
            "Would you like to play again? (Y/N): "
        )

        if not again:

            print("\nThank you for playing!")
            print("Goodbye!\n")

            break


# ----------------------------------------------------
# Program Entry Point
# ----------------------------------------------------

if __name__ == "__main__":
    main()