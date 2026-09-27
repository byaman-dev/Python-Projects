# 💰 Expense Tracker

> Where did my money go? This project exists so I never have to ask that question and shrug.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Storage](https://img.shields.io/badge/Storage-SQLite-lightgrey?style=for-the-badge&logo=sqlite)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

---

## 🤔 Why this exists

I kept spending money and having absolutely no idea where it went by the end of the week. So instead of downloading some app with 40 permissions I didn't understand, I built my own — a small command-line tool that just asks "what did you spend, on what, how much" and remembers it for me.

Small problem, small tool. That's the whole pitch.

---

## 🧪 The plot twist

The first version of this "kept" my expenses in a plain Python list. Which sounds fine until you realize a list living in memory disappears the moment the program closes. So technically, v1 was less "expense tracker" and more "expense forgetter" — it worked perfectly for exactly as long as you didn't close the terminal.

v2 fixes that by handing the job to SQLite, a real (tiny) database that lives on disk. Close the terminal, shut down the laptop, come back next week — your expenses are still there. Wild concept, I know.

---

## ✨ What it actually does

* ➕ Add an expense — category, description, amount, and it quietly timestamps it with today's date
* 📋 View everything you've logged, neatly lined up in a table
* 💰 Ask it for your running total, no mental math required
* 🗑 Delete an expense by its ID — no more "wait, did deleting #3 just turn #4 into #3?" confusion
* ⚠ It will not accept "banana" as a valid amount, and it will tell you so

---

## 🧠 What building this taught me

* How to actually **persist** data instead of pretending a Python list is a database
* Writing real SQL — `CREATE TABLE`, `INSERT`, `SELECT`, `DELETE` — instead of just reading about it
* Why IDs are safer than list positions the moment deletion is involved
* That input validation is 80% of what makes a CLI tool feel trustworthy instead of fragile
* Structuring a program so the "brain" (database logic) and the "face" (menu/printing) don't get tangled together

---

## 📁 What's in the folder

```text
04 - Expense Tracker
│
├── Expense Tracker.py         → the actual program
├── test_expense_tracker.py    → automated tests (10 of them, all green)
├── README.md                  → you are here
├── requirements.txt
└── sample-output.txt
```

No `expenses.db` is committed — it gets created automatically the first time you run the program, right next to the script.

---

## ▶️ Running it

```bash
# grab the project
git clone <repository-url>
cd "04 - Expense Tracker"

# run it
python "Expense Tracker.py"
```

First run creates `expenses.db` for you. Every run after that just uses it.

---

## 🧪 Running the tests

Curious whether it actually works, or just want to poke it before trusting it with your data? Same instinct I had.

```bash
python -m unittest "test_expense_tracker.py" -v
```

The tests spin up a **temporary, throwaway database** for each check — your real `expenses.db` is never touched. They cover the boring-but-important stuff: adding an expense actually saves it, invalid amounts get rejected, deleting by ID removes the right row (and only the right row), and totals add up correctly.

---

## 💻 What it looks like

```text
=============================================
          EXPENSE TRACKER
=============================================
1. Add Expense
2. View Expenses
3. Show Total Expenses
4. Delete Expense
5. Exit
=============================================
Select an option (1-5): 1

Add New Expense
------------------------------
Category    : Food
Description : Lunch
Amount (₹)  : 250

✅ Expense added successfully.
```

---

## 🚀 Where this could go next

* Filter expenses by date or category (the data's already there, just needs a query)
* Monthly or weekly spending summaries
* Edit an existing expense instead of delete-and-redo
* Export to CSV for spreadsheet people
* Maybe, eventually, a GUI — but the terminal version has to earn that upgrade first

---

## 🌱 The honest reflection

The interesting part of this project wasn't the menu or the print statements — it was realizing, halfway through, that "store data" and "don't lose data" are two completely different problems, and my first version only solved the first one. Fixing that meant learning just enough SQL to be dangerous, and rethinking how delete should work once records have a permanent identity instead of just a spot in a list.

Small tool. Real lesson.

---

## 📌 Quick facts

| Property       | Details                     |
| -------------- | ---------------------------- |
| **Project**    | Expense Tracker               |
| **Language**   | Python                        |
| **Storage**    | SQLite                        |
| **Tests**      | ✅ 10/10 passing               |
| **Status**     | ✅ Completed                   |

---

> *"A list remembers things until you close it. A database remembers things until you delete it. That difference is the whole point of this project."*
