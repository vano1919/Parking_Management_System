import os
import re
import sys
import subprocess
import sqlite3
import shutil
import webbrowser
import requests
from datetime import datetime, timedelta
from zipfile import ZipFile
import pyautogui
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from PySide6.QtCore import Qt
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QLabel, QLineEdit, \
	QMessageBox, QPushButton, QVBoxLayout, QWidget, QCompleter


pyautogui.FAILSAFE = False
"""
This Python script is the main application logic and user interface for a parking system. 

The script starts with importing necessary modules such as os, re, sys, subprocess, sqlite3, shutil, webbrowser, requests, datetime, timedelta, and zipfile from Python's standard library. It also imports several classes from PyQt5 and PySide6 for creating the graphical user interface.

The script defines several classes:

1. EnterMoveQLineEdit: A custom QLineEdit that overrides the keyPressEvent method to switch focus to the next child widget when the Enter or Return key is pressed.

2. CarEntryDialog: A dialog for entering and validating car details such as brand, model, and VIN code. It supports autocomplete for car brands and models.

3. ParkingSpot: Represents a parking spot in the UI. It can toggle between available and occupied states. It also has methods for adding a car, confirming car removal, printing car details, showing warnings, exiting a car, refreshing the spot status, and getting today's earnings.

4. CustomButton: A custom QPushButton with a fixed size and specific stylesheet.

5. MainApplication: The main application widget for the parking system. It initializes the database, sets up the UI, confirms exit, and retrieves today's total earnings from the database.

The script ends with a main function that serves as the entry point of the application. It initializes and starts the PyQt application.
"""


# This file contains the main application logic and user interface for the parking system.
class EnterMoveQLineEdit(QLineEdit):
	"""Custom QLineEdit that overrides the keyPressEvent method to switch focus to the next child widget when the Enter or Return key is pressed."""

	def __init__(self, parent=None):
		super().__init__(parent)

	def keyPressEvent(self, event):

		if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
			self.focusNextChild()
		else:
			super().keyPressEvent(event)


class CarEntryDialog(QDialog):
	"""Dialog for entering and validating car details such as brand, model, and VIN code. It supports autocomplete for car brands and models."""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setWindowTitle("ავტომობილის სადგომზე დამატება")
		self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;  /* Dark background */
                font-family: 'Arial';
                font-size: 14px;
                color: white;  /* White text color */
            }
            QLineEdit {
                border: 2px solid #555;  /* Darker border for line edits */
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 10px;
                font-size: 16px;
                background-color: #333;  /* Darker background for line edits */
                color: white;  /* White text color */
            }
            QLabel {
                font-size: 16px;
                margin-bottom: 5px;
                color: white;  /* White text color */
            }
            QDialogButtonBox {
                margin-top: 15px;
            }
            QPushButton {
                border: 1px solid #555;  /* Darker border for buttons */
                border-radius: 6px;
                background-color: #333;  /* Darker background for buttons */
                min-width: 100px;
                font-size: 14px;
                padding: 5px;
                color: white;  /* White text color */
            }
            QPushButton:hover {
                background-color: #555;  /* Slightly lighter background for buttons on hover */
            }
            QPushButton:pressed {
                background-color: #777;  /* Even lighter background for buttons when pressed */
            }
        """)

		main_layout = QVBoxLayout(self)

		car_details_layout = QFormLayout()
		self.ავტომობილის_მარკა_entry = EnterMoveQLineEdit()
		self.ავტომობილის_მოდელი_entry = EnterMoveQLineEdit()
		self.vin_კოდი_entry = EnterMoveQLineEdit()
		car_details_layout.addRow("მარკა:", self.ავტომობილის_მარკა_entry)
		car_details_layout.addRow("მოდელი:", self.ავტომობილის_მოდელი_entry)
		car_details_layout.addRow("VIN კოდი:", self.vin_კოდი_entry)
		main_layout.addLayout(car_details_layout)

		def load_car_dict_from_file(filename):
			car_dict = {}
			with open(filename, 'r') as file:
				for line in file:
					parts = line.strip().split(':')
					if len(parts) == 2:
						brand, models_str = parts
						models = models_str.split(',')
						car_dict[brand] = models
			return car_dict

		filename = 'car_brands_and_models.txt'  # Ensure this file exists in the correct directory
		self.car_dict = load_car_dict_from_file(filename)

		# Completer for car makes
		self.make_completer = QCompleter(list(self.car_dict.keys()))
		self.make_completer.setCaseSensitivity(Qt.CaseInsensitive)
		self.make_completer.setCompletionMode(QCompleter.PopupCompletion)
		self.ავტომობილის_მარკა_entry.setCompleter(self.make_completer)

		# Completer for car models, initially empty
		self.model_completer = QCompleter()
		self.model_completer.setCaseSensitivity(Qt.CaseInsensitive)
		self.model_completer.setCompletionMode(QCompleter.PopupCompletion)
		self.ავტომობილის_მოდელი_entry.setCompleter(self.model_completer)

		# Connect ავტომობილის_მარკა_entry text changed signal to update model completer
		self.ავტომობილის_მარკა_entry.textChanged.connect(self.update_model_completer)

		owner_details_layout = QGridLayout()

		self.სახელი_entry = EnterMoveQLineEdit()
		self.გვარი_entry = EnterMoveQLineEdit()
		self.პირადი_ნომერი_entry = EnterMoveQLineEdit()
		self.ტელეფონის_ნომერი_entry = EnterMoveQLineEdit()  # Phone number field

		self.ინდივიდუალური_გადასახადი_entry = EnterMoveQLineEdit()
		self.ინდივიდუალური_გადასახადი_entry.setText("5")  # Set a default fee or leave blank for user input

		owner_details_layout.addWidget(QLabel("მფლობელის სახელი:"), 0, 0)
		owner_details_layout.addWidget(self.სახელი_entry, 0, 1)
		owner_details_layout.addWidget(QLabel("მფლობელის გვარი:"), 0, 2)
		owner_details_layout.addWidget(self.გვარი_entry, 0, 3)
		owner_details_layout.addWidget(QLabel("მფლობელის ID ნომერი:"), 1, 0)
		owner_details_layout.addWidget(self.პირადი_ნომერი_entry, 1, 1)
		owner_details_layout.addWidget(QLabel("მობილურის ნომერი:"), 1, 2)
		owner_details_layout.addWidget(self.ტელეფონის_ნომერი_entry, 1, 3)

		car_details_layout.addRow("პარკინგის ტარიფი:",
		                          self.ინდივიდუალური_გადასახადი_entry)
		main_layout.addLayout(owner_details_layout)

		buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttons.accepted.connect(self.validate_and_accept)
		buttons.rejected.connect(self.reject)
		main_layout.addWidget(buttons)

		self.setFixedSize(800, 450)

	def update_model_completer(self, text):
		"""Updates the car model completer based on the selected car brand."""
		make = text.strip().title()
		if make in self.car_dict:
			models = self.car_dict[make]
			model = QStandardItemModel()
			for model_name in models:
				item = QStandardItem(model_name)
				model.appendRow(item)
			self.model_completer.setModel(model)
		else:
			self.model_completer.setModel(QStandardItemModel())  # Clear the model if the make is not found

	def move_cursor_to_model(self, index):
		"""Sets the focus to the car model entry field."""
		self.ავტომობილის_მოდელი_entry.setFocus()

	def move_cursor_to_vin(self, index):
		"""Sets the focus to the VIN code entry field."""
		self.vin_კოდი_entry.setFocus()

	def validate_and_accept(self):
		"""Validates car details and closes the dialog if validation is successful."""
		ავტომობილის_მარკა = self.ავტომობილის_მარკა_entry.text().strip().title()
		ავტომობილის_მოდელი = self.ავტომობილის_მოდელი_entry.text().strip()
		vin_კოდი = self.vin_კოდი_entry.text().strip().upper()

		try:
			parking_fee = int(self.ინდივიდუალური_გადასახადი_entry.text())
			if parking_fee <= 0:
				raise ValueError  # Ensure the fee is positive
		except ValueError:
			self.show_warning("გთხოვთ, შეიყვანეთ სწორი დაფასება (მხოლოდ დადებითი ციფრები).")
			return
		if not ავტომობილის_მარკა or not ავტომობილის_მოდელი or not vin_კოდი:
			self.show_warning("გთხოვთ შეავსოთ ყველა ველი.")
			return

		vin_regex = re.compile(
			r'^[A-HJ-NPR-Za-hj-npr-z\d]{8}[\dX][A-HJ-NPR-Za-hj-npr-zm\d]{2}\d{6}$')
		# Basic VIN format validation
		if not vin_regex.match(vin_კოდი):
			confirm_vin_dialog = self.show_confirm(f"{vin_კოდი} სწორია?")
			if confirm_vin_dialog == QMessageBox.Yes:
				if not self.vin_code_exists_in_current(vin_კოდი):
					self.accept()


				else:
					self.show_warning("ავტომობილი ამ VIN კოდით უკვე დამატებულია.")
		else:
			self.accept()

	def show_warning(self, message):
		"""Displays a warning message dialog."""
		QMessageBox.warning(self, "გაფრთხილება", message)

	def show_confirm(self, message):
		"""Displays a confirmation dialog and returns the user's choice."""
		return QMessageBox.question(self, "დაადასტურე", message, QMessageBox.Yes | QMessageBox.No)

	def vin_code_exists_in_current(self, vin_კოდი):
          """Checks if the given VIN code already exists in the database."""
          with sqlite3.connect('parking_system.db') as conn:
               cursor = conn.cursor()
               cursor.execute("SELECT COUNT(*) FROM parking WHERE vin_კოდი = ?", (vin_კოდი,))
               count = cursor.fetchone()[0]
          return count > 0

	def get_result(self):
		"""Retrieves the input car details from the form."""
		return (self.ავტომობილის_მარკა_entry.text().strip().title(),
		        self.ავტომობილის_მოდელი_entry.text().strip(),
		        self.vin_კოდი_entry.text().strip().upper(),
		        self.სახელი_entry.text().strip(),  # Ensure this is correctly capturing input
		        self.გვარი_entry.text().strip(),  # Ensure this is correctly capturing input
		        self.პირადი_ნომერი_entry.text().strip(),  # Ensure this is correctly capturing input
		        self.ტელეფონის_ნომერი_entry.text().strip())  # Ensure this is correctly capturing input


class ParkingSpot(QtWidgets.QPushButton):
	"""Represents a parking spot in the UI. It can toggle between available and occupied states."""


	def __init__(self, id, parent=None):
		super().__init__(parent)
		self.სახელი = None
		self.გვარი = None
		self.პირადი_ნომერი = None
		self.ტელეფონის_ნომერი = None
		self.id = id
		self.db_conn = sqlite3.connect('parking_system.db')
		self.db_conn_history = sqlite3.connect('parking_history.db')
		self.is_occupied = False
		self.ავტომობილის_მარკა = None
		self.ავტომობილის_მოდელი = None
		self.vin_კოდი = None
		self.ჯამში_გადახდილი = None
		self.setText(f'ადგილი {self.id}')
		self.setStyleSheet("background-color: green; color: white; font-weight: bold; font-size: 14px;")
		self.setMinimumHeight(50)
		self.setMinimumWidth(100)
		self.clicked.connect(self.toggle)
		self.refresh_spot_status()

	def toggle(self):
		"""Toggles the parking spot's occupancy state."""
		if not self.is_occupied:
			self.add_car()
		else:
			self.confirm_remove_car()

	def add_car(self):
		"""Displays a dialog for entering a new car into the parking spot."""


		def backup_database(db_name, backup_dir):
			"""
			Backs up the specified SQLite database to the backup directory.
			The backup file is named with the current date for easy identification.
			"""
			date_str = datetime.now().strftime("%Y-%m-%d-%H")  # Format the current date and time
			backup_file = os.path.join(backup_dir, f"{db_name}_{date_str}.db")
			try:
				# Make sure the backup directory exists
				os.makedirs(backup_dir, exist_ok=True)
				shutil.copy(f"{db_name}.db", backup_file)

				# Remove backups older than 5 days
				for file in os.listdir(backup_dir):
					file_path = os.path.join(backup_dir, file)

					if file.startswith(db_name) and file.endswith(".db"):

						file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

						if datetime.now() - file_time > timedelta(days=5):
							os.remove(file_path)
							print(f"Removed old backup: {file}")


			except Exception as e:
				print(f"An error occurred while backing up {db_name}.db: {e}")

		dialog = CarEntryDialog()
		if dialog.exec():
			# Get the results from the dialog
			ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი = dialog.get_result()
			ინდივიდუალური_გადასახადი = float(
				dialog.ინდივიდუალური_გადასახადი_entry.text())  # Get individual fee from the dialog

			# Insert into the database with ინდივიდუალური_გადასახადი
			try:
				self.db_conn.execute(
					'INSERT INTO parking (ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა, პარკინგის_ადგილი, ინდივიდუალური_გადასახადი) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
					(ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი,
					 ტელეფონის_ნომერი,
					 datetime.now().strftime("%Y-%m-%d"),
					 self.id, ინდივიდუალური_გადასახადი)
				)
				self.db_conn.commit()
				self.print_car_details(self.id, status="entry_check")

				script_dir = os.path.dirname(os.path.abspath(__file__))
				backup_database('parking_system', os.path.join(script_dir, 'backups'))
				backup_database('parking_history', os.path.join(script_dir, 'backups'))

			except sqlite3.Error as e:
				print("An error occurred:", e)

			self.refresh_spot_status()

	def confirm_remove_car(self):
		"""Initiates the car removal process from the parking spot."""
		entry_info = self.db_conn.execute(
			'SELECT ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა, პარკინგის_ადგილი, ინდივიდუალური_გადასახადი FROM parking WHERE პარკინგის_ადგილი = ? AND გამოსვლა IS NULL',
			(self.id,)).fetchone()

		# Check if car information is not found or already checked out
		if entry_info is None:
			self.show_warning("მანქანა უკვე გამოსულია.")
			return

		# Extract car details
		ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა_str, პარკინგის_ადგილი, ინდივიდუალური_გადასახადი = entry_info

		# Convert entry and exit timestamps to dates
		entry_date = datetime.strptime(შესვლა_str, "%Y-%m-%d").date()
		exit_date = datetime.now().date()  # This removes the time part, keeping only the date

		ინდივიდუალური_გადასახადი = entry_info[-1]  # Assuming it's the last in the fetched data
		total_days = (exit_date - entry_date).days + 1
		self.ჯამში_გადახდილი = total_days * ინდივიდუალური_გადასახადი

		payment_info = f"""<html>
        <head>
            <style>
                body {{
                    font-family: 'Times New Roman', Times, serif; /* Applying Roman-style font */
                }}
                .label {{
                    font-weight: 600;
                    display: inline-block;
                    width: 150px; /* Adjust width as needed */
                }}
                .value {{
                    display: inline-block;
                    text-align: left;
                    width: 200px; /* Adjust width as needed, ensures consistent text length */
                }}
                .total-payment {{
                    font-size: 24px;
                    color: #4A90E2;
                    font-weight: 700; /* Emphasizes total payment */
                }}
            </style>
        </head>
        <body>
            <p><span class="label">ავტომობილი:</span> <span class="value">{ავტომობილის_მარკა} {ავტომობილის_მოდელი}</span></p>
            <p><span class="label">VIN კოდი:</span> <span class="value">{vin_კოდი}</span></p>
            <p><span class="label">მფლობელი:</span> <span class="value">{სახელი} {გვარი} ({პირადი_ნომერი})</span></p>
            <p><span class="label">ტელ:</span> <span class="value">{ტელეფონის_ნომერი}</span></p>
            <p><span class="label">ავტომობილი სადგომზე იმყოფებოდა:</span> <span class="value">{total_days} დღე</span></p>
            <p style="margin-top:20px;"><span class="font-size:18px; font-weight:700;">სულ:</span> <span class="total-payment">{self.ჯამში_გადახდილი} ლარი</span></p>
        </body>
        </html>"""

		dialog = QDialog(self)

		dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
		dialog.setFixedSize(500, 500)
		dialog.setStyleSheet("""
            QDialog {
    background-color: #1e1e1e;  /* Dark background */
    font-family: 'Arial';
    font-size: 14px;
    color: white;  /* White text color */
}

QLabel {
    font-size: 16px;
    margin-bottom: 5px;
    color: white;  /* White text color */
}

QLineEdit {
    border: 2px solid #555;  /* Darker border for line edits */
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
    font-size: 16px;
    background-color: #333;  /* Darker background for line edits */
    color: white;  /* White text color */
}

QPushButton {
    border: 1px solid #555;  /* Darker border for buttons */
    border-radius: 6px;
    background-color: #333;  /* Darker background for buttons */
    min-width: 100px;
    font-size: 14px;
    padding: 5px;
    color: white;  /* White text color */
}

QPushButton:hover {
    background-color: #555;  /* Slightly lighter background for buttons on hover */
}

QPushButton:pressed {
    background-color: #777;  /* Even lighter background for buttons when pressed */
}

        """)

		layout = QVBoxLayout()
		info_widget = QWidget()
		info_widget_layout = QVBoxLayout(info_widget)
		info_widget_layout.setAlignment(Qt.AlignCenter)  # Center the information

		# Set the style for the information container
		info_widget.setStyleSheet("""
            background-color: #1e1e1e;  /* Dark background */
            border-radius: 15px; /* Rounded corners */
            padding: 20px;
            color: white; /* White text */
        """)

		info_label = QLabel(payment_info)
		info_label.setAlignment(Qt.AlignCenter)  # Center align the text within the label
		info_label.setStyleSheet("""
            font-size: 16px; /* Adjusted text size for clarity */
            color: white; /* Black text for readability against the light background */
        """)
		info_widget_layout.addWidget(info_label)
		layout.addWidget(info_widget)

		finish_button = QPushButton("პარკინგის დასრულება")
		finish_button.setStyleSheet("""
            background-color: #004225; /* Consistent blue color for action buttons */
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 5px;
            margin-top: 20px;
        """)
		finish_button.clicked.connect(lambda: self.user_confirmed_exit(dialog, self.confirm_exit_with_password()))
		layout.addWidget(finish_button)

		cancel_button = QPushButton("გაუქმება")
		cancel_button.setStyleSheet("""
            background-color: #D22F2F; /* Grey color for cancel button */
            color: white; /* Dark grey text */
            font-weight: bold;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 5px;
            margin-top: 10px;
        """)
		cancel_button.clicked.connect(lambda: self.user_confirmed_exit(dialog, False))
		layout.addWidget(cancel_button)

		dialog.setLayout(layout)
		dialog.exec()
		self.refresh_spot_status()


	# Call this method instead of directly exiting

	def user_confirmed_exit(self, dialog, confirmed):
		"""Finalizes car removal if the user confirms."""
		dialog.close()
		if confirmed:
			self.exit_car()  # Call the exit operation

	def confirm_exit_with_password(self):
		"""Displays a dialog to confirm exit with a password."""
		dialog = QDialog(self)
		dialog.setWindowTitle("პაროლის შეყვანა")
		dialog.setFixedSize(300, 200)

		dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
		dialog.setAttribute(Qt.WA_TranslucentBackground)  # Make the background transparent
		dialog.setModal(True)

		layout = QVBoxLayout(dialog)

		# Set dialog stylesheet for dark mode
		dialog.setStyleSheet("""
            QDialog {
                background-color: #333; /* Dark background */
                color: white; /* White text */
                border-radius: 10px; /* Rounded corners */
            }
            QLabel {
                color: white; /* White text for labels */
                background-color: none; /* No specific background */
                border: none; /* No border */
            }
            QLineEdit {
                border: 2px solid #555; /* Border for line edits */
                border-radius: 5px;
                padding: 5px;
                color: white; /* White text */
                background-color: #222; /* Darker background for line edits */
            }
            QPushButton {
                border: 2px solid #555; /* Border for buttons */
                border-radius: 5px;
                padding: 5px;
                color: white; /* White text */
                background-color: #555; /* Darker background for buttons */
            }
            QPushButton:hover {
                background-color: #777; /* Lighter background on hover */
            }
            QPushButton:pressed {
                background-color: #888; /* Even lighter background for buttons when pressed */
            }
        """)

		label = QLabel("პაროლის შეყვანა:")
		layout.addWidget(label)

		password_entry = QLineEdit()
		password_entry.setEchoMode(QLineEdit.Password)
		layout.addWidget(password_entry)

		button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		layout.addWidget(button_box)

		button_box.accepted.connect(lambda: self.check_password_and_exit(password_entry.text(), dialog))
		button_box.rejected.connect(dialog.reject)

		dialog.exec()

	def check_password_and_exit(self, entered_password, dialog):
		"""Checks if the entered password is correct and proceeds with the exit."""
		# Read the correct password from the file
		with open('credentials.txt', 'r') as file:
			credentials = {}
			for line in file:
				key, value = line.strip().split(': ')
				credentials[key] = value.strip()  # Ensure to strip value

		# Check if the entered password is correct
		if entered_password == credentials.get('password', ''):

			self.exit_car()
			dialog.accept()
			self.print_car_details(self.id, status="exit_check")
		# Assuming self.id contains the პარკინგის_ადგილი

		else:
			msg_box = QMessageBox()
			msg_box.setIcon(QMessageBox.Warning)
			msg_box.setWindowTitle("პაროლი არასწორია")
			msg_box.setText("პაროლი არასწორია")

			msg_box.setGeometry(1, 0, 400, 200)

			msg_box.exec()

	def print_car_details(self, parking_spot, status):
		"""Prints a ticket with car details for entry or exit."""

		def add_text(canvas, text, x, y, font, size):
			canvas.setFont(font, size)
			canvas.drawString(x, y, text)

		def add_multiline_text(canvas, text, x, y, font, size, line_height):
			canvas.setFont(font, size)
			lines = text.split('\n')
			for i, line in enumerate(lines):
				canvas.drawString(x, y - i * line_height, line)

		def add_dashed_line(canvas, x, y, length):
			canvas.setDash(3, 5)  # Pattern: 3 points on, 5 points off
			canvas.line(x, y, x + length, y)
			canvas.setDash([])  # Resetting to solid line

		def add_logo(canvas, logo_path, x, y, width, height):
			"""Adds a logo image to the canvas."""
			canvas.drawImage(logo_path, x, y, width, height)




		universal_font_name = 'DejaVuSerif'
		universal_font_filename = 'DejaVuSerif.ttf'
		universal_font_path = os.path.join("fonts", universal_font_filename)
		pdfmetrics.registerFont(TTFont(universal_font_name, f"fonts/{universal_font_filename}"))

		# Determine the size of the ticket based on the status
		if status in ["entry_check", "exit_check"]:
			check_width, check_height = 3.5 * 72, 8 * 72

		margin = 72 * 0.5
		line_height = 16
		logo_path_1 = 'logos/logo_1.png.png'
		logo_path_2 = 'logos/logo_2.png.png'
		logo_width, logo_height = 200, 100  # Replace with actual logo dimensions

		pdf_filename = "car_details.pdf"
		c = canvas.Canvas(pdf_filename, pagesize=(check_width, check_height))
		c.setTitle("Parking Check")

		# Add the logo to the ticket
		add_logo(c, logo_path_1, (check_width - 250) / 2, check_height - (200 - margin) * 1.2, 250,
		         200)
		add_logo(c, logo_path_2, (check_width - logo_width) / 2, check_height - (logo_height - margin) * 8.2,
		         logo_width,
		         logo_height)
		# Database connection
		conn = sqlite3.connect('parking_system.db')
		cursor = conn.cursor()

		# Selecting data from the database based on the status
		sql_query = "SELECT ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, შესვლა, ინდივიდუალური_გადასახადი FROM parking WHERE პარკინგის_ადგილი = ?"

		cursor.execute(sql_query, (parking_spot,))
		record = cursor.fetchone()
		if status == "exit_check":
			# Update the exit timestamp
			შესვლა = datetime.strptime(record[-2], "%Y-%m-%d")
			გამოსვლა = datetime.now()
			total_days = (გამოსვლა.date() - შესვლა.date()).days + 1  # Including the current day
			ჯამში_გადახდილი = total_days * record[-1]
			record = list(record)
			record[-1] = გამოსვლა.strftime("%Y-%m-%d")
			record.append(ჯამში_გადახდილი)

		if status == "entry_check":
			record = list(record)
			record.append(parking_spot)




		cursor.close()

		# Print car details from the record
		if record:
			headings = ["მარკა", "მოდელი", "VIN კოდი", "სახელი", "გვარი", "პირადი N", "შესვლა",
			            "გამოსვლა", "ჯამში_გადახდილი"] if status == "exit_check" else ["მარკა", "მოდელი",
			                                                                           "VIN კოდი", "სახელი", "გვარი",
			                                                                           "პირადი N", "შესვლა",
			                                                                           "დღეში გადასახდელი","ადგილი"]
			for i, (heading, value) in enumerate(zip(headings, record)):

				if heading == "ადგილი":
					spot_id_possition = (check_height - margin - len(
						headings) * line_height * 2 - line_height) / 1.5
					add_multiline_text(c, f"საპარკინგე ადგილი N: {value}", margin, spot_id_possition,
					                   universal_font_name, 14, line_height)
				else:
					if heading != "ჯამში_გადახდილი":
						text = f"{heading}: {value}"
						strLen = len(f"{heading}: {value}")
						if strLen < 27:
							text = f"{heading}:{'_' * (27 - strLen)} {value}"

						add_multiline_text(c,
						                   text
						                   , margin, (check_height - margin - i * line_height * 2) / 1.5,
						                   universal_font_name,
						                   12,
						                   line_height)
					else:
						total_paid_y_position = (check_height - margin - len(
							headings) * line_height * 2 - line_height) / 1.5
						add_multiline_text(c, f"გადასახდელი თანხა: {value}", margin, total_paid_y_position,
						                   universal_font_name, 14, line_height)

		# Add footer and dashed lines for aesthetics
		add_dashed_line(c, margin, 30, check_width - 2 * margin)  # Adjust Y position as needed
		add_multiline_text(c, "მადლობა ვიზიტისთვის!", margin, 10, universal_font_name, 13, 18)

		# Finalize PDF and close the database connection
		conn.close()
		c.save()
		absolute_path = os.path.abspath(pdf_filename)
		webbrowser.open(f'file://{absolute_path}')
		time.sleep(2)
		pyautogui.hotkey('ctrl', 'p')

		if status == "exit_check":
			cursor = self.db_conn.cursor()

			cursor.execute("DELETE FROM parking WHERE პარკინგის_ადგილი = ?", (self.id,))

			self.db_conn.commit()

			cursor.close()

		self.refresh_spot_status()

	def show_warning(self, message):
		"""Displays a warning message dialog."""
		# Create a separate method for showing warnings if you don't have it already
		warning_dialog = QDialog(self)
		warning_dialog.setWindowTitle("გაფრთხილება")
		warning_dialog.setFixedSize(400, 200)
		warning_dialog.setStyleSheet("background-color: #2b2b2b; color: white;")
		layout = QVBoxLayout()
		label = QLabel(message)
		label.setStyleSheet("font-size: 16px;")
		layout.addWidget(label)
		ok_button = QPushButton("OK")
		ok_button.clicked.connect(warning_dialog.close)
		layout.addWidget(ok_button)
		warning_dialog.setLayout(layout)
		warning_dialog.exec()

	def exit_car(self):
		"""Processes the car's exit from the parking spot and updates the database."""
		with sqlite3.connect('parking_system.db') as conn:
			entry_info = conn.execute(
				'SELECT შესვლა, ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, ინდივიდუალური_გადასახადი FROM parking WHERE პარკინგის_ადგილი = ? AND გამოსვლა IS NULL',
				(self.id,)).fetchone()

			if entry_info is None:
				self.show_warning("ავტომობილი უკვე გამოსულია სადგომიდან.")  # Car has already exited
				return

			შესვლა_str, ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, ინდივიდუალური_გადასახადი = entry_info
			შესვლა = datetime.strptime(შესვლა_str, "%Y-%m-%d")
			გამოსვლა = datetime.now()
			total_days = (გამოსვლა.date() - შესვლა.date()).days + 1  # Including the current day
			ჯამში_გადახდილი = total_days * ინდივიდუალური_გადასახადი


			conn.execute(
				'UPDATE parking SET გამოსვლა = ?, ჯამში_გადახდილი = ? WHERE პარკინგის_ადგილი = ? AND გამოსვლა IS NULL',
				(გამოსვლა.strftime("%Y-%m-%d"), ჯამში_გადახდილი, self.id))
			conn.commit()

		with sqlite3.connect('parking_history.db') as conn_history:
			conn_history.execute(
				'INSERT INTO parking_history (ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა, გამოსვლა, ჯამში_გადახდილი,პარკინგის_ადგილი) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
				(
					ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი,
					ტელეფონის_ნომერი,
					შესვლა_str,
					გამოსვლა.strftime("%Y-%m-%d"), ჯამში_გადახდილი, self.id), )




		self.is_occupied = False
		self.setStyleSheet("background-color: green; color: white; font-weight: bold; font-size: 14px;")
		self.setText(f'ადგილი {self.id}')
		self.refresh_spot_status()





	def refresh_spot_status(self):
		"""Refreshes the parking spot's status (occupied/available)."""
		with sqlite3.connect('parking_system.db') as conn:
			cursor = conn.cursor()
			car_info = cursor.execute(
				'SELECT ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი FROM parking WHERE პარკინგის_ადგილი = ? AND გამოსვლა IS NULL',
				(self.id,)
			).fetchone()
		if car_info:
			self.is_occupied = True
			self.ავტომობილის_მარკა, self.ავტომობილის_მოდელი, self.vin_კოდი = car_info
			# Updated styles for occupied spots
			self.setStyleSheet("""
                    background-color: #D22F2F; /* Darker red for occupied spot */
				color: #white;
				font-weight: 300; /* Extra bold font */
				font-size: 20px; /* Increased font size for better visibility */
				padding: 20px; /* Add more padding for a larger button */
				border-top-left-radius: 30px; /* Rounded top-left corner */
				min-height: 40px; /* Minimum button height */
				min-width: 40px; /* Minimum button width */

            """)
			self.setText(f'ადგილი {self.id}')
		else:
			self.is_occupied = False

			# Updated styles for unoccupied spots
			self.setStyleSheet("""
                    background-color: #004225; /* Darker green for available spot */
                    color: #cccccc;
                    font-weight: 300; /* Extra bold font */
                    font-size: 20px; /* Consistent increased font size */
                    padding: 20px; /* Consistent padding with occupied spots */
                    border-top-left-radius: 30px; /* Rounded top-left corner */
                    min-height: 40px; /* Consistent minimum button height */
                    min-width: 40px; /* Consistent minimum button width */
            """)
			self.setText(f'ადგილი {self.id}')



class CustomButton(QtWidgets.QPushButton):
	class CustomButton(QtWidgets.QPushButton):
		def __init__(self, text, parent=None):
			super().__init__(text, parent)
			self.setFixedSize(90, 30)  # Set fixed size for small buttons
			self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #ff0000; /* Set text color to dark red */
                }
                QPushButton:hover {
                    color: #ff5555; /* Lighter red color on hover */
                }
            """)


class MainApplication(QtWidgets.QWidget):
	"""Main application widget for the parking system."""

	@staticmethod
	def read_credentials():
		"""Reads and returns the application's credentials from a file."""
		global global_password
		# Set default values using the global variable
		credentials = {'number_of_spaces': 64, 'password': 1237}
		try:
			with open('credentials.txt', 'r') as file:
				for line in file:
					key, value = line.strip().split(': ')
					credentials[key] = value.strip()
		except FileNotFoundError:
			print("credentials.txt file not found, using default values.")
		except ValueError:
			print("Error processing credentials.txt, ensure it is formatted correctly.")

		# Update global password based on file or keep default
		global_password = credentials['password']

		return credentials

	@staticmethod
	def init_db():
		"""Initializes the database for the parking system."""
		conn = sqlite3.connect('parking_system.db')
		cursor = conn.cursor()
		cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ავტომობილის_მარკა TEXT,
                ავტომობილის_მოდელი TEXT,
                vin_კოდი TEXT,
                სახელი TEXT,
                გვარი TEXT,
                პირადი_ნომერი TEXT,
                ტელეფონის_ნომერი TEXT,
                შესვლა TEXT,
                გამოსვლა TEXT,
                ჯამში_გადახდილი REAL,
                პარკინგის_ადგილი INTEGER,
                ინდივიდუალური_გადასახადი REAL  -- New column for individual parking fee
            );
        ''')
		conn.commit()
		conn.close()

		conn_history = sqlite3.connect('parking_history.db')
		cursor_history = conn_history.cursor()
		cursor_history.execute('''
            CREATE TABLE IF NOT EXISTS parking_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ავტომობილის_მარკა TEXT,
                ავტომობილის_მოდელი TEXT,
                vin_კოდი TEXT,
                სახელი TEXT,
                გვარი TEXT,
                პირადი_ნომერი TEXT,
                ტელეფონის_ნომერი TEXT,
                შესვლა TEXT,
                გამოსვლა TEXT,
                ჯამში_გადახდილი REAL,
                ინდივიდუალური_გადასახადი REAL,  -- New column for individual parking fee
                პარკინგის_ადგილი INTEGER
            );
        ''')
		conn_history.commit()
		conn_history.close()

	def __init__(self):
		super().__init__()
		credentials = MainApplication.read_credentials()  # Read credentials from file # Use the password from credentials

		MainApplication.init_db()
		self.init_ui()

	def init_ui(self):
		"""Initializes the UI components of the application."""

		self.setWindowTitle("Parking System")
		self.setStyleSheet("""
	        QWidget {
	            background-color: #1e1e1e;
	            color: #ffffff;
	        }
	        QLabel {
	            color: #e1e1e1;
	            font-size: 16pt;
	            margin-top: 20px;
	        }
	        QPushButton[type="primary"]:hover {
	            background-color: #ff5555;
	        }
	        QPushButton[type="secondary"]:hover {
	            background-color: #3CB371;
	        }
	    """)

		self.main_layout = QtWidgets.QVBoxLayout(self)
		self.setLayout(self.main_layout)

		# Top layout setup for earnings label and minimize/exit buttons
		self.top_layout = QtWidgets.QHBoxLayout()

		self.update_earnings_button = CustomButton("ნავაჭრის ნახვა")
		self.minimize_button = CustomButton("ჩაკეცვა")
		self.exit_button = CustomButton("გამორთვა")
		self.update_earnings_button.clicked.connect(self.update_earnings)

		self.top_layout.addStretch(1)
		self.top_layout.addWidget(self.update_earnings_button)
		self.top_layout.addWidget(self.minimize_button)
		self.top_layout.addWidget(self.exit_button)

		self.main_layout.addLayout(self.top_layout)

		# Minimize and exit actions
		self.minimize_button.clicked.connect(self.showMinimized)
		self.exit_button.clicked.connect(self.confirm_exit)

		# Scroll area setup for the parking spots
		self.scrollArea = QtWidgets.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		self.scrollAreaContents = QtWidgets.QWidget()
		self.scrollArea.setWidget(self.scrollAreaContents)
		self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaContents)

		# Populate the grid with buttons
		num_buttons = int(self.read_credentials()['number_of_spaces'])
		rows, cols = (num_buttons, 8)
		button_id = 1
		for row in range(rows):
			for col in range(cols):
				if button_id > num_buttons:
					break  # Stop adding buttons if the maximum number is reached
				button = ParkingSpot(str(button_id))
				self.gridLayout.addWidget(button, row, col)
				button_id += 1

		# Add the scroll area to the main layout, below the top layout
		self.main_layout.addWidget(self.scrollArea)

	def update_earnings(self):
		dialog = PasswordDialog(self)
		if dialog.exec():
			password = dialog.password_entry.text()
			if password == str(global_password):
				earnings = self.get_today_earnings()
				msg_box = QtWidgets.QMessageBox()
				msg_box.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
				msg_box.setStyleSheet("""
	                QMessageBox {
	                    background-color: #333; /* Dark background */
	                    color: white; /* White text */
	                    border: none; /* No border */
	                }
	            """)
				msg_box.information(self, 'ნავაჭრი', f'დღის ნავაჭრი: {earnings} ლარი')
			else:
				warning_box = QtWidgets.QMessageBox()
				warning_box.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
				warning_box.setStyleSheet("""
	                QMessageBox {
	                    background-color: #333; /* Dark background */
	                    color: white; /* White text */
	                    border: none; /* No border */
	                }
	            """)
				warning_box.warning(self, 'შეცდომა', 'არასწორი პაროლი.')

	def confirm_exit(self):
		"""Displays a confirmation dialog before exiting the application."""
		reply = QtWidgets.QMessageBox.question(self, 'დაზუსტება',
		                                       "დარწმუნებული ხარ?",
		                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
		                                       QtWidgets.QMessageBox.No)

		if reply == QtWidgets.QMessageBox.Yes:
			QtWidgets.QApplication.instance().quit()


	def get_today_earnings(self):
		"""Retrieves and returns today's total earnings from the database."""

		today = datetime.now().date()
		conn = sqlite3.connect('parking_history.db')
		cursor = conn.cursor()
		cursor.execute("SELECT SUM(ჯამში_გადახდილი) FROM parking_history WHERE DATE(გამოსვლა) = ?", (today,))
		today_earnings = cursor.fetchone()[0]
		conn.close()
		return today_earnings if today_earnings else 0
class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 100)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setStyleSheet("""
            QDialog {
                background-color: #333; /* Dark background */
                color: white; /* White text */
                border-radius: 10px; /* Rounded corners */
            }
            QLabel {
                color: white; /* White text for labels */
                background-color: none; /* No specific background */
                border: none; /* No border */
            }
            QLineEdit {
                border: 2px solid #555; /* Border for line edits */
                border-radius: 5px;
                padding: 5px;
                color: white; /* White text */
                background-color: #222; /* Darker background for line edits */
            }
            QPushButton {
                border: 2px solid #555; /* Border for buttons */
                border-radius: 5px;
                padding: 5px;
                color: white; /* White text */
                background-color: #555; /* Darker background for buttons */
            }
            QPushButton:hover {
                background-color: #777; /* Lighter background on hover */
            }
            QPushButton:pressed {
                background-color: #888; /* Even lighter background for buttons when pressed */
            }
        """)

        layout = QVBoxLayout(self)
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)
        ok_button = QPushButton('კარგი')
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
def main():
	"""Entry point of the application. Initializes and starts the PyQt application."""
	try:
		app = QtWidgets.QApplication(sys.argv)
		window = MainApplication()
		window.showFullScreen()
		sys.exit(app.exec())
	except Exception as e:
		print(e)


if __name__ == '__main__':
	main()
