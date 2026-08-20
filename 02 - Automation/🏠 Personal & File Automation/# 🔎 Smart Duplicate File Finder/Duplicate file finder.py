"""
Project : Smart Duplicate File Finder
Module  : Automation
Author  : Aman Kumar
Repository : Python-Projects

Description:
A Python automation tool that scans a selected folder and its
subfolders to find duplicate files.

The program scans files, compares their sizes, calculates hashes,
groups files that contain exactly the same data, analyzes duplicate
groups, recommends which copies should be kept, allows
user-confirmed cleanup, and generates a detailed report.

Additional automation will be added in later stages.
"""


# ----------------------------------------------------
# Imports
# ----------------------------------------------------

from pathlib import Path
from datetime import datetime
import hashlib
import json
import os


# ----------------------------------------------------
# Load Rules
# ----------------------------------------------------

def load_rules():
    """
    Load program rules from rules.json.

    The rules file is kept separate from the main program
    so settings can be changed without modifying Python code.

    Returns:
        dict: Rules loaded from the configuration file.
    """

    rules_path = Path(__file__).parent / "rules.json"

    try:
        with rules_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except FileNotFoundError:

        print("⚠ rules.json was not found.")
        print("Using default settings.")

        return {}

    except json.JSONDecodeError:

        print("⚠ rules.json contains invalid JSON.")
        print("Using default settings.")

        return {}

    except OSError as error:

        print(
            f"⚠ Unable to read rules.json: {error}"
        )

        print("Using default settings.")

        return {}


# ----------------------------------------------------
# Folder Scanner
# ----------------------------------------------------

def scan_folder(folder_path):
    """
    Scan a folder and return all files found inside it.

    The scan includes subfolders.
    Files that cannot be accessed are skipped.

    Returns:
        list: Files found inside the folder.
    """

    files = []

    try:

        for path in folder_path.rglob("*"):

            # Only process regular files.
            if path.is_file():
                files.append(path)

    except PermissionError:

        print(
            "⚠ Some files or folders could not be accessed."
        )

    except OSError as error:

        print(
            f"⚠ Unable to access part of the folder: {error}"
        )

    return files


# ----------------------------------------------------
# Group Files by Size
# ----------------------------------------------------

def group_files_by_size(files):
    """
    Group files that have the same size.

    Files with unique sizes cannot be exact duplicates,
    so only groups containing multiple files are returned.

    Returns:
        dict: File sizes mapped to lists of matching files.
    """

    size_groups = {}

    for file_path in files:

        try:

            file_size = file_path.stat().st_size

            if file_size not in size_groups:
                size_groups[file_size] = []

            size_groups[file_size].append(file_path)

        except OSError:

            # Skip files that cannot be accessed.
            continue

    # Keep only sizes that belong to multiple files.
    possible_duplicates = {
        size: file_list
        for size, file_list in size_groups.items()
        if len(file_list) > 1
    }

    return possible_duplicates


# ----------------------------------------------------
# Calculate File Hash
# ----------------------------------------------------

def calculate_hash(
    file_path,
    algorithm="sha256",
    chunk_size=1024 * 1024
):
    """
    Calculate a hash of a file.

    The file is read in small chunks instead of loading
    the entire file into memory at once.

    Args:
        file_path: File to hash.
        algorithm: Hash algorithm to use.
        chunk_size: Number of bytes read at a time.

    Returns:
        str: File hash.
        None: If the file cannot be accessed.
    """

    try:

        hash_function = hashlib.new(algorithm)

    except ValueError:

        print(
            f"⚠ Unsupported hash algorithm: {algorithm}"
        )

        return None

    try:

        with file_path.open("rb") as file:

            while chunk := file.read(chunk_size):
                hash_function.update(chunk)

        return hash_function.hexdigest()

    except OSError:

        return None


# ----------------------------------------------------
# Group Files by Hash
# ----------------------------------------------------

def group_files_by_hash(
    size_groups,
    rules
):
    """
    Group possible duplicate files by their hash.

    Only files that already have the same size are checked.

    Hashing settings are loaded from rules.json.

    Returns:
        dict: Hashes mapped to lists of exact duplicate files.
    """

    hash_groups = {}

    hashing_rules = rules.get(
        "hashing",
        {}
    )

    algorithm = hashing_rules.get(
        "algorithm",
        "sha256"
    )

    chunk_size = hashing_rules.get(
        "chunk_size",
        1024 * 1024
    )

    for file_list in size_groups.values():

        for file_path in file_list:

            file_hash = calculate_hash(
                file_path,
                algorithm,
                chunk_size
            )

            # Skip files that could not be accessed.
            if file_hash is None:
                continue

            if file_hash not in hash_groups:
                hash_groups[file_hash] = []

            hash_groups[file_hash].append(file_path)

    # Keep only hashes that belong to multiple files.
    duplicate_groups = {
        file_hash: file_list
        for file_hash, file_list in hash_groups.items()
        if len(file_list) > 1
    }

    return duplicate_groups


# ----------------------------------------------------
# Analyze Duplicate Groups
# ----------------------------------------------------

def analyze_duplicate_groups(duplicate_groups):
    """
    Analyze exact duplicate groups.

    Calculates useful information such as:

        - Copy count
        - File size
        - File locations
        - Modification dates
        - Potential storage recovery

    Returns:
        list: Information about each duplicate group.
    """

    analyzed_groups = []

    for group_number, (
        file_hash,
        file_list
    ) in enumerate(
        duplicate_groups.items(),
        start=1
    ):

        try:

            file_size = file_list[0].stat().st_size

        except OSError:

            # Skip groups whose files cannot be accessed.
            continue

        file_information = []

        for file_path in file_list:

            try:

                file_stat = file_path.stat()

                file_information.append({
                    "path": file_path,
                    "modified_time": file_stat.st_mtime
                })

            except OSError:

                # Skip files whose metadata cannot be accessed.
                continue

        copy_count = len(file_information)

        # One copy is kept.
        potential_space = (
            file_size * (copy_count - 1)
        )

        analyzed_groups.append({
            "group_number": group_number,
            "hash": file_hash,
            "files": file_information,
            "copy_count": copy_count,
            "file_size": file_size,
            "potential_space": potential_space
        })

    return analyzed_groups


# ----------------------------------------------------
# Recommend Duplicate Files
# ----------------------------------------------------

def recommend_duplicates(
    analyzed_groups,
    rules
):
    """
    Recommend which file should be kept in each
    duplicate group.

    No files are deleted or modified.

    Recommendation behavior is controlled by rules.json.

    Supported strategies:

        oldest:
            Recommend keeping the oldest file.

        newest:
            Recommend keeping the newest file.

        shortest_path:
            Recommend keeping the file with the shortest path.

    Returns:
        list: Duplicate groups with recommendations.
    """

    recommendation_rules = rules.get(
        "recommendations",
        {}
    )

    strategy = recommendation_rules.get(
        "keep",
        "oldest"
    ).lower()

    recommended_groups = []

    for group in analyzed_groups:

        files = group["files"]

        if len(files) < 2:
            continue

        if strategy == "newest":

            recommended_file = max(
                files,
                key=lambda file_info:
                file_info["modified_time"]
            )

        elif strategy == "shortest_path":

            recommended_file = min(
                files,
                key=lambda file_info:
                len(str(file_info["path"]))
            )

        else:

            # Default strategy: oldest file.
            recommended_file = min(
                files,
                key=lambda file_info:
                file_info["modified_time"]
            )

        # Every other copy becomes a removal candidate.
        remove_candidates = [
            file_info
            for file_info in files
            if file_info["path"]
            != recommended_file["path"]
        ]

        recommended_groups.append({
            "group_number": group["group_number"],
            "keep": recommended_file,
            "remove_candidates": remove_candidates,
            "strategy": strategy,
            "potential_space": group["potential_space"]
        })

    return recommended_groups


# ----------------------------------------------------
# Format File Size
# ----------------------------------------------------

def format_file_size(size):
    """
    Convert bytes into a human-readable file size.

    Returns:
        str: Formatted file size.
    """

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ]

    size = float(size)

    for unit in units:

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


# ----------------------------------------------------
# Display Duplicate Summary
# ----------------------------------------------------

def display_duplicate_summary(
    files,
    size_groups,
    analyzed_groups,
    folder
):
    """
    Display a summary of the duplicate scan.

    The summary shows important results without printing
    every duplicate group to the terminal.
    """

    total_duplicate_files = sum(
        group["copy_count"]
        for group in analyzed_groups
    )

    potential_space = sum(
        group["potential_space"]
        for group in analyzed_groups
    )

    print("\n" + "=" * 50)
    print("           DUPLICATE SUMMARY")
    print("=" * 50)

    print(
        f"\nFiles scanned: {len(files)}"
    )

    print(
        f"Possible duplicate groups: "
        f"{len(size_groups)}"
    )

    print(
        f"Exact duplicate groups: "
        f"{len(analyzed_groups)}"
    )

    print(
        f"Duplicate files: "
        f"{total_duplicate_files}"
    )

    print(
        f"Potential space to recover: "
        f"{format_file_size(potential_space)}"
    )

    print(
        f"Folder scanned: {folder}"
    )


# ----------------------------------------------------
# Display Duplicate Groups
# ----------------------------------------------------

def display_duplicate_groups(
    analyzed_groups,
    groups_per_page=10
):
    """
    Display duplicate groups using pagination.

    Only a limited number of groups are displayed at a time
    to prevent endless terminal output.
    """

    if not analyzed_groups:

        print(
            "\n🎯 No duplicate groups to display."
        )

        return

    total_groups = len(analyzed_groups)
    current_page = 0

    while True:

        start_index = (
            current_page * groups_per_page
        )

        end_index = min(
            start_index + groups_per_page,
            total_groups
        )

        print("\n" + "=" * 50)
        print("             DUPLICATE GROUPS")
        print("=" * 50)

        print(
            f"\nShowing groups "
            f"{start_index + 1}-{end_index} "
            f"of {total_groups}"
        )

        for group in analyzed_groups[
            start_index:end_index
        ]:

            print("\n" + "-" * 50)

            print(
                f"🎯 Duplicate Group "
                f"#{group['group_number']}"
            )

            print("-" * 50)

            print(
                f"Copies: "
                f"{group['copy_count']}"
            )

            print(
                f"File size: "
                f"{format_file_size(group['file_size'])}"
            )

            print(
                f"Potential space: "
                f"{format_file_size(group['potential_space'])}"
            )

            print("\nLocations:")

            for number, file_info in enumerate(
                group["files"],
                start=1
            ):

                formatted_date = (
                    datetime.fromtimestamp(
                        file_info["modified_time"]
                    ).strftime(
                        "%d %b %Y, %H:%M"
                    )
                )

                print(
                    f"\n{number}. "
                    f"{file_info['path']}"
                )

                print(
                    f"   Modified: "
                    f"{formatted_date}"
                )

        print("\n" + "-" * 50)
        print("\nOptions:")

        if end_index < total_groups:
            print("[N] Next page")

        if current_page > 0:
            print("[P] Previous page")

        print("[B] Back to main menu")

        choice = input(
            "\nChoice: "
        ).strip().lower()

        if (
            choice == "n"
            and end_index < total_groups
        ):

            current_page += 1

        elif (
            choice == "p"
            and current_page > 0
        ):

            current_page -= 1

        elif choice == "b":

            print(
                "\nReturning to main menu."
            )

            break

        else:

            print(
                "\n⚠ Invalid choice."
            )


# ----------------------------------------------------
# Display Recommendations
# ----------------------------------------------------

def display_recommendations(
    recommendations,
    groups_per_page=10
):
    """
    Display duplicate cleanup recommendations.

    Recommendations are displayed using pagination.

    No files are deleted.
    """

    if not recommendations:

        print(
            "\n🎯 No recommendations available."
        )

        return

    total_groups = len(recommendations)
    current_page = 0

    while True:

        start_index = (
            current_page * groups_per_page
        )

        end_index = min(
            start_index + groups_per_page,
            total_groups
        )

        print("\n" + "=" * 50)
        print("        DUPLICATE RECOMMENDATIONS")
        print("=" * 50)

        print(
            f"\nShowing groups "
            f"{start_index + 1}-{end_index} "
            f"of {total_groups}"
        )

        for recommendation in recommendations[
            start_index:end_index
        ]:

            group_number = recommendation[
                "group_number"
            ]

            keep_file = recommendation[
                "keep"
            ]

            remove_candidates = recommendation[
                "remove_candidates"
            ]

            strategy = recommendation[
                "strategy"
            ]

            potential_space = recommendation[
                "potential_space"
            ]

            print("\n" + "-" * 50)

            print(
                f"🎯 Duplicate Group "
                f"#{group_number}"
            )

            print("-" * 50)

            print(
                f"Recommendation strategy: "
                f"{strategy}"
            )

            print("\n✅ Recommended to keep:")

            print(
                f"   {keep_file['path']}"
            )

            formatted_date = (
                datetime.fromtimestamp(
                    keep_file["modified_time"]
                ).strftime(
                    "%d %b %Y, %H:%M"
                )
            )

            print(
                f"   Modified: "
                f"{formatted_date}"
            )

            print("\n🗑 Candidates for removal:")

            for file_info in remove_candidates:

                formatted_date = (
                    datetime.fromtimestamp(
                        file_info["modified_time"]
                    ).strftime(
                        "%d %b %Y, %H:%M"
                    )
                )

                print(
                    f"\n   {file_info['path']}"
                )

                print(
                    f"   Modified: "
                    f"{formatted_date}"
                )

            print(
                "\n💾 Potential space: "
                f"{format_file_size(potential_space)}"
            )

        print("\n" + "-" * 50)
        print("\nOptions:")

        if end_index < total_groups:
            print("[N] Next page")

        if current_page > 0:
            print("[P] Previous page")

        print("[B] Back to main menu")

        choice = input(
            "\nChoice: "
        ).strip().lower()

        if (
            choice == "n"
            and end_index < total_groups
        ):

            current_page += 1

        elif (
            choice == "p"
            and current_page > 0
        ):

            current_page -= 1

        elif choice == "b":

            print(
                "\nReturning to main menu."
            )

            break

        else:

            print(
                "\n⚠ Invalid choice."
            )


# ----------------------------------------------------
# Select Recommendation Group
# ----------------------------------------------------

def select_recommendation_group(
    recommendations
):
    """
    Let the user choose one recommendation group.

    Returns:
        dict: Selected recommendation.
        None: If the user cancels or the group is invalid.
    """

    if not recommendations:

        print(
            "\n🎯 No recommendations available."
        )

        return None

    print("\n" + "=" * 50)
    print("        SELECT DUPLICATE GROUP")
    print("=" * 50)

    print(
        f"\nAvailable groups: "
        f"{len(recommendations)}"
    )

    print(
        "\nEnter a group number "
        "or Q to cancel."
    )

    selection = input(
        "\nGroup number: "
    ).strip().lower()

    if selection == "q":
        return None

    try:

        group_number = int(selection)

    except ValueError:

        print(
            "\n⚠ Invalid group number."
        )

        return None

    for recommendation in recommendations:

        if recommendation["group_number"] == group_number:
            return recommendation

    print(
        "\n⚠ That group does not exist."
    )

    return None


# ----------------------------------------------------
# Move File to Recycle Bin
# ----------------------------------------------------

def move_to_recycle_bin(file_path):
    """
    Move a file to the Windows Recycle Bin.

    Returns:
        bool: True if the operation succeeds.
    """

    if os.name != "nt":

        print(
            "\n⚠ Recycle Bin support is currently "
            "available only on Windows."
        )

        return False

    try:

        import ctypes
        from ctypes import wintypes

        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [
                ("hwnd", wintypes.HWND),
                ("wFunc", wintypes.UINT),
                ("pFrom", wintypes.LPCWSTR),
                ("pTo", wintypes.LPCWSTR),
                ("fFlags", wintypes.WORD),
                ("fAnyOperationsAborted", wintypes.BOOL),
                ("hNameMappings", wintypes.LPVOID),
                ("lpszProgressTitle", wintypes.LPCWSTR)
            ]

        FO_DELETE = 0x0003

        FOF_SILENT = 0x0004
        FOF_NOCONFIRMATION = 0x0010
        FOF_ALLOWUNDO = 0x0040

        source = str(file_path) + "\0\0"

        operation = SHFILEOPSTRUCTW(
            hwnd=None,
            wFunc=FO_DELETE,
            pFrom=source,
            pTo=None,
            fFlags=(
                FOF_SILENT
                | FOF_NOCONFIRMATION
                | FOF_ALLOWUNDO
            ),
            fAnyOperationsAborted=False,
            hNameMappings=None,
            lpszProgressTitle=None
        )

        result = ctypes.windll.shell32.SHFileOperationW(
            ctypes.byref(operation)
        )

        return result == 0

    except OSError:

        return False


# ----------------------------------------------------
# Cleanup Duplicates
# ----------------------------------------------------

def cleanup_duplicates(
    recommendation,
    rules
):
    """
    Safely clean selected duplicate files.

    The user can choose between:

        1. Move to Recycle Bin
        2. Permanently Delete

    The recommended keep-file is protected.

    Returns:
        list: Files successfully cleaned up.
    """

    keep_file = recommendation["keep"]
    remove_candidates = recommendation[
        "remove_candidates"
    ]

    if not remove_candidates:

        print(
            "\n🎯 There are no duplicate files "
            "available for cleanup."
        )

        return []

    cleanup_rules = rules.get(
        "cleanup",
        {}
    )

    require_confirmation = cleanup_rules.get(
        "require_confirmation",
        True
    )

    print("\n" + "=" * 50)
    print("             SAFE CLEANUP")
    print("=" * 50)

    print("\n✅ File protected from cleanup:")

    print(
        f"   {keep_file['path']}"
    )

    print(
        "\n🗑 Duplicate files available "
        "for cleanup:"
    )

    for number, file_info in enumerate(
        remove_candidates,
        start=1
    ):

        formatted_date = (
            datetime.fromtimestamp(
                file_info["modified_time"]
            ).strftime(
                "%d %b %Y, %H:%M"
            )
        )

        print(
            f"\n[{number}] "
            f"{file_info['path']}"
        )

        print(
            f"    Modified: {formatted_date}"
        )

    print(
        "\nEnter the numbers of the files "
        "you want to clean up."
    )

    print("Example: 1")
    print("For multiple files, use: 1,2,3")

    selection = input(
        "\nSelection (or Q to cancel): "
    ).strip().lower()

    if selection == "q":

        print(
            "\nCleanup cancelled."
        )

        return []

    try:

        selected_numbers = {
            int(number.strip())
            for number in selection.split(",")
            if number.strip()
        }

    except ValueError:

        print(
            "\n⚠ Invalid selection."
        )

        return []

    valid_numbers = set(
        range(
            1,
            len(remove_candidates) + 1
        )
    )

    if not selected_numbers:

        print(
            "\n⚠ No files were selected."
        )

        return []

    if not selected_numbers.issubset(
        valid_numbers
    ):

        print(
            "\n⚠ One or more selected numbers "
            "are invalid."
        )

        return []

    selected_files = [
        remove_candidates[number - 1]
        for number in sorted(selected_numbers)
    ]

    # ------------------------------------------------
    # Choose Cleanup Mode
    # ------------------------------------------------

    print("\n" + "-" * 50)
    print("             CLEANUP MODE")
    print("-" * 50)

    print("\n[1] ♻️ Move to Recycle Bin")
    print("[2] 🗑️ Permanently Delete")
    print("[Q] Cancel")

    mode = input(
        "\nChoice: "
    ).strip().lower()

    if mode == "q":

        print(
            "\nCleanup cancelled."
        )

        return []

    if mode == "1":

        cleanup_mode = "recycle_bin"

    elif mode == "2":

        cleanup_mode = "permanent"

    else:

        print(
            "\n⚠ Invalid cleanup mode."
        )

        return []

    # ------------------------------------------------
    # Final Confirmation
    # ------------------------------------------------

    print("\n" + "-" * 50)
    print("⚠ FINAL CONFIRMATION")
    print("-" * 50)

    if cleanup_mode == "recycle_bin":

        print(
            "\nThe selected files will be "
            "moved to the Recycle Bin."
        )

    else:

        print(
            "\n⚠ PERMANENT DELETE SELECTED."
        )

        print(
            "The selected files will be "
            "permanently deleted."
        )

    print(
        "\nThe protected file will NOT be affected:"
    )

    print(
        f"\n✅ {keep_file['path']}"
    )

    print("\nSelected files:")

    for file_info in selected_files:

        print(
            f"\n- {file_info['path']}"
        )

    if require_confirmation:

        if cleanup_mode == "recycle_bin":

            confirmation = input(
                "\nType DELETE to confirm: "
            ).strip()

            if confirmation != "DELETE":

                print(
                    "\n❌ Cleanup cancelled."
                )

                return []

        else:

            confirmation = input(
                "\nType DELETE PERMANENTLY "
                "to continue: "
            ).strip()

            if confirmation != "DELETE PERMANENTLY":

                print(
                    "\n❌ Permanent deletion cancelled."
                )

                return []

    # ------------------------------------------------
    # Perform Cleanup
    # ------------------------------------------------

    cleaned_files = []

    for file_info in selected_files:

        file_path = file_info["path"]

        try:

            # Extra protection.
            if file_path == keep_file["path"]:

                print(
                    f"\n⚠ Protected file skipped: "
                    f"{file_path}"
                )

                continue

            if cleanup_mode == "recycle_bin":

                success = move_to_recycle_bin(
                    file_path
                )

                if success:

                    cleaned_files.append(
                        file_path
                    )

                    print(
                        f"\n♻️ Moved to Recycle Bin: "
                        f"{file_path}"
                    )

                else:

                    print(
                        f"\n⚠ Could not move to "
                        f"Recycle Bin: "
                        f"{file_path}"
                    )

            else:

                file_path.unlink()

                cleaned_files.append(
                    file_path
                )

                print(
                    f"\n🗑️ Permanently deleted: "
                    f"{file_path}"
                )

        except FileNotFoundError:

            print(
                f"\n⚠ File no longer exists: "
                f"{file_path}"
            )

        except PermissionError:

            print(
                f"\n⚠ Permission denied: "
                f"{file_path}"
            )

        except OSError as error:

            print(
                f"\n⚠ Could not process "
                f"{file_path}: {error}"
            )

    print("\n" + "-" * 50)

    print("Cleanup complete.")

    print(
        f"Files processed successfully: "
        f"{len(cleaned_files)}"
    )

    return cleaned_files


# ----------------------------------------------------
# Generate Duplicate Report
# ----------------------------------------------------

def generate_report(
    files,
    size_groups,
    analyzed_groups,
    recommendations,
    folder,
    rules,
    cleaned_files
):
    """
    Generate a text report containing duplicate scan results.

    The report includes:

        - Scan summary
        - Duplicate statistics
        - Potential storage recovery
        - Duplicate groups
        - Recommendations
        - Cleanup results

    Returns:
        Path: Location of the generated report.
        None: If the report could not be created.
    """

    reporting_rules = rules.get(
        "reporting",
        {}
    )

    if not reporting_rules.get(
        "enabled",
        True
    ):

        print(
            "\n📄 Reporting is disabled in rules.json."
        )

        return None

    report_filename = reporting_rules.get(
        "filename",
        "duplicate-report.txt"
    )

    report_path = (
        Path(__file__).parent
        / report_filename
    )

    total_duplicate_files = sum(
        group["copy_count"]
        for group in analyzed_groups
    )

    potential_space = sum(
        group["potential_space"]
        for group in analyzed_groups
    )

    try:

        with report_path.open(
            "w",
            encoding="utf-8"
        ) as report:

            # ------------------------------------------------
            # Report Header
            # ------------------------------------------------

            report.write(
                "SMART DUPLICATE FILE FINDER REPORT\n"
            )

            report.write(
                "=" * 60 + "\n\n"
            )

            # ------------------------------------------------
            # Scan Information
            # ------------------------------------------------

            report.write(
                "SCAN INFORMATION\n"
            )

            report.write(
                "-" * 60 + "\n"
            )

            report.write(
                f"Folder scanned: {folder}\n"
            )

            report.write(
                f"Files scanned: {len(files)}\n"
            )

            report.write(
                f"Possible duplicate groups: "
                f"{len(size_groups)}\n"
            )

            report.write(
                f"Exact duplicate groups: "
                f"{len(analyzed_groups)}\n"
            )

            report.write(
                f"Duplicate files: "
                f"{total_duplicate_files}\n"
            )

            report.write(
                f"Potential space to recover: "
                f"{format_file_size(potential_space)}\n"
            )

            # ------------------------------------------------
            # Duplicate Groups
            # ------------------------------------------------

            report.write(
                "\n\nDUPLICATE GROUPS\n"
            )

            report.write(
                "-" * 60 + "\n"
            )

            if not analyzed_groups:

                report.write(
                    "No exact duplicate groups found.\n"
                )

            else:

                for group in analyzed_groups:

                    report.write(
                        "\nDuplicate Group "
                        f"#{group['group_number']}\n"
                    )

                    report.write(
                        "~" * 40 + "\n"
                    )

                    report.write(
                        f"Copies: "
                        f"{group['copy_count']}\n"
                    )

                    report.write(
                        f"File size: "
                        f"{format_file_size(group['file_size'])}\n"
                    )

                    report.write(
                        f"Potential space: "
                        f"{format_file_size(group['potential_space'])}\n"
                    )

                    report.write(
                        f"SHA-256: "
                        f"{group['hash']}\n"
                    )

                    report.write(
                        "\nLocations:\n"
                    )

                    for number, file_info in enumerate(
                        group["files"],
                        start=1
                    ):

                        modified_date = (
                            datetime.fromtimestamp(
                                file_info["modified_time"]
                            ).strftime(
                                "%d %b %Y, %H:%M"
                            )
                        )

                        report.write(
                            f"\n{number}. "
                            f"{file_info['path']}\n"
                        )

                        report.write(
                            f"   Modified: "
                            f"{modified_date}\n"
                        )

            # ------------------------------------------------
            # Recommendations
            # ------------------------------------------------

            report.write(
                "\n\nRECOMMENDATIONS\n"
            )

            report.write(
                "-" * 60 + "\n"
            )

            if not recommendations:

                report.write(
                    "No recommendations available.\n"
                )

            else:

                for recommendation in recommendations:

                    keep_file = recommendation["keep"]

                    report.write(
                        "\nDuplicate Group "
                        f"#{recommendation['group_number']}\n"
                    )

                    report.write(
                        f"Strategy: "
                        f"{recommendation['strategy']}\n"
                    )

                    report.write(
                        "Recommended to keep:\n"
                    )

                    report.write(
                        f"  {keep_file['path']}\n"
                    )

                    report.write(
                        "\nCandidates for removal:\n"
                    )

                    for file_info in recommendation[
                        "remove_candidates"
                    ]:

                        report.write(
                            f"  {file_info['path']}\n"
                        )

                    report.write(
                        "\nPotential space: "
                        f"{format_file_size(recommendation['potential_space'])}\n"
                    )

            # ------------------------------------------------
            # Cleanup Results
            # ------------------------------------------------

            report.write(
                "\n\nCLEANUP RESULTS\n"
            )

            report.write(
                "-" * 60 + "\n"
            )

            report.write(
                f"Files successfully cleaned: "
                f"{len(cleaned_files)}\n"
            )

            if cleaned_files:

                report.write(
                    "\nCleaned files:\n"
                )

                for file_path in cleaned_files:

                    report.write(
                        f"- {file_path}\n"
                    )

            else:

                report.write(
                    "No files were cleaned during this run.\n"
                )

            # ------------------------------------------------
            # Report Footer
            # ------------------------------------------------

            report.write(
                "\n\n"
                + "=" * 60
                + "\n"
            )

            report.write(
                "End of report\n"
            )

        print(
            f"\n📄 Report saved to:\n"
            f"{report_path}"
        )

        return report_path

    except OSError as error:

        print(
            f"\n⚠ Could not create report: {error}"
        )

        return None


# ----------------------------------------------------
# Get Folder
# ----------------------------------------------------

def get_folder():
    """
    Ask the user for a folder to scan.

    Returns:
        Path: A valid folder path.
    """

    while True:

        folder_input = input(
            "\nEnter folder to scan: "
        ).strip()

        if not folder_input:

            print(
                "⚠ Please enter a folder path."
            )

            continue

        folder_path = (
            Path(folder_input)
            .expanduser()
        )

        if not folder_path.exists():

            print(
                "⚠ That folder does not exist."
            )

            continue

        if not folder_path.is_dir():

            print(
                "⚠ Please enter a folder, "
                "not a file."
            )

            continue

        return folder_path


# ----------------------------------------------------
# Main Program
# ----------------------------------------------------

def main():
    """
    Run the Duplicate File Finder.
    """

    print("=" * 50)
    print("       🔎 SMART DUPLICATE FILE FINDER")
    print("=" * 50)

    # ------------------------------------------------
    # Load external configuration
    # ------------------------------------------------

    rules = load_rules()

    print("\n📖 Rules loaded.")

    hashing_rules = rules.get(
        "hashing",
        {}
    )

    print(
        f"🔐 Hash algorithm: "
        f"{hashing_rules.get('algorithm', 'sha256')}"
    )

    print(
        f"📦 Hash chunk size: "
        f"{hashing_rules.get('chunk_size', 1048576)} "
        f"bytes"
    )

    recommendation_rules = rules.get(
        "recommendations",
        {}
    )

    print(
        f"🧠 Recommendation strategy: "
        f"{recommendation_rules.get('keep', 'oldest')}"
    )

    display_rules = rules.get(
        "display",
        {}
    )

    groups_per_page = display_rules.get(
        "groups_per_page",
        10
    )

    # Files successfully cleaned during this run.
    cleaned_files = []

    # ------------------------------------------------
    # Get Folder
    # ------------------------------------------------

    folder = get_folder()

    print(
        "\n🔍 Scanning folder..."
    )

    print(
        f"📂 {folder}"
    )

    files = scan_folder(folder)

    # ------------------------------------------------
    # Group by Size
    # ------------------------------------------------

    print(
        "\n📏 Checking file sizes..."
    )

    size_groups = group_files_by_size(
        files
    )

    # ------------------------------------------------
    # Group by Hash
    # ------------------------------------------------

    print(
        "\n🔐 Comparing file contents..."
    )

    duplicate_groups = group_files_by_hash(
        size_groups,
        rules
    )

    # ------------------------------------------------
    # Analyze Duplicate Groups
    # ------------------------------------------------

    print(
        "\n📊 Analyzing duplicate groups..."
    )

    analyzed_groups = analyze_duplicate_groups(
        duplicate_groups
    )

    # ------------------------------------------------
    # Display Summary
    # ------------------------------------------------

    display_duplicate_summary(
        files,
        size_groups,
        analyzed_groups,
        folder
    )

    # ------------------------------------------------
    # Recommendations
    # ------------------------------------------------

    if analyzed_groups:

        print(
            "\n🎯 Exact duplicates "
            "have been identified."
        )

        print(
            "\n🧠 Generating recommendations..."
        )

        recommendations = recommend_duplicates(
            analyzed_groups,
            rules
        )

        print(
            f"✅ Recommendations generated "
            f"for {len(recommendations)} groups."
        )

        # --------------------------------------------
        # Main User Menu
        # --------------------------------------------

        while True:

            print("\n" + "=" * 50)
            print("                 OPTIONS")
            print("=" * 50)

            print(
                "\n[1] Inspect duplicate groups"
            )

            print(
                "[2] View recommendations"
            )

            print(
                "[3] Clean up a duplicate group"
            )

            print(
                "[4] Generate report"
            )

            print(
                "[Q] Finish"
            )

            choice = input(
                "\nChoice: "
            ).strip().lower()

            if choice == "1":

                display_duplicate_groups(
                    analyzed_groups,
                    groups_per_page
                )

            elif choice == "2":

                display_recommendations(
                    recommendations,
                    groups_per_page
                )

            elif choice == "3":

                recommendation = (
                    select_recommendation_group(
                        recommendations
                    )
                )

                if recommendation:

                    newly_cleaned = (
                        cleanup_duplicates(
                            recommendation,
                            rules
                        )
                    )

                    cleaned_files.extend(
                        newly_cleaned
                    )

            elif choice == "4":

                generate_report(
                    files,
                    size_groups,
                    analyzed_groups,
                    recommendations,
                    folder,
                    rules,
                    cleaned_files
                )

            elif choice == "q":

                break

            else:

                print(
                    "\n⚠ Invalid choice."
                )

    else:

        print(
            "\n🎯 No exact duplicates were found."
        )

        print(
            "\nWould you like to generate "
            "a report anyway?"
        )

        choice = input(
            "Enter Y to generate a report, "
            "or N to finish: "
        ).strip().lower()

        if choice == "y":

            generate_report(
                files,
                size_groups,
                [],
                [],
                folder,
                rules,
                cleaned_files
            )

    # ------------------------------------------------
    # Complete
    # ------------------------------------------------

    print("\n" + "=" * 50)
    print("                 COMPLETE")
    print("=" * 50)


# ----------------------------------------------------
# Program Entry Point
# ----------------------------------------------------

if __name__ == "__main__":
    main()
