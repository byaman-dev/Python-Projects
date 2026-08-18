# 🔎 Smart Duplicate File Finder

Ever opened a folder and thought:

> **"Wait... didn't I already have this file?"** 😅

That's exactly the kind of problem this little Python project is made for.

You choose a folder, the program searches through it, finds files that are actually the same, and puts those duplicates into groups so you can see what's going on.

It also shows where the duplicates are, how much space they are taking, and can suggest which copy might be better to keep.

But don't worry — the program doesn't go around deleting your files on its own.

The final decision is always yours.

The main idea is simple:

> **If a task is repetitive, let Python do it.**

---

## 🎯 Why I Built This

Duplicate files have a funny way of appearing when we're not looking.

They can come from:

* Downloading the same file multiple times
* Copying projects
* Creating backups
* Transferring files between drives
* Keeping multiple copies of the same document
* Forgetting that a file already exists

For example:

```text
Downloads/
├── report.pdf
├── report_copy.pdf
├── report_final.pdf
├── photo.jpg
├── photo_backup.jpg
├── project.zip
└── ...
```

Finding them manually is fine when you have five files. It gets much less fun when you have 500... or 5,000.

Instead of opening files and playing **"Are these two the same?"**, this project lets Python do the boring detective work.

You select a folder, run the program, and it looks for files that contain exactly the same data.

And yes, I know there are already plenty of duplicate file finders out there. So why build another one?

Because this project isn't about pretending that I invented the idea of finding duplicate files. It's about understanding how one can be built from scratch with Python.

I wanted to take a problem that already has solutions, break it into small pieces, and build my own version from scratch — something I can understand, change, break, fix, and learn from.

In other words:

> **I'm not reinventing the wheel. I'm learning how to build one.**

---

## ⚙️ How It Works — The Detective Work 🕵️

The program follows a simple trail:

```text
Select Folder
     ↓
Scan Files
     ↓
Group Files by Size
     ↓
Calculate Hashes
     ↓
Compare Hashes
     ↓
Group Exact Duplicates
     ↓
Analyze Duplicate Groups
     ↓
Calculate Potential Space
     ↓
Generate Recommendations
     ↓
User Reviews Results
     ↓
Optional Confirmed Cleanup
     ↓
Generate Report
```

The program doesn't immediately read every file from beginning to end.

First, it checks their sizes. If two files have different sizes, they can't be exact duplicates. Case closed. 🔍

That means there is no reason to spend time reading their contents.

Only files with the same size move to the next step.

```text
File A
   ↓
Size: 2.4 MB
```

```text
File B
   ↓
Size: 2.4 MB
```

If their sizes match, the program takes a closer look by calculating a **hash**.

A hash is basically a tiny fingerprint for a file. It is created from the file's contents, so if the contents change, the fingerprint changes too.

```text
File A → SHA-256 → A8F42C91...
File B → SHA-256 → A8F42C91...
```

If the files have the same size and the same SHA-256 hash, the program treats them as exact duplicates.

**SHA-256** is simply the method we use to make that fingerprint.

So instead of comparing two huge files byte by byte right away, we can compare their fingerprints.

---

## 🧠 What Makes It "Smart"?

It doesn't just shout **"Duplicate!"** and walk away. 😄

It gives you some useful context about each group.

It analyzes each duplicate group and provides useful information such as:

* Number of copies
* File size
* File locations
* Modification dates
* Potential recoverable storage
* A recommendation for which copy could be kept

For example:

```text
Duplicate Group #1
────────────────────────────────

Copies: 3
File Size: 24.6 MB
Potential Space: 49.2 MB

Locations:

1. C:\Projects\report.pdf
   Modified: 18 Aug 2026

2. C:\Downloads\report_copy.pdf
   Modified: 15 Aug 2026

3. D:\Backup\report.pdf
   Modified: 10 Aug 2026

Recommendation:
Keep #1

Reason:
- Located in the selected working directory
- Most recently modified

⚠ Recommendation only — review before deleting.
```

The recommendation is only a **suggestion**, not a magic answer.

The program can't know which copy is important to you. For example, an older file might be a backup that you really want to keep.

So the program does the detective work, gives you the clues, and lets **you** make the final decision.

---

## 📋 The Rulebook 📖

The project keeps its **rules** separate from the main Python code.

Think of `rules.json` as the program's little rulebook. Instead of digging through the main code every time we want to change a rule, we can change the rulebook.

For example:

```text
Smart Duplicate File Finder
│
├── Main Program
│   └── Scanning and duplicate detection
│
└── Rules
    └── Recommendation preferences
```

The rules can control things such as:

* Which hash method to use
* How duplicate recommendations should work
* Whether some files should be ignored
* Whether hidden files should be included
* Other simple scanning preferences

We will keep this rulebook small and easy to understand.

The goal is to make the program easier to change, not to create a complicated settings system.

---

## 🔐 So... How Does It Actually Know?

The filename doesn't matter.

`report.pdf` and `pizza.txt` could theoretically be duplicates if their actual contents are the same. The program cares about what's inside, not what the file is called.

For example:

```text
report.pdf
report_copy.pdf
final_report.pdf
```

These files may have completely different names but still contain identical data.

The program cares about what is actually inside the files.

The detection process is:

```text
Different Size
     ↓
Not a duplicate
```

```text
Same Size
     ↓
Calculate SHA-256
     ↓
Different Hash
     ↓
Not a duplicate
```

```text
Same Size
     ↓
Calculate SHA-256
     ↓
Same Hash
     ↓
Exact Duplicate
```

The program calculates the hash in small **chunks** instead of loading a huge file into memory all at once.

In simple terms: read a little → update the fingerprint → read a little more → repeat until the file is finished.

This makes it easier to work with large files without using a huge amount of memory.

---

## 💾 How Much Space Is Hiding in There?

The program also works out how much storage is sitting inside those extra copies.

For example:

```text
File Size: 100 MB
Copies: 3
```

One copy needs to remain.

Therefore:

```text
100 MB × (3 - 1)

Potential Recoverable Space:
200 MB
```

This is only an estimate of **potential** storage recovery.

For example, if the program says you could recover 2 GB, that doesn't mean 2 GB has already been freed. It is simply showing what could be freed if the extra copies were removed.

---

## 📍 Where Did All Those Copies Come From?

The program displays the location of every file in a duplicate group.

Example:

```text
Duplicate Group #1

File Size: 12.4 MB
Copies: 3

Locations:

1. C:\Users\User\Documents\report.pdf
2. C:\Users\User\Downloads\report_copy.pdf
3. D:\Backup\report.pdf
```

This makes it easy to see where the copies are before deciding what to do with them.

---

## 🛡️ No Surprise Deletions

The program is designed to help avoid the classic **"Oh no... I didn't mean to delete that!"** moment.

### The program does not automatically delete duplicates.

The workflow is:

```text
Find duplicates
      ↓
Show information
      ↓
Provide recommendation
      ↓
User selects files
      ↓
Ask for confirmation
      ↓
Perform cleanup
```

Deletion requires explicit user confirmation.

Recommendations are suggestions only.

You remain in control of which files should be kept or removed.

The program will also try to handle common file problems, such as folders it cannot access or files that disappear while the scan is running.

It will not follow shortcuts/symbolic links by default, helping keep the scan safer and simpler.

---

## 📂 Project Structure

```text
02-Duplicate-File-Finder/
│
├── README.md
├── duplicate_finder.py
├── rules.json
└── sample-output.txt
```

### `duplicate_finder.py`

The main Python program.

This is the main Python file. It handles things like:

* Scanning directories
* Finding files
* Comparing file sizes
* Calculating hashes
* Detecting duplicates
* Grouping results
* Analyzing duplicate groups
* Generating recommendations
* Handling cleanup
* Generating reports

### `rules.json`

Contains the small set of rules used by the program.

Keeping these rules outside the main code makes the project easier to understand and change.

### `sample-output.txt`

Contains an example of what the program looks like when it runs.

---

## 🚀 Getting Started

### Requirements

* Python 3.11 or newer
* No extra Python packages are needed

### Run the program

Move into the project directory:

```text
cd 02-Duplicate-File-Finder
```

Then run:

```text
python duplicate_finder.py
```

The program will ask you which folder you want to scan.

---

## 💻 Example

Before running the program:

```text
Downloads/
├── report.pdf
├── report_copy.pdf
├── photo.jpg
├── photo_backup.jpg
└── project.zip
```

After scanning, the program may report:

```text
Duplicate Group #1
────────────────────────────────

Copies: 2
File Size: 2.4 MB
Potential Space: 2.4 MB

Locations:

1. C:\Users\User\Downloads\report.pdf
2. C:\Users\User\Downloads\report_copy.pdf

Recommendation:
Keep #1

⚠ Recommendation only — review before deleting.
```

The program will also show a final summary when the scan is finished.

See [`sample-output.txt`](sample-output.txt) for an example execution.

---

## 📊 At the End of the Hunt

After the scan, the program provides an overview of the results.

Example:

```text
========================================
           SCAN COMPLETE
========================================

Files scanned       : 1,284
Duplicate groups    : 37
Duplicate files     : 82
Potential space     : 4.72 GB

Recommendations     : 37
Files deleted       : 0

Report saved to:
duplicate-report.txt
```

The summary gives you the quick version of what happened without making you count everything yourself.

---

## ⚠️ Current Limitations

This project focuses on **exact duplicates**.

It does not currently try to find files that are only similar.

For example:

```text
photo.jpg
photo_edited.jpg
```

These files may look similar to a person but contain different data.

They will not be treated as duplicates unless their actual contents match.

The program also can't know which file is most valuable to you.

Its recommendations are based on simple rules and information such as file location and modification date. They are suggestions, not automatic decisions.

---

## 🛠️ Roadmap

### Version 1.0

* Recursive folder scanning
* File size comparison
* Chunk-based SHA-256 hashing
* Exact duplicate detection
* Duplicate grouping
* File locations
* File size information
* Modification dates
* Potential storage calculation
* Configurable recommendation rules
* Duplicate recommendations
* Interactive duplicate inspection
* User-confirmed deletion
* Duplicate report
* Final scan summary
* Safe handling of common file-system errors

### Version 2.0

* Better filtering options
* Ignore selected folders
* Improved cleanup workflow
* Recycle Bin support
* More detailed reports
* Better handling of very large directories
* Additional configuration options

### Future

* Similar-file detection
* More advanced recommendations
* Scheduled duplicate scans
* Additional report formats
* Further automation features

---

## 🧠 What I'm Learning From It

This project is about using Python to solve a real and slightly annoying file-management problem — while learning what is actually happening under the hood.

While building it, I get to practice things like:

* File and directory handling
* Recursive directory scanning
* File hashing — creating a fingerprint from a file's contents
* Chunk-based file processing
* Dictionaries
* Lists and sets
* Functions
* Input validation
* Exception handling
* Data grouping
* File metadata — information about a file, such as its size and modified date
* Storage calculations
* Configuration files — keeping settings outside the main code
* Safe file operations
* Command-line interaction
* Basic automation design

---

## 📌 The Bigger Idea

The goal isn't to build some giant file-management application.

The goal is much simpler: take a boring task that people normally do by hand and let Python handle the repetitive part.

```text
Manual searching
      ↓
Run the program
      ↓
Find and understand duplicates
      ↓
Review recommendations
      ↓
Clean up if necessary
```

Python handles the boring searching and comparison. You handle the important decisions.

> **Automate the repetitive work. Keep the final decision with the user.**

That's the core idea behind this Automation project.

---

## 📄 License

This project is open source and available under the license included in this repository.
