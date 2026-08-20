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
* How many duplicate groups are shown per page
* Whether cleanup requires explicit confirmation
* Whether cleanup can use the Windows Recycle Bin
* Whether report generation is enabled and what filename is used

We will keep this rulebook small and easy to understand.

The goal is to make the program easier to change, not to create a complicated settings system.

For example, changing the hash chunk size or the number of groups displayed per page can be done directly in `rules.json` without changing the Python code.

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

## 🧯 What Went Wrong While Building It?

This project was not built in one clean pass. Several parts had to be tested, broken, debugged, and corrected before the final workflow worked reliably.

That is an important part of the project too. The final program shows the result, but the development process included failures at different stages.

### 1. 📂 File Scanning — The First Layer Had to Be Verified

The first stage is deceptively simple: find every file inside the selected folder.

The problem is that the rest of the program is only as reliable as this list. If recursive scanning misses a subfolder or includes something it should not, every later calculation becomes wrong.

So this stage was tested separately with files in the main folder and inside subfolders.

**Failure risk:** an incomplete or incorrect file list would produce incorrect duplicate results.

**Fix:** isolate recursive scanning as its own function and test the returned paths before moving on to duplicate detection.

### 2. 📏 File-Size Grouping — Same Size Does Not Mean Duplicate

The size filter is an optimisation, not proof of duplication.

Two completely different files can have exactly the same size. Treating them as duplicates would be a serious logic error.

**Failure:** files with the same size were able to reach the duplicate-checking stage even though their contents could be different.

**Fix:** use file size only as the first filter, then require a matching content hash before declaring an exact duplicate.

This distinction is also covered by the automated tests for same-size, different-content files.

### 3. 🔐 Hashing — The Fingerprint Had to Be Tested Independently

Hashing is the point where the program actually examines file contents, so a mistake here could make the entire detector unreliable.

The SHA-256 implementation was therefore tested against known content and against invalid hash-algorithm input. Empty files were also included in testing because they are a valid edge case and still need a deterministic hash.

**Failure risk:** an incorrect algorithm, incorrect file reading, or incorrect chunk handling could produce the wrong fingerprint and therefore the wrong duplicate decision.

**Fix:** test hashing independently before relying on it in the full duplicate-detection pipeline.

### 4. 🧩 Duplicate Grouping — The Pipeline Needed More Than One Check

The detector had to prove two things:

```text
Same Size
    ↓
Same Hash
    ↓
Exact Duplicate
```

and also correctly reject:

```text
Same Size
    ↓
Different Hash
    ↓
Not a Duplicate
```

The empty-file case and groups containing three identical files were also tested because simple two-file examples do not cover every grouping situation.

### 5. 🧠 Recommendations — A Correct Recommendation Must Not Change Files

The recommendation system is intentionally separate from cleanup.

One important safety requirement was that generating a recommendation must not modify the files it is analysing.

**Failure risk:** mixing recommendation logic with file operations could accidentally turn a suggestion into an unwanted modification.

**Fix:** recommendations only analyse metadata and return a suggested file to keep plus removal candidates. Actual cleanup happens later and requires a separate user action.

The recommendation strategies are also tested independently, including `newest`, `oldest`, and `shortest_path`.

### 6. 📋 Rules Connection — Configuration Must Not Be Trusted Blindly

`rules.json` is deliberately kept outside the Python code, but that creates another failure point: the configuration file can be missing, malformed, or contain unexpected values.

**Failure:** invalid JSON can prevent the program from receiving usable configuration.

**Fix:** the rules loader was tested with both valid JSON and invalid JSON. The program can fall back safely instead of treating a broken configuration file as a successful configuration.

This is why the rulebook is not just documentation — it is an actual tested part of the program.

### 7. 🗑️ Cleanup — The Most Dangerous Stage Needed the Strongest Tests

Cleanup is where a logic mistake can cause real data loss, so it was tested separately from detection.

The cleanup tests specifically cover:

* Selecting multiple files
* Protecting the recommended file
* Invalid selections
* Wrong confirmation text
* Permanent deletion
* Successful deletion of only the selected files

The interactive workflow was also manually tested using the Windows Recycle Bin. A duplicate was selected, confirmation was required, the duplicate was moved to the Recycle Bin, and a follow-up scan confirmed that it was no longer detected.

The important lesson here was simple:

> **Finding a duplicate is not permission to delete it.**

### 8. 📄 Reporting — The Report Had to Reflect the Whole Run

Report generation is another stage where it is easy for the program to appear successful while producing incomplete information.

The report was therefore tested for the presence of the major sections:

* Scan information
* Duplicate groups
* Recommendations
* Cleanup results

This makes the report part of the tested workflow rather than an unverified extra feature.

### 9. 🧪 The Development Process Itself Had Failures

Not every failure was inside the final application logic.

During development, an early code-edit attempt failed because the expected source-file context did not match the actual file. The change could not safely be applied without first checking the current code.

That was a useful reminder for the project itself:

> **Don't assume the code is in the state you think it is. Check it before changing it.**

The final implementation was then tested as individual functions and as a complete pipeline instead of relying only on visual inspection.

### What This Changed About the Project

The final version is therefore not simply:

```text
Write code → It works
```

It is closer to:

```text
Build a stage
     ↓
Test it
     ↓
Find a failure or edge case
     ↓
Understand what went wrong
     ↓
Fix the logic
     ↓
Test again
     ↓
Connect it to the next stage
```

That debugging process is one of the main things this project was built to teach.

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

Contains the configurable rules used by the program, including hashing, recommendation strategy, display pagination, cleanup behavior, and reporting settings.

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

The program can also generate a detailed `duplicate-report.txt` report containing the scan information, duplicate groups, recommendations, and cleanup results.

---

## 🧪 Testing

The project includes a test suite covering the main detection, analysis, recommendation, cleanup, configuration, and reporting logic.

The current test suite passes:

```text
24 passed
```

The tests cover areas such as:

* Recursive folder scanning
* File-size grouping
* SHA-256 hashing
* Exact duplicate detection
* Same-size but different-content files
* Empty-file duplicates
* Duplicate-group analysis and storage calculations
* Recommendation strategies
* Recommendation safety
* File-size formatting
* Group selection and validation
* Confirmed permanent cleanup
* Invalid cleanup selections
* Incorrect cleanup confirmation
* Report generation
* Valid and invalid `rules.json` files
* No-duplicate scanning pipeline
* Multiple identical files

In addition to automated tests, the interactive workflow has been manually tested with real files, including duplicate detection, recommendation display, report generation, Recycle Bin cleanup, and a follow-up scan confirming that the cleaned duplicate was no longer detected.

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

### Version 1.0 — Completed ✅

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
* Recycle Bin cleanup on Windows
* Duplicate report
* Final scan summary
* Safe handling of common file-system errors

### Version 2.0

* Better filtering options
* Ignore selected folders
* Improved cleanup workflow
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
