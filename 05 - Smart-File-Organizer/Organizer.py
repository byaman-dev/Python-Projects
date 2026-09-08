"""
Project : Smart File Organizer
Module  : Automation
Version : 1.0
Author  : Aman Kumar
Repository : Python-Projects

Description:
A command-line automation tool that organizes files into folders
based on user-defined rules stored in rules.txt.

The project is designed to reduce the time spent manually sorting
files into different folders.
"""


# ----------------------------------------------------
# Imports
# ----------------------------------------------------

from pathlib import Path


# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

RULES_FILE = Path("rules.txt")


# ----------------------------------------------------
# Rule Loading
# ----------------------------------------------------

def load_rules() -> dict[str, str]:
    """
    Load file organization rules from rules.txt.

    Returns:
        A dictionary mapping file extensions to folder names.
    """

    rules = {}

    if not RULES_FILE.exists():
        print(f"\nError: {RULES_FILE} was not found.")
        return rules

    try:
        with RULES_FILE.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                # Ignore blank lines and comments.
                if not line or line.startswith("#"):
                    continue

                # Every rule must follow: .extension=Folder
                if "=" not in line:
                    print(
                        f"Warning: Invalid rule on line {line_number}: "
                        f"{line}"
                    )
                    continue

                extension, folder = line.split("=", 1)

                extension = extension.strip().lower()
                folder = folder.strip()

                if not extension or not folder:
                    print(
                        f"Warning: Invalid rule on line {line_number}: "
                        f"{line}"
                    )
                    continue

                if not extension.startswith("."):
                    print(
                        f"Warning: Extension must start with '.': "
                        f"{extension}"
                    )
                    continue

                rules[extension] = folder

    except OSError as error:
        print(f"\nError reading {RULES_FILE}: {error}")

    return rules


# ----------------------------------------------------
# Folder Selection
# ----------------------------------------------------

def get_target_folder() -> Path | None:
    """
    Ask the user for the folder they want to organize.

    Returns:
        A valid folder path, or None if the path is invalid.
    """

    folder_input = input(
        "\nEnter the folder you want to organize:\n> "
    ).strip()

    if not folder_input:
        print("\nError: No folder was provided.")
        return None

    folder = Path(folder_input).expanduser()

    if not folder.exists():
        print("\nError: The specified folder does not exist.")
        return None

    if not folder.is_dir():
        print("\nError: The specified path is not a folder.")
        return None

    return folder


# ----------------------------------------------------
# File Organization
# ----------------------------------------------------

def organize_files(
    target_folder: Path,
    rules: dict[str, str],
) -> tuple[int, int, int, int]:
    """
    Organize files in the target folder according to the rules.

    Returns:
        A tuple containing:
        - files processed
        - files organized
        - files skipped
        - errors
    """

    processed = 0
    organized = 0
    skipped = 0
    errors = 0

    try:
        items = list(target_folder.iterdir())
    except OSError as error:
        print(f"\nError scanning folder: {error}")
        return processed, organized, skipped, errors + 1

    for item in items:

        # Only process files.
        if not item.is_file():
            continue

        processed += 1

        extension = item.suffix.lower()

        # Check whether a rule exists for this extension.
        if extension not in rules:
            print(
                f"  - Skipped: {item.name} "
                f"(no matching rule)"
            )
            skipped += 1
            continue

        destination_name = rules[extension]
        destination_folder = target_folder / destination_name

        try:
            # Create destination folder if it does not exist.
            destination_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination = destination_folder / item.name

            # Version 1.0 does not handle filename conflicts.
            if destination.exists():
                print(
                    f"  ! Skipped: {item.name} "
                    f"(destination already exists)"
                )
                skipped += 1
                continue

            item.rename(destination)

            print(
                f"  ✓ {item.name} → {destination_name}"
            )

            organized += 1

        except OSError as error:
            print(
                f"  ✗ Error moving {item.name}: {error}"
            )
            errors += 1

    return processed, organized, skipped, errors


# ----------------------------------------------------
# Summary
# ----------------------------------------------------

def display_summary(
    processed: int,
    organized: int,
    skipped: int,
    errors: int,
) -> None:
    """Display the final organization summary."""

    print("\n" + "=" * 40)
    print("       ORGANIZATION COMPLETE")
    print("=" * 40)

    print(f"\nFiles processed : {processed}")
    print(f"Files organized : {organized}")
    print(f"Files skipped   : {skipped}")
    print(f"Errors          : {errors}")

    print("\nThank you for using Smart File Organizer!")


# ----------------------------------------------------
# Main Program
# ----------------------------------------------------

def main() -> None:
    """Run the Smart File Organizer."""

    print("=" * 40)
    print("       SMART FILE ORGANIZER")
    print("=" * 40)

    rules = load_rules()

    if not rules:
        print("\nNo valid organization rules were found.")
        print(f"Check your {RULES_FILE} file.")
        return

    target_folder = get_target_folder()

    if target_folder is None:
        return

    print(f"\nOrganizing: {target_folder}")
    print("\nProcessing files...\n")

    processed, organized, skipped, errors = organize_files(
        target_folder,
        rules,
    )

    display_summary(
        processed,
        organized,
        skipped,
        errors,
    )


# ----------------------------------------------------
# Program Entry Point
# ----------------------------------------------------

if __name__ == "__main__":
    main()
