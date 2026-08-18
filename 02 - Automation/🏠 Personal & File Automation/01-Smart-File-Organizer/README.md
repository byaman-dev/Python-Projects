# 📁 Smart File Organizer

A small Python automation tool that helps organize messy folders automatically.

Instead of manually going through a folder and moving PDFs, images, videos, archives, and other files one by one, this tool reads a set of rules and organizes the files for you.

The main idea is simple:

> **If a task is repetitive, let Python do it.**

---

## 🎯 Why I Built This

Organizing files is not difficult, but it can become annoying when a folder contains dozens or hundreds of files.

For example, a Downloads folder can quickly become:

```text
Downloads/
├── photo.jpg
├── report.pdf
├── video.mp4
├── notes.txt
├── setup.exe
├── archive.zip
└── ...
```

Instead of manually sorting everything, this project automates the process.

You select the folder, run the program, and it organizes the files according to the rules you have defined.

---

## ⚙️ How It Works

The organizer follows a simple process:

```text
Select Folder
     ↓
Scan Files
     ↓
Read Rules
     ↓
Identify File Extension
     ↓
Find Matching Folder
     ↓
Create Folder if Needed
     ↓
Move File
     ↓
Show Summary
```

For example:

```text
report.pdf
    ↓
.pdf
    ↓
Documents
    ↓
Documents/report.pdf
```

---

## ✨ Features

* Organizes files automatically
* Uses file extensions to determine where files belong
* User-defined organization rules
* Creates destination folders when required
* Works with different file types
* Runs directly from the terminal
* Shows a summary after the organization is complete
* Keeps organization rules separate from the Python code

---

## 📂 Project Structure

```text
01-Smart-File-Organizer/
│
├── README.md
├── organizer.py
├── rules.txt
├── sample-output.txt
└── .gitignore
```

### `organizer.py`

The main Python program. It contains the logic responsible for scanning and organizing files.

### `rules.txt`

Contains the organization rules.

This is kept separate from the Python code so users can change how files are organized without modifying the program itself.

### `sample-output.txt`

Contains an example of what the program looks like when it is executed.

### `.gitignore`

Prevents unnecessary local or temporary files from being added to the repository.

---

## 🧩 Rules Configuration

The organizer uses `rules.txt` to decide where each file type should go.

The format is:

```text
.extension=FolderName
```

Example:

```text
# Documents
.pdf=Documents
.docx=Documents
.txt=Documents

# Images
.jpg=Images
.jpeg=Images
.png=Images

# Videos
.mp4=Videos
.mkv=Videos

# Audio
.mp3=Audio
.wav=Audio

# Archives
.zip=Archives
.rar=Archives
```

You can add or change rules depending on how you want your files organized.

For example:

```text
.py=Python
.html=Web
.csv=Data
```

would put Python files into `Python`, HTML files into `Web`, and CSV files into `Data`.

---

## 🚀 Getting Started

### Requirements

* Python 3.11 or newer
* No external Python packages are required for v1.0

### Run the program

Clone the repository and move into the project directory:

```bash
cd 01-Smart-File-Organizer
```

Then run:

```bash
python organizer.py
```

The program will ask for the folder you want to organize.

---

## 💻 Example

Before running the organizer:

```text
Downloads/
├── photo.jpg
├── certificate.pdf
├── movie.mp4
├── song.mp3
└── backup.zip
```

After running the program:

```text
Downloads/
├── Images/
│   └── photo.jpg
│
├── Documents/
│   └── certificate.pdf
│
├── Videos/
│   └── movie.mp4
│
├── Audio/
│   └── song.mp3
│
└── Archives/
    └── backup.zip
```

The terminal will also show what happened during the process.

See [`sample-output.txt`](sample-output.txt) for an example execution.

---

## ⚠️ Current Limitations

This is **Version 1.0**, so the project intentionally has a limited scope.

Currently, the organizer focuses on rule-based organization using file extensions.

Some features are planned for later versions, especially safer handling of situations where a destination already contains a file with the same name.

---

## 🛠️ Roadmap

### Version 1.0

* [x] Rule-based file organization
* [x] Configurable `rules.txt`
* [x] Automatic folder creation
* [x] Terminal-based interface
* [x] Organization summary

### Version 2.0

* [ ] Better filename conflict handling
* [ ] Safer file operations
* [ ] Improved error handling
* [ ] Better reporting of failed operations

### Future

* [ ] Preview / dry-run mode
* [ ] More organization rules
* [ ] Additional ways to classify files
* [ ] Further automation features

---

## 🧠 What I Learned

This project is mainly about learning how Python can automate repetitive tasks.

Some of the concepts involved are:

* File and directory handling
* Working with file extensions
* Reading configuration files
* Conditional logic
* Functions
* Exception handling
* Command-line interaction
* Separating configuration from program logic
* Basic automation design

---

## 📌 Project Goal

The goal of this project isn't to build a complicated application.

It's to take something that can be repetitive when done manually and reduce the amount of time and effort needed to do it.

**Manual sorting → Run the script → Organized folder**

That's the whole idea behind this Automation module.

---

## 📄 License

This project is open source and available under the license included in this repository.
