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

# ANSI escape sequences for colors
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RED = "\033[91m"
PURPLE = "\033[95m"
ORANGE = "\033[38;5;214m"  # Custom orange color

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
        # Format: 1.234.567,89€
        s = f"{amount:,.2f}"               # => "1,234,567.89"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{s}€"

    def parse_amount(self, s: str) -> float:
        """
        Akzeptiert Eingaben wie:
          "1,50" -> 1.5
          "1.234,50" -> 1234.5
          "1234.50" -> 1234.5
          "€ 1.234,50" -> 1234.5
        """
        if s is None:
            raise ValueError("Kein Betrag angegeben")
        s = s.strip()
        # remove currency symbol and spaces/non-breaking spaces
        s = s.replace("€", "").replace(" ", "").replace("\xa0", "")
        if not s:
            raise ValueError("Leerer Betrag")
        # Wenn sowohl Punkt als auch Komma vorhanden: Punkt als Tausender, Komma als Dezimal
        if "." in s and "," in s:
            s = s.replace(".", "").replace(",", ".")
        else:
            # Nur Komma => Komma als Dezimal markieren
            if "," in s and "." not in s:
                s = s.replace(",", ".")
            # Nur Punkt => Standard-Parsing (ggf. bereits Dezimal)
            # Falls tausender mit space schon entfernt, ok
        return float(s)

    def view_expenses(self):
        if not self.expenses:
            print("No expenses recorded yet.")
            return

        # dynamische Spaltenbreiten ermitteln
        date_w = max(10, max((len(exp.date) for exp in self.expenses), default=10))
        cat_w = max(len("Category"), max((len(exp.category) for exp in self.expenses), default=8))
        desc_w = max(len("Description"), max((len(exp.description) for exp in self.expenses), default=30))
        # Breite der Amount-Spalte anhand formatierten Beträgen
        all_amounts = [self.format_amount(exp.amount) for exp in self.expenses]
        all_amounts.append(self.format_amount(self.get_total()))
        amt_w = max(len("Amount"), max((len(a) for a in all_amounts), default=12))

        # Gesamtbreite für Trennlinie
        total_width = date_w + 3 + cat_w + 3 + desc_w + 3 + amt_w

        # Kopfzeile
        header = f"{'Date':<{date_w}} | {'Category':<{cat_w}} | {'Description':<{desc_w}} | {'Amount':>{amt_w}}"
        print("\n" + header)
        print("-" * total_width)

        # Zeilen
        for exp in self.expenses:
            date_field = f"{PURPLE}{exp.date:<{date_w}}{RESET}"
            cat_field = f"{GREEN}{exp.category:<{cat_w}}{RESET}"
            desc_field = f"{BLUE}{exp.description:<{desc_w}}{RESET}"
            amt_field = f"{ORANGE}{self.format_amount(exp.amount):>{amt_w}}{RESET}"
            print(f"{date_field} | {cat_field} | {desc_field} | {amt_field}")

        print("-" * total_width)
        # Total: linke Fläche auffüllen, Amount rechtsbündig unter Amount-Spalte
        total_label_width = date_w + 3 + cat_w + 3 + desc_w
        print(f"{YELLOW}{'Total Expenses:':<{total_label_width}}{RESET} {ORANGE}{self.format_amount(self.get_total()):>{amt_w}}{RESET}")

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
            category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount

        categories = list(category_totals.keys())
        totals = list(category_totals.values())

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
        print(f"\n{CYAN}=== Personal Expense Tracker ==={RESET}")
        print(f"{GREEN}1.{RESET} Add new expense")
        print(f"{GREEN}2.{RESET} View all expenses")
        print(f"{GREEN}3.{RESET} Search by category")
        print(f"{GREEN}4.{RESET} Search by date")
        print(f"{GREEN}5.{RESET} Show summary chart")
        print(f"{GREEN}6.{RESET} Exit")

        choice = input(f"{YELLOW}Choose an option (1-6): {RESET}").strip()

        if choice == "1":
            try:
                date = input(f"{YELLOW}Enter date (YYYY-MM-DD): {RESET}").strip()
                # validate date
                datetime.datetime.strptime(date, "%Y-%m-%d")
                category = input(f"{YELLOW}Enter category: {RESET}").strip()
                description = input(f"{YELLOW}Enter description: {RESET}").strip()
                amount_input = input(f"{YELLOW}Enter amount (z.B. 1.234,50 oder 1,50): {RESET}").strip()
                try:
                    amount = tracker.parse_amount(amount_input)
                except ValueError:
                    print(f"{RED}Ungültiges Betragsformat. Bitte z.B. 1,50 oder 1.234,50 eingeben.{RESET}")
                    continue
                tracker.add_expense(Expense(date, category, description, amount))
            except ValueError:
                print(f"{RED}Invalid input. Please check your entries.{RESET}")
        elif choice == "2":
            tracker.view_expenses()
        elif choice == "3":
            category = input(f"{YELLOW}Enter category to search: {RESET}").strip()
            tracker.search_by_category(category)
        elif choice == "4":
            date = input(f"{YELLOW}Enter date to search (YYYY-MM-DD): {RESET}").strip()
            tracker.search_by_date(date)
        elif choice == "5":
            tracker.plot_summary()
        elif choice == "6":
            print(f"{GREEN}Goodbye!{RESET}")
            break
        else:
            print(f"{RED}Invalid option. Please try again.{RESET}")


# =============================
# Entry Point
# =============================

if __name__ == "__main__":
    main_menu()
