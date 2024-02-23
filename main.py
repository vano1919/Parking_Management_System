import sys
import re

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import QDialog, QMessageBox, QCompleter, QLabel
import sqlite3
from datetime import datetime

# Dictionary of car makes and models
car_dict = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Sienna", "Tacoma", "Tundra"],
    "Honda": ["Accord", "Civic", "CR-V", "Pilot", "Odyssey", "Fit", "HR-V"],
    # Add more makes and models as needed
}

class CarEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Car Entry")
        layout = QtWidgets.QFormLayout(self)
        self.car_make_entry = QtWidgets.QLineEdit()
        self.car_make_entry.setPlaceholderText("Make")
        self.car_model_entry = QtWidgets.QLineEdit()
        self.car_model_entry.setPlaceholderText("Model")
        self.vin_code_entry = QtWidgets.QLineEdit()
        self.vin_code_entry.setPlaceholderText("VIN Code")

        # Completer for car make entry
        self.make_completer = QCompleter(list(car_dict.keys()))
        self.make_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.make_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.car_make_entry.setCompleter(self.make_completer)

        # Completer for car model entry
        self.model_completer = QCompleter()
        self.model_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.model_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.car_model_entry.setCompleter(self.model_completer)

        layout.addRow("Make:", self.car_make_entry)
        layout.addRow("Model:", self.car_model_entry)
        layout.addRow("VIN Code:", self.vin_code_entry)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.car_make_entry.textChanged.connect(self.update_model_completer)
        self.make_completer.activated.connect(self.move_cursor_to_model)
        self.model_completer.activated.connect(self.move_cursor_to_vin)

    def update_model_completer(self, text):
        make = text.strip().title()
        if make in car_dict:
            models = car_dict[make]
            self.model_completer.setModel(QtCore.QStringListModel(models))
        else:
            self.model_completer.setModel(QtCore.QStringListModel())

    def move_cursor_to_model(self, index):
        self.car_model_entry.setFocus()

    def move_cursor_to_vin(self, index):
        self.vin_code_entry.setFocus()

    def validate_and_accept(self):
        car_make = self.car_make_entry.text().strip().title()
        car_model = self.car_model_entry.text().strip()
        vin_code = self.vin_code_entry.text().strip().upper()

        if not car_make or not car_model or not vin_code:
            self.show_warning("Please fill in all fields.")
            return

        if car_make not in car_dict or car_model.lower() not in map(str.lower, car_dict[car_make]):
            confirm_dialog = self.show_confirm("Model not found. Do you want to add it?")
            if confirm_dialog == QMessageBox.Yes:
                self.accept()
        else:
            vin_regex = re.compile(r'^[A-HJ-NPR-Za-hj-npr-z\d]{8}[\dX][A-HJ-NPR-Za-hj-npr-z\d]{2}\d{6}$')  # Basic VIN format validation
            if not vin_regex.match(vin_code):
                self.show_warning("Invalid VIN Code.")
            else:
                confirm_vin_dialog = self.show_confirm(f"Is the VIN Code '{vin_code}' correct?")
                if confirm_vin_dialog == QMessageBox.Yes:
                    if not self.vin_code_exists_in_current(vin_code):
                        self.accept()
                    else:
                        self.show_warning("Car with this VIN Code is already parked.")
    def show_warning(self, message):
        QMessageBox.warning(self, "Warning", message)

    def show_confirm(self, message):
        return QMessageBox.question(self, "Confirmation", message, QMessageBox.Yes | QMessageBox.No)


    def vin_code_exists_in_current(self, vin_code):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parking WHERE vin_code = ?", (vin_code,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def get_result(self):
        car_make = self.car_make_entry.text().strip().title()
        car_model = self.car_model_entry.text().strip()
        vin_code = self.vin_code_entry.text().strip().upper()
        return car_make, car_model, vin_code


class ParkingSpot(QtWidgets.QPushButton):
    def refresh_earnings(self):
        earnings_label = self.parent().findChild(QLabel)
        if earnings_label:
            earnings_label.setText(f"Today's earnings: {self.get_today_earnings()} Lari")

    def __init__(self, id, parent=None):
        super().__init__(parent)
        self.id = id
        self.db_conn = sqlite3.connect('parking_system.db')
        self.db_conn_history = sqlite3.connect('parking_history.db')
        self.is_occupied = False
        self.car_make = None
        self.car_model = None
        self.vin_code = None
        self.total_fee = None
        self.setText(f'Spot {self.id}')
        self.setStyleSheet("background-color: green; color: white; font-weight: bold; font-size: 14px;")
        self.setMinimumHeight(50)
        self.setMinimumWidth(100)
        self.clicked.connect(self.toggle)
        self.refresh_spot_status()

    def toggle(self):
        if not self.is_occupied:
            self.add_car()
        else:
            self.confirm_remove_car()

    def add_car(self):
        dialog = CarEntryDialog()
        if dialog.exec():
            car_make, car_model, vin_code = dialog.get_result()
            if car_make and car_model and vin_code:
                self.is_occupied = True
                self.car_make = car_make
                self.car_model = car_model
                self.vin_code = vin_code
                self.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 14px;")
                self.setText(f'{self.car_make}\n{self.car_model}\n{self.vin_code}')
                entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.db_conn.execute('INSERT INTO parking (car_make, car_model, vin_code, entry_time, spot_id) VALUES (?, ?, ?, ?, ?)',
                                     (car_make, car_model, vin_code, entry_time, self.id))
                self.db_conn.commit()

    def confirm_remove_car(self):
        entry_info = self.db_conn.execute(
            'SELECT entry_time, car_make, car_model, vin_code FROM parking WHERE spot_id = ? AND exit_time IS NULL',
            (self.id,)).fetchone()
        print("Entry Info:", entry_info)  # Add this line
        if entry_info is None or entry_info[0] is None:
            self.show_warning("Car has already exited.")
            return
        entry_time_str, car_make, car_model, vin_code = entry_info
        entry_time = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
        exit_time = datetime.now()
        parking_duration = exit_time - entry_time
        total_days = parking_duration.days
        self.total_fee = max(total_days * 5, 5)

        payment_info = f"Car Make: {car_make}\nModel: {car_model}\nVIN Code: {vin_code}\nDays: {total_days}\nTotal Fee: {self.total_fee} Lari"
        reply = QMessageBox.question(self, "Payment", payment_info + "\nDo you want to exit the car?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            confirm_dialog = QMessageBox.question(self, "Confirmation", "Are you sure you want to remove the car?",
                                                  QMessageBox.Yes | QMessageBox.No)
            if confirm_dialog == QMessageBox.Yes:
                self.exit_car()

    def exit_car(self):
        entry_info = self.db_conn.execute(
            'SELECT entry_time, car_make, car_model, vin_code FROM parking WHERE spot_id = ? AND exit_time IS NULL',
            (self.id,)).fetchone()
        if entry_info is None or entry_info[0] is None:
            self.show_warning("Car has already exited.")
            return
        entry_time_str, car_make, car_model, vin_code = entry_info
        self.is_occupied = False
        self.setStyleSheet("background-color: green; color: white; font-weight: bold; font-size: 14px;")
        self.setText(f'Spot {self.id}')
        entry_time = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
        exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parking_duration = datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S") - entry_time
        total_days = parking_duration.days
        self.total_fee = max(total_days * 5, 5)

        self.db_conn.execute('UPDATE parking SET exit_time = ?, total_fee = ? WHERE spot_id = ? AND exit_time IS NULL',
                             (exit_time, self.total_fee, self.id))
        self.db_conn_history.execute(
            'INSERT INTO parking_history (car_make, car_model, vin_code, entry_time, exit_time, total_fee) VALUES (?, ?, ?, ?, ?, ?)',
            (car_make, car_model, vin_code, entry_time, exit_time, self.total_fee))
        self.db_conn.commit()
        self.db_conn_history.commit()

        # Remove the car entry from the current parking
        self.db_conn.execute('DELETE FROM parking WHERE vin_code = ?', (vin_code,))
        self.db_conn.commit()

        self.refresh_earnings()


    def refresh_spot_status(self):
        car_info = self.db_conn.execute('SELECT car_make, car_model, vin_code FROM parking WHERE spot_id = ? AND exit_time IS NULL', (self.id,)).fetchone()
        if car_info:
            self.is_occupied = True
            self.car_make, self.car_model, self.vin_code = car_info
            self.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 14px;")
            self.setText(f'{self.car_make}\n{self.car_model}\n{self.vin_code}')
        else:
            self.is_occupied = False
            self.setStyleSheet("background-color: green; color: white; font-weight: bold; font-size: 14px;")
            self.setText(f'Spot {self.id}')

    @staticmethod
    def get_today_earnings():
        today = datetime.now().date()
        conn = sqlite3.connect('parking_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total_fee) FROM parking_history WHERE DATE(exit_time) = ?", (today,))
        today_earnings = cursor.fetchone()[0]
        conn.close()
        return today_earnings if today_earnings else 0

def init_db():
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_make TEXT,
            car_model TEXT,
            vin_code TEXT,
            entry_time TEXT,
            exit_time TEXT,
            total_fee REAL,
            spot_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

    conn_history = sqlite3.connect('parking_history.db')
    cursor_history = conn_history.cursor()
    cursor_history.execute('''
        CREATE TABLE IF NOT EXISTS parking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_make TEXT,
            car_model TEXT,
            vin_code TEXT,
            entry_time TEXT,
            exit_time TEXT,
            total_fee REAL
        )
    ''')
    conn_history.commit()
    conn_history.close()

def main():
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    root = QtWidgets.QWidget()
    root.setWindowTitle("Parking System")
    layout = QtWidgets.QGridLayout(root)

    spots = [ParkingSpot(i + 1) for i in range(70)]  # Adjust the number of spots as needed
    row, col = 0, 0
    for spot in spots:
        layout.addWidget(spot, row, col)
        col += 1
        if col == 10:
            col = 0
            row += 1

    earnings_label = QLabel()
    earnings_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 20px;")
    earnings_label.setAlignment(QtCore.Qt.AlignCenter)
    earnings_label.setText(f"Today's earnings: {ParkingSpot.get_today_earnings()} Lari")
    layout.addWidget(earnings_label, row + 1, 0, 1, 10)

    root.setLayout(layout)
    root.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
