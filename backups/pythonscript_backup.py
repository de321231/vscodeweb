"""
Personal Expense Tracker
------------------------
Features:
- Add new expenses with categories and dates
- View all expenses in a table format
- Search expenses by category or date
- Save and load expenses from a CSV file
- Generate a spending summary and pie chart
"""

import csv
import os
import datetime
from typing import List, Dict
import matplotlib.pyplot as plt
import math

# =============================
# Data Model
# =============================

class Expense:
    def __init__(self, date: str, category: str, description: str, amount: float):
        self.date = date
        self.category = category
        self.description = description
        self.amount = amount

    def to_dict(self) -> Dict[str, str]:
        return {
            "date": self.date,
            "category": self.category,
            "description": self.description,
            "amount": f"{self.amount:.2f}"
        }

    def __str__(self):
        return f"{self.date} | {self.category:15} | {self.description:30} | ${self.amount:>8.2f}"


# =============================
# Expense Tracker Logic
# =============================

class ExpenseTracker:
    def __init__(self, filename="expenses.csv"):
        self.filename = filename
        self.expenses: List[Expense] = []
        self.load_expenses()

    def add_expense(self, expense: Expense):
        print("Adding new expense...")
        self.expenses.append(expense)
        self.save_expenses()

    def save_expenses(self):
        with open(self.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "category", "description", "amount"])
            writer.writeheader()
            for exp in self.expenses:
                writer.writerow(exp.to_dict())
        print("Expenses saved successfully.")

    def load_expenses(self):
        if not os.path.exists(self.filename):
            print("No existing expense file found. Starting fresh.")
            return
        with open(self.filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.expenses = [Expense(r["date"], r["category"], r["description"], float(r["amount"])) for r in reader]
        print(f"Loaded {len(self.expenses)} expenses from file.")

    def format_amount(self, amount: float) -> str:
        s = f"{amount:,.2f}"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{s}€"

    def parse_amount(self, s: str) -> float:
        if s is None:
            raise ValueError("Kein Betrag angegeben")
        s = s.strip()
        s = s.replace("€", "").replace(" ", "").replace("\xa0", "")
        if not s:
            raise ValueError("Leerer Betrag")
        if "." in s and "," in s:
            s = s.replace(".", "").replace(",", ".")
        else:
            if "," in s and "." not in s:
                s = s.replace(",", ".")
        return float(s)

    def view_expenses(self):
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        date_w = max(10, max((len(exp.date) for exp in self.expenses), default=10))
        cat_w = max(len("Category"), max((len(exp.category) for exp in self.expenses), default=8))
        desc_w = max(len("Description"), max((len(exp.description) for exp in self.expenses), default=30))
        all_amounts = [self.format_amount(exp.amount) for exp in self.expenses]
        all_amounts.append(self.format_amount(self.get_total()))
        amt_w = max(len("Amount"), max((len(a) for a in all_amounts), default=12))
        total_width = date_w + 3 + cat_w + 3 + desc_w + 3 + amt_w

        header = f"{'Date':<{date_w}} | {'Category':<{cat_w}} | {'Description':<{desc_w}} | {'Amount':>{amt_w}}"
        print("\n" + header)
        print("-" * total_width)

        for exp in self.expenses:
            date_field = f"{exp.date:<{date_w}}"
            cat_field = f"{exp.category:<{cat_w}}"
            desc_field = f"{exp.description:<{desc_w}}"
            amt_field = f"{self.format_amount(exp.amount):>{amt_w}}"
            print(f"{date_field} | {cat_field} | {desc_field} | {amt_field}")

        print("-" * total_width)
        total_label_width = date_w + 3 + cat_w + 3 + desc_w
        print(f"{'Total Expenses:':<{total_label_width}} {self.format_amount(self.get_total()):>{amt_w}}")

    def get_total(self) -> float:
        return sum(exp.amount for exp in self.expenses)

    def search_by_category(self, category: str):
        results = [exp for exp in self.expenses if exp.category.lower() == category.lower()]
        print(f"\nExpenses in category '{category}':")
        for exp in results:
            print(exp)
        if not results:
            print("No matching expenses found.")

    def search_by_date(self, date: str):
        results = [exp for exp in self.expenses if exp.date == date]
        print(f"\nExpenses on date '{date}':")
        for exp in results:
            print(exp)
        if not results:
            print("No matching expenses found.")

    def plot_summary(self):
        if not self.expenses:
            print("No data to plot.")
            return
        category_totals = {}
        for exp in self.expenses:
            try:
                amt = float(exp.amount)
            except Exception:
                continue
            if math.isnan(amt):
                continue
            category_totals[exp.category] = category_totals.get(exp.category, 0) + amt
        filtered = {k: v for k, v in category_totals.items() if v is not None and not math.isnan(v) and v > 0}
        if not filtered:
            print("Keine positiven Beträge zum Darstellen.")
            return
        categories = list(filtered.keys())
        totals = list(filtered.values())
        plt.figure(figsize=(8, 6))
        plt.pie(totals, labels=categories, autopct="%1.1f%%", startangle=90)
        plt.title("Expense Breakdown by Category")
        plt.show()


# =============================
# User Interface
# =============================

def main_menu():
    tracker = ExpenseTracker()

    while True:
        print("\n=== Personal Expense Tracker ===")
        print("1. Add new expense")
        print("2. View all expenses")
        print("3. Search by category")
        print("4. Search by date")
        print("5. Show summary chart")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            try:
                date = input("Enter date (YYYY-MM-DD): ").strip()
                # validate date
                datetime.datetime.strptime(date, "%Y-%m-%d")
                category = input("Enter category: ").strip()
                description = input("Enter description: ").strip()
                amount_input = input("Enter amount: ").strip()
                amount = tracker.parse_amount(amount_input)
                tracker.add_expense(Expense(date, category, description, amount))
            except ValueError:
                print("Invalid input. Please check your entries.")
        elif choice == "2":
            tracker.view_expenses()
        elif choice == "3":
            category = input("Enter category to search: ").strip()
            tracker.search_by_category(category)
        elif choice == "4":
            date = input("Enter date to search (YYYY-MM-DD): ").strip()
            tracker.search_by_date(date)
        elif choice == "5":
            tracker.plot_summary()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


# =============================
# Entry Point
# =============================

if __name__ == "__main__":
    main_menu()
