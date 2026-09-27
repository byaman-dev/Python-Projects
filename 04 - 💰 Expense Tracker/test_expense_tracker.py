"""
Tests for Expense Tracker (SQLite version)

Run with:
    python -m unittest "test_expense_tracker.py" -v

These tests load "Expense Tracker.py" directly (it has spaces in the
filename, so it can't be imported the normal way) and point it at a
temporary database file for each test, so nothing here ever touches
your real expenses.db.
"""

import importlib.util
import io
import os
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch


def load_tracker_module():
    """
    Load "Expense Tracker.py" as a module even though its filename
    contains spaces and parentheses.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "Expense Tracker.py")

    spec = importlib.util.spec_from_file_location("expense_tracker", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tracker = load_tracker_module()


class ExpenseTrackerTests(unittest.TestCase):

    def setUp(self):
        # Point the module at a fresh temp database for this test only.
        self.temp_db = tempfile.NamedTemporaryFile(
            suffix=".db", delete=False
        )
        self.temp_db.close()

        tracker.DB_FILE = self.temp_db.name
        tracker.init_db()

    def tearDown(self):
        os.remove(self.temp_db.name)

    # ------------------------------------------------
    # init_db
    # ------------------------------------------------

    def test_init_db_creates_expenses_table(self):
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='expenses'"
        )
        table = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(table, "expenses table should exist after init_db()")

    def test_init_db_is_safe_to_call_twice(self):
        # Calling it again should not raise or wipe existing data.
        with patch("builtins.input", side_effect=["Food", "Lunch", "100"]):
            tracker.add_expense()

        tracker.init_db()
        rows = tracker.fetch_all_expenses()
        self.assertEqual(len(rows), 1)

    # ------------------------------------------------
    # add_expense / fetch_all_expenses
    # ------------------------------------------------

    def test_add_expense_stores_correct_values(self):
        with patch("builtins.input", side_effect=["Food", "Lunch", "150"]):
            tracker.add_expense()

        rows = tracker.fetch_all_expenses()
        self.assertEqual(len(rows), 1)

        _, category, description, amount, expense_date = rows[0]
        self.assertEqual(category, "Food")
        self.assertEqual(description, "Lunch")
        self.assertEqual(amount, 150.0)
        self.assertTrue(expense_date)  # a date string was recorded

    def test_add_expense_rejects_invalid_amount_then_accepts_valid_one(self):
        # "abc" and "-5" should both be rejected before "75" succeeds.
        with patch("builtins.input",
                    side_effect=["Travel", "Bus", "abc", "-5", "75"]):
            tracker.add_expense()

        rows = tracker.fetch_all_expenses()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][3], 75.0)

    def test_fetch_all_expenses_empty_by_default(self):
        self.assertEqual(tracker.fetch_all_expenses(), [])

    # ------------------------------------------------
    # show_total
    # ------------------------------------------------

    def test_show_total_sums_all_expenses(self):
        with patch("builtins.input", side_effect=["Food", "Lunch", "100"]):
            tracker.add_expense()
        with patch("builtins.input", side_effect=["Travel", "Bus", "50"]):
            tracker.add_expense()

        output = io.StringIO()
        with redirect_stdout(output):
            tracker.show_total()

        self.assertIn("150", output.getvalue())

    def test_show_total_handles_no_expenses(self):
        output = io.StringIO()
        with redirect_stdout(output):
            tracker.show_total()

        self.assertIn("No expenses recorded", output.getvalue())

    # ------------------------------------------------
    # delete_expense
    # ------------------------------------------------

    def test_delete_expense_removes_correct_row(self):
        with patch("builtins.input", side_effect=["Food", "Lunch", "100"]):
            tracker.add_expense()
        with patch("builtins.input", side_effect=["Travel", "Bus", "50"]):
            tracker.add_expense()

        rows_before = tracker.fetch_all_expenses()
        lunch_id = rows_before[0][0]

        with patch("builtins.input", side_effect=[str(lunch_id)]):
            tracker.delete_expense()

        rows_after = tracker.fetch_all_expenses()
        self.assertEqual(len(rows_after), 1)
        self.assertEqual(rows_after[0][2], "Bus")

    def test_delete_expense_rejects_invalid_id_then_accepts_valid_one(self):
        with patch("builtins.input", side_effect=["Food", "Lunch", "100"]):
            tracker.add_expense()

        real_id = tracker.fetch_all_expenses()[0][0]
        fake_id = real_id + 999

        with patch("builtins.input", side_effect=[str(fake_id), str(real_id)]):
            tracker.delete_expense()

        self.assertEqual(tracker.fetch_all_expenses(), [])

    def test_delete_expense_handles_no_expenses(self):
        output = io.StringIO()
        with redirect_stdout(output):
            tracker.delete_expense()

        self.assertIn("No expenses recorded", output.getvalue())


if __name__ == "__main__":
    unittest.main()
