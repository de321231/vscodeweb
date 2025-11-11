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
import getpass
import sys

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
        # Punkt+Komma => Punkt Tausender, Komma Dezimal
        if "." in s and "," in s:
            s = s.replace(".", "").replace(",", ".")
        else:
            # Nur Komma => Komma als Dezimal markieren
            if "," in s and "." not in s:
                s = s.replace(",", ".")
        return float(s)

    def delete_entry(self, index: int) -> bool:
        """
        Löscht einen Eintrag anhand 1-basierter Nummer. Gibt True bei Erfolg zurück.
        """
        if index < 1 or index > len(self.expenses):
            return False
        # entferne Eintrag
        del self.expenses[index - 1]
        self.save_expenses()
        return True

    def view_expenses(self):
        if not self.expenses:
            print("Noch keine Ausgaben erfasst.")
            return

        # dynamische Spaltenbreiten ermitteln (inkl. Nr.)
        nr_w = max(len("Nr."), len(str(len(self.expenses))))
        date_w = max(10, max((len(exp.date) for exp in self.expenses), default=10))
        cat_w = max(len("Kategorie"), max((len(exp.category) for exp in self.expenses), default=8))
        desc_w = max(len("Beschreibung"), max((len(exp.description) for exp in self.expenses), default=30))
        # Breite der Betrag-Spalte anhand formatierter Beträge
        all_amounts = [self.format_amount(exp.amount) for exp in self.expenses]
        all_amounts.append(self.format_amount(self.get_total()))
        amt_w = max(len("Betrag"), max((len(a) for a in all_amounts), default=12))

        # Gesamtbreite für Trennlinie
        total_width = nr_w + 3 + date_w + 3 + cat_w + 3 + desc_w + 3 + amt_w

        # Kopfzeile (Deutsch) mit Nr.
        header = f"{'Nr.':<{nr_w}} | {'Datum':<{date_w}} | {'Kategorie':<{cat_w}} | {'Beschreibung':<{desc_w}} | {'Betrag':>{amt_w}}"
        print("\n" + header)
        print("-" * total_width)

        # Zeilen mit Nummern
        for i, exp in enumerate(self.expenses, start=1):
            nr_field = f"{PURPLE}{i:<{nr_w}}{RESET}"
            date_field = f"{PURPLE}{exp.date:<{date_w}}{RESET}"
            cat_field = f"{GREEN}{exp.category:<{cat_w}}{RESET}"
            desc_field = f"{BLUE}{exp.description:<{desc_w}}{RESET}"
            amt_field = f"{ORANGE}{self.format_amount(exp.amount):>{amt_w}}{RESET}"
            print(f"{nr_field} | {date_field} | {cat_field} | {desc_field} | {amt_field}")

        print("-" * total_width)
        # Gesamteinahmen (Netto: Einnahmen minus Ausgaben)
        total_label_width = nr_w + 3 + date_w + 3 + cat_w + 3 + desc_w
        print(f"{YELLOW}{'Gesamteinahmen:':<{total_label_width}}{RESET} {ORANGE}{self.format_amount(self.get_total()):>{amt_w}}{RESET}")

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
        # Zeige Kreisdiagramm nur wenn gültige positive Werte vorhanden sind
        if not self.expenses:
            print(f"{RED}No data to plot.{RESET}")
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

        # Nur positive, gültige Beträge verwenden
        filtered = {k: v for k, v in category_totals.items() if v is not None and not math.isnan(v) and v > 0}

        if not filtered:
            print(f"{RED}Keine positiven Beträge zum Darstellen.{RESET}")
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

def clear_screen():
	# plattformunabhängig Bildschirm löschen
	os.system("cls" if os.name == "nt" else "clear")

# kurze Textressource für Deutsch/Englisch
TEXTS = {
	"title": {"de": "Personal Expense Tracker", "en": "Personal Expense Tracker"},
	"opt1": {"de": "Neuen Eintrag hinzufügen", "en": "Add new expense"},
	"opt2": {"de": "Alle Ausgaben anzeigen", "en": "View all expenses"},
	"opt3": {"de": "Nach Kategorie suchen", "en": "Search by category"},
	"opt4": {"de": "Nach Datum suchen", "en": "Search by date"},
	"opt5": {"de": "Sprache wählen (Deutsch / English)", "en": "Choose language (Deutsch / English)"},
	"opt6": {"de": "Beenden", "en": "Exit"},
	"opt7": {"de": "Eintrag löschen", "en": "Delete entry"},
	"choose": {"de": "Wähle eine Option (1-6):", "en": "Choose an option (1-6):"},
	"enter_date": {"de": "Datum eingeben (YYYY-MM-DD):", "en": "Enter date (YYYY-MM-DD):"},
	"invalid_date": {"de": "Ungültiges Datum. Bitte im Format YYYY-MM-DD.", "en": "Invalid date. Use YYYY-MM-DD."},
	"enter_category": {"de": "Kategorie eingeben:", "en": "Enter category:"},
	"enter_description": {"de": "Beschreibung eingeben:", "en": "Enter description:"},
	"enter_amount": {"de": "Betrag eingeben (z.B. 1.234,50 oder 1,50):", "en": "Enter amount (e.g. 1.234,50 or 1.50):"},
	"invalid_amount": {"de": "Ungültiges Betragsformat. Bitte z.B. 1,50 oder 1.234,50 eingeben.", "en": "Invalid amount format. Use e.g. 1.50 or 1,234.50."},
	"saved": {"de": "Eintrag gespeichert.", "en": "Entry saved."},
	"press_enter": {"de": "Drücke Enter, um zum Menü zurückzukehren...", "en": "Press Enter to return to menu..."},
	"goodbye": {"de": "Auf Wiedersehen!", "en": "Goodbye!"},
	"delete_prompt": {"de": "Gebe die Nummer des zu löschenden Eintrags ein:", "en": "Enter the number of the entry to delete:"},
	"admin_pw_prompt": {"de": "Admin-Passwort eingeben:", "en": "Enter admin password:"},
	"pw_wrong": {"de": "Falsches Passwort. Löschvorgang abgebrochen.", "en": "Wrong password. Deletion aborted."},
	"delete_success": {"de": "Eintrag erfolgreich gelöscht.", "en": "Entry deleted successfully."},
	"delete_invalid": {"de": "Ungültige Nummer. Kein Eintrag gelöscht.", "en": "Invalid number. No entry deleted."},
	"login_user": {"de": "Benutzername:", "en": "Username:"},
	"login_pw": {"de": "Passwort:", "en": "Password:"},
	"login_fail": {"de": "Anmeldung fehlgeschlagen. Versuche es erneut.", "en": "Login failed. Try again."},
}

TEXTS.update({
	"select_sign": {"de": "Typ wählen (+ Einnahme / - Ausgabe):", "en": "Choose type (+ income / - expense):"},
	"income_label": {"de": "Einnahme", "en": "Income"},
	"expense_label": {"de": "Ausgabe", "en": "Expense"},
})

def main_menu():
	tracker = ExpenseTracker()
	lang = "de"  # Standard: Deutsch

	while True:
		show_main_menu(lang=lang)
		choice = input(f"{YELLOW}{TEXTS['choose'][lang]} {RESET}").strip()

		if choice == "1":
			try:
				date = input(f"{YELLOW}{TEXTS['enter_date'][lang]} {RESET}").strip()
				datetime.datetime.strptime(date, "%Y-%m-%d")
			except Exception:
				print(f"{RED}{TEXTS['invalid_date'][lang]}{RESET}")
				input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")
				continue
			category = input(f"{YELLOW}{TEXTS['enter_category'][lang]} {RESET}").strip()
			description = input(f"{YELLOW}{TEXTS['enter_description'][lang]} {RESET}").strip()
			amount_input = input(f"{YELLOW}{TEXTS['enter_amount'][lang]} {RESET}").strip()
			try:
				amount = tracker.parse_amount(amount_input)
			except Exception:
				print(f"{RED}{TEXTS['invalid_amount'][lang]}{RESET}")
				input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")
				continue

			# Neu: Typ wählen (+ oder -)
			sign = input(f"{YELLOW}{TEXTS['select_sign'][lang]} {RESET}").strip()
			if sign not in ("+", "-"):
				print(f"{RED}{TEXTS['sign_invalid'][lang]}{RESET}")
				sign = "-"  # Default = Ausgabe
			if sign == "-":
				amount = -abs(amount)
			else:
				amount = abs(amount)

			tracker.add_expense(Expense(date, category, description, amount))
			print(f"{GREEN}{TEXTS['saved'][lang]}{RESET}")
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "2":
			tracker.view_expenses()
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "3":
			category = input(f"{YELLOW}{TEXTS['enter_category'][lang]} {RESET}").strip()
			tracker.search_by_category(category)
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "4":
			date = input(f"{YELLOW}{TEXTS['enter_date'][lang]} {RESET}").strip()
			tracker.search_by_date(date)
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "5":
			# vorher war Sprache, nun zeigt Option 5 die Zusammenfassung
			tracker.plot_summary()
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "6":
			print(f"{GREEN}{TEXTS['goodbye'][lang]}{RESET}")
			break

		elif choice == "7":
			# Löschen: Nummer eingeben, Passwort prüfen, löschen
			num_input = input(f"{YELLOW}{TEXTS['delete_prompt'][lang]} {RESET}").strip()
			if not num_input.isdigit():
				print(f"{RED}{TEXTS['delete_invalid'][lang]}{RESET}")
				input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")
				continue
			num = int(num_input)
			pw = get_password_masked(f"{TEXTS['admin_pw_prompt'][lang]} ")
			if pw != "654321!":
				print(f"{RED}{TEXTS['pw_wrong'][lang]}{RESET}")
				input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")
				continue
			if tracker.delete_entry(num):
				print(f"{GREEN}{TEXTS['delete_success'][lang]}{RESET}")
			else:
				print(f"{RED}{TEXTS['delete_invalid'][lang]}{RESET}")
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		else:
			print(f"{RED}Ungültige Option. Bitte versuche es erneut.{RESET}")
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")


# --- neu: Benutzerverwaltung / Login ---
def load_users(filename: str = "users.csv") -> Dict[str, str]:
	"""
	Lädt eine CSV mit header: username,password
	Gibt dict username -> password zurück.
	Wenn die Datei nicht existiert, wird sie mit einem Beispiel-admin erstellt.
	"""
	if not os.path.exists(filename):
		# Beispiel-Datei anlegen
		with open(filename, "w", newline="", encoding="utf-8") as f:
			f.write("username,password\n")
			f.write("admin,1234\n")
			f.write("user,userpass\n")
	users = {}
	with open(filename, "r", newline="", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		for r in reader:
			u = (r.get("username") or "").strip()
			p = (r.get("password") or "").strip()
			if u:
				users[u] = p
	return users

def show_login_screen(lang: str = "de", attempts: int | None = None):
    """Zeigt eine breitere Login-Box mit Platz für Eingaben."""
    clear_screen()
    title = TEXTS["title"][lang]
    login_user = TEXTS["login_user"][lang]
    login_pw = TEXTS["login_pw"][lang]

    # Box-Inhalt mit mehr Platz für Eingaben
    min_width = 60  # breiter für Eingaben
    lines = []
    lines.append(title)
    if attempts is not None:
        lines.append(f"Versuche verbleibend: {attempts}")
    lines.append("")
    # Platzhalter für Eingaben (werden später überschrieben)
    lines.append(f"{login_user:<20}")  # Platz für Eingabe
    lines.append(f"{login_pw:<20}")    # Platz für Eingabe
    lines.append("")

    # Breite berechnen
    width = max(min_width, max(len(l) for l in lines)) + 8
    border = CYAN + "+" + "-" * width + "+" + RESET

    # Box zeichnen
    print("\n" + border)
    for l in lines:
        print(CYAN + "|" + RESET + " " + l.center(width - 2) + " " + CYAN + "|" + RESET)
    print(border)

def authenticate_user(users: Dict[str, str], max_attempts: int = 3, lang: str = "de") -> str | None:
    """Login mit Eingaben in der Box."""
    for attempt in range(max_attempts, 0, -1):
        show_login_screen(lang=lang, attempts=attempt)

        # Cursor 4 Zeilen hoch bewegen
        sys.stdout.write("\033[4A")
        sys.stdout.flush()

        # Benutzername in der Box
        sys.stdout.write(f"\033[{39}C")  # 39 Spalten nach rechts
        username = input().strip()

        # Eine Zeile runter für Passwort
        sys.stdout.write(f"\033[{35}C")  # 1 Zeile runter, 36 Spalten nach rechts
        sys.stdout.flush()
        password = get_password_masked("")

        # Cursor wieder unter die Box bewegen
        sys.stdout.write("\033[3B")
        sys.stdout.flush()

        expected = users.get(username)
        if expected is not None and password == expected:
            print(f"\n{GREEN}Angemeldet als {username}.{RESET}")
            return username

        print(f"\n{RED}{TEXTS['login_fail'][lang]}{RESET}")
        if attempt - 1 > 0:
            print(f"{YELLOW}Noch {attempt - 1} Versuch(e).{RESET}")
            input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

    return None

def show_main_menu(user: str | None = None, lang: str = "de"):
	"""Zeigt Hauptmenü mit korrektem Rahmen."""
	clear_screen()
	title = TEXTS["title"][lang]
	options = [
		("1", TEXTS["opt1"][lang]),
		("2", TEXTS["opt2"][lang]),
		("3", TEXTS["opt3"][lang]),
		("4", TEXTS["opt4"][lang]),
		("5", TEXTS["opt5"][lang]),
		("6", TEXTS["opt6"][lang]),
		("7", TEXTS["opt7"][lang]),
	]
	
	# Breite für gleichmäßige Box
	width = max(
		len(title),
		len(f"Angemeldet: {user}") if user else 0,
		max(len(f"  {n}. {t}") for n, t in options)
	) + 6  # Padding

	# Box zeichnen mit korrekter Ausrichtung
	border = MAGENTA + "+" + "-" * width + "+" + RESET
	print("\n" + border)
	print(MAGENTA + "|" + RESET + title.center(width) + MAGENTA + "|" + RESET)
	print(MAGENTA + "|" + RESET + "-" * width + MAGENTA + "|" + RESET)

	if user:
		print(MAGENTA + "|" + RESET + f"Angemeldet: {user}".center(width) + MAGENTA + "|" + RESET)
		print(MAGENTA + "|" + RESET + "-" * width + MAGENTA + "|" + RESET)

	# Optionen mit korrekter Ausrichtung
	for n, t in options:
		line = f"  {GREEN}{n}{RESET}. {t}"
		padding = " " * (width - len(line.replace(GREEN, "").replace(RESET, "")))
		print(MAGENTA + "|" + RESET + line + padding + MAGENTA + "|" + RESET)

#print(border)
#print(f"\n{CYAN}Wähle eine Option (1-7):{RESET}")

def main_menu(user: str | None = None):
	tracker = ExpenseTracker()
	lang = "de"

	while True:
		show_main_menu(user=user, lang=lang)
		choice = input(f"{YELLOW}{TEXTS['choose'][lang]} {RESET}").strip()

		if choice == "1":
			# Add entry (bestehende Logik wiederverwenden)
			try:
				date = input(f"{YELLOW}{TEXTS['enter_date'][lang]} {RESET}").strip()
				datetime.datetime.strptime(date, "%Y-%m-%d")
			except Exception:
				print(f"{RED}{TEXTS['invalid_date'][lang]}{RESET}")
				input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")
				continue
			category = input(f"{YELLOW}{TEXTS['enter_category'][lang]} {RESET}").strip()
			description = input(f"{YELLOW}{TEXTS['enter_description'][lang]} {RESET}").strip()
			amount_input = input(f"{YELLOW}{TEXTS['enter_amount'][lang]} {RESET}").strip()
			try:
				amount = tracker.parse_amount(amount_input)
			except Exception:
				print(f"{RED}{TEXTS['invalid_amount'][lang]}{RESET}")
				input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")
				continue

			# Typ wählen (+ oder -)
			sign = input(f"{YELLOW}{TEXTS['select_sign'][lang]} {RESET}").strip()
			if sign not in ("+", "-"):
				print(f"{RED}{TEXTS['sign_invalid'][lang]}{RESET}")
				sign = "-"  # Default = Ausgabe
			if sign == "-":
				amount = -abs(amount)
			else:
				amount = abs(amount)

			tracker.add_expense(Expense(date, category, description, amount))
			print(f"{GREEN}{TEXTS['saved'][lang]}{RESET}")
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "2":
			tracker.view_expenses()
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "3":
			category = input(f"{YELLOW}{TEXTS['enter_category'][lang]} {RESET}").strip()
			tracker.search_by_category(category)
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "4":
			date = input(f"{YELLOW}{TEXTS['enter_date'][lang]} {RESET}").strip()
			tracker.search_by_date(date)
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "5":
			tracker.plot_summary()
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		elif choice == "6":
			print(f"{GREEN}{TEXTS['goodbye'][lang]}{RESET}")
			break

		elif choice == "7":
			num_input = input(f"{YELLOW}{TEXTS['delete_prompt'][lang]} {RESET}").strip()
			if not num_input.isdigit():
				print(f"{RED}{TEXTS['delete_invalid'][lang]}{RESET}")
				input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")
				continue
			num = int(num_input)
			pw = get_password_masked(f"{TEXTS['admin_pw_prompt'][lang]} ")
			if pw != "654321!":
				print(f"{RED}{TEXTS['pw_wrong'][lang]}{RESET}")
				input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")
				continue
			if tracker.delete_entry(num):
				print(f"{GREEN}{TEXTS['delete_success'][lang]}{RESET}")
			else:
				print(f"{RED}{TEXTS['delete_invalid'][lang]}{RESET}")
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")

		else:
			print(f"{RED}Ungültige Option. Bitte versuche es erneut.{RESET}")
			input(f"{YELLOW}{TEXTS['press_enter'][lang]}{RESET}")


# get_password_masked: maskiertes Passwort-Eingabe mit '*' (Windows und Unix)
try:
	import msvcrt

	def get_password_masked(prompt: str = "") -> str:
		sys.stdout.write(prompt)
		sys.stdout.flush()
		pw_chars = []
		while True:
			ch = msvcrt.getwch()
			if ch in ("\r", "\n"):
				print()
				break
			if ch == "\x03":
				raise KeyboardInterrupt
			if ch == "\x08":  # Backspace
				if pw_chars:
					pw_chars.pop()
					sys.stdout.write("\b \b")
					sys.stdout.flush()
			else:
				pw_chars.append(ch)
				sys.stdout.write("*")
				sys.stdout.flush()
		return "".join(pw_chars)

except ImportError:
	import tty
	import termios

	def get_password_masked(prompt: str = "") -> str:
		sys.stdout.write(prompt)
		sys.stdout.flush()
		fd = sys.stdin.fileno()
		old = termios.tcgetattr(fd)
		pw_chars = []
		try:
			tty.setraw(fd)
			while True:
				ch = sys.stdin.read(1)
				if ch in ("\r", "\n"):
					sys.stdout.write("\n")
					break
				if ch == "\x03":
					raise KeyboardInterrupt
				if ch in ("\x7f", "\b"):  # Backspace/Delete
					if pw_chars:
						pw_chars.pop()
						sys.stdout.write("\b \b")
						sys.stdout.flush()
				else:
					pw_chars.append(ch)
					sys.stdout.write("*")
					sys.stdout.flush()
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old)
		return "".join(pw_chars)


# =============================
# Entry Point
# =============================

if __name__ == "__main__":
	# Benutzer laden und Login ausführen (Sprache standard 'de')
	users = load_users(os.path.join(os.path.dirname(__file__), "users.csv"))
	# Standard-Sprache Deutsch für Login-Meldungen
	lang0 = "de"
	user = authenticate_user(users, max_attempts=3, lang=lang0)
	if not user:
		print(f"{RED}Anmeldung fehlgeschlagen. Programm wird beendet.{RESET}")
	else:
		# Bei erfolgreichem Login das Hauptmenü starten
		main_menu()
