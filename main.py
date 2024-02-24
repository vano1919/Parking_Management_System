import sys
import re

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import QDialog, QMessageBox, QCompleter, QLabel
import sqlite3
from datetime import datetime

car_dict = {
    "Mitsubishi": ["Outlander", "Eclipse Cross", "Mirage", "Pajero", "L200", "ASX", "Triton", "Space Star", "Montero",
                   "Galant"],
    "Chrysler": ["300", "Pacifica", "Voyager", "Aspen", "Sebring", "Crossfire", "PT Cruiser"],
    "Dodge": ["Charger", "Challenger", "Durango", "Journey", "Grand Caravan", "Dakota", "Viper", "Nitro", "Avenger"],
    "Subaru": ["Outback", "Forester", "Crosstrek", "Legacy", "Impreza", "Ascent", "BRZ", "WRX", "Levorg", "Baja",
               "Tribeca"],
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Sienna", "Tacoma", "Tundra", "4Runner", "Avalon",
               "Yaris", "Land Cruiser", "Supra", "C-HR", "Sequoia", "Corolla Cross"],
    "Honda": ["Accord", "Civic", "CR-V", "Pilot", "Odyssey", "Fit", "HR-V", "Ridgeline", "Insight", "Passport",
              "Clarity", "Element", "CR-Z"],
    "Aston Martin": ["DB11", "DBS Superleggera", "Vantage", "DBX", "Rapide", "Vanquish", "Virage", "DB7"],
    "Lexus": ["RX", "ES", "NX", "UX", "IS", "GX", "LS", "LC", "RC", "LFA", "CT", "LX", "HS"],
    "Lotus": ["Evora", "Exige", "Elise", "Emira"],
    "Alfa Romeo": ["Giulia", "Stelvio", "4C", "8C", "Giulietta", "Spider", "Brera", "MiTo"],
    "Maserati": ["Ghibli", "Levante", "Quattroporte", "GranTurismo", "GranCabrio", "Spyder", "Coupe"],
    "Rolls-Royce": ["Phantom", "Ghost", "Cullinan", "Wraith", "Dawn", "Silver Ghost", "Park Ward", "Corniche"],
    "Bugatti": ["Chiron", "Divo", "Centodieci", "La Voiture Noire", "EB110", "Veyron"],
    "Genesis": ["G70", "G80", "G90", "GV80", "GV70", "G60"],
    "Porsche": ["911", "Cayenne", "Macan", "Panamera", "Taycan", "718", "Carrera GT", "Boxster", "Cayman"],
    "Mini": ["Cooper", "Countryman", "Clubman", "Convertible", "Paceman", "Roadster", "Coupe"],
    "Smart": ["EQ fortwo", "Forfour", "Crossblade", "Roadster"],
    "Fiat": ["500", "500X", "500L", "124 Spider", "Panda", "Tipo", "Punto", "Doblo", "Qubo", "Talento"],
    "Jaguar": ["F-PACE", "E-PACE", "XE", "XF", "F-TYPE", "I-PACE", "XJ", "XK", "S-Type"],
    "Volvo": ["XC90", "XC60", "S60", "V60", "XC40", "S90", "V90", "V60 Cross Country", "V90 Cross Country", "P1800",
              "C30", "S80", "XC70"],
    "Buick": ["Encore", "Enclave", "Envision", "Regal", "Lacrosse", "Verano", "Cascada"],
    "Tesla": ["Model S", "Model 3", "Model X", "Model Y", "Roadster", "Cybertruck", "Model C"],
    "Audi": ["A4", "Q5", "A3", "Q7", "A6", "Q3", "A5", "Q8", "e-tron", "RS 3", "RS 6", "TT", "R8", "S4", "S5", "S6"],
    "Ford": ["Fusion", "Escape", "Explorer", "F-150", "Mustang", "Edge", "Ranger", "Expedition", "EcoSport", "Transit",
             "Flex", "Bronco", "Focus", "C-Max", "Taurus"],
    "Chevrolet": ["Silverado", "Equinox", "Malibu", "Traverse", "Tahoe", "Suburban", "Camaro", "Colorado",
                  "Trailblazer", "Spark", "Blazer", "Cruze", "Impala", "Volt", "Bolt EV"],
    "Nissan": ["Altima", "Rogue", "Sentra", "Pathfinder", "Murano", "Versa", "Frontier", "Titan", "Kicks", "Armada",
               "Maxima", "Leaf", "370Z", "GT-R", "Juke"],
    "Mercedes-Benz": ["C-Class", "GLC", "E-Class", "GLE", "A-Class", "GLA", "S-Class", "GLS", "CLA", "CLS", "GLB",
                      "SLC", "SL", "AMG GT", "G-Class", "Maybach"],
    "BMW": ["3 Series", "X3", "5 Series", "X5", "2 Series", "X1", "4 Series", "7 Series", "X7", "i3", "8 Series", "Z4",
            "X6", "M2", "M4", "M5", "i8"],
    "Land Rover": ["Range Rover", "Range Rover Sport", "Range Rover Evoque", "Discovery", "Discovery Sport", "Defender",
                   "Velar", "Freelander"],
    "Infiniti": ["QX60", "QX80", "Q50", "QX50", "QX30", "Q60", "FX35", "G35", "G37", "EX35", "M35", "M45"],
    "Lincoln": ["Navigator", "Aviator", "Corsair", "Nautilus", "MKZ", "Continental", "MKT", "MKX"],
    "Acura": ["MDX", "RDX", "TLX", "ILX", "RLX", "NSX", "ZDX", "TSX"],
    "GMC": ["Sierra", "Acadia", "Terrain", "Yukon", "Canyon", "Envoy", "Savana", "Jimmy"],
    "Ram": ["1500", "2500", "3500", "Promaster", "Promaster City", "Dakota", "Ramcharger"],
    "Polestar": ["Polestar 1", "Polestar 2", "Polestar 3", "Polestar 4"],
    "Rivian": ["R1T", "R1S", "R2", "R3"],
    "Lucid": ["Air", "Gravity", "Dream"],
    "Koenigsegg": ["Jesko", "Regera", "Gemera", "CCX", "Agera", "One:1", "CCR", "CC8S"],
    "McLaren": ["570S", "720S", "GT", "600LT", "Speedtail", "P1", "675LT", "765LT"],
    "Ferrari": ["F8 Tributo", "812 Superfast", "SF90 Stradale", "Roma", "Portofino", "LaFerrari", "488 GTB",
                "California T"],
    "Kia": ["Seltos", "Telluride", "Sportage", "Sorento", "Forte", "Stinger", "Rio", "Soul", "Cadenza", "K900",
            "Optima", "Niro"],
    "Hyundai": ["Santa Fe", "Tucson", "Palisade", "Elantra", "Sonata", "Accent", "Veloster", "Venue", "Nexo", "Ioniq",
                "Kona", "Genesis", "Azera"],
    "Jeep": ["Wrangler", "Grand Cherokee", "Cherokee", "Renegade", "Compass", "Gladiator", "Wagoneer", "Grand Wagoneer",
             "Patriot", "Liberty"],
    "Mazda": ["CX-5", "CX-9", "CX-30", "Mazda3", "Mazda6", "MX-5 Miata", "MX-30", "RX-8", "Tribute", "Protege", "CX-3"],
    "Volkswagen": ["Golf", "Jetta", "Passat", "Tiguan", "Atlas", "Arteon", "Taos", "ID.4", "Atlas Cross Sport",
                   "Beetle", "CC", "Eos", "Golf R"],
    "Renault": ["Clio", "Captur", "Megane", "Kadjar", "Duster", "Talisman", "Koleos", "Twingo", "Zoe", "Scenic",
                "Espace", "Fluence"],
    "Peugeot": ["208", "2008", "308", "3008", "5008", "508", "Rifter", "Partner", "Traveller", "Expert", "RCZ", "207"],
    "Citroen": ["C3", "C4", "C5 Aircross", "C1", "C3 Aircross", "C4 Cactus", "Berlingo", "SpaceTourer", "Jumpy", "DS3",
                "DS4", "DS5"],
    "Opel": ["Corsa", "Astra", "Crossland", "Grandland X", "Mokka", "Zafira", "Insignia", "Combo", "Vivaro", "Movano",
             "Meriva", "Adam"],
    "Fiat": ["500", "500X", "500L", "124 Spider", "Panda", "Tipo", "Punto", "Doblo", "Qubo", "Talento", "Freemont",
             "Linea"],
    "Alpine": ["A110", "A310", "A610", "A120", "Berlinette"],
    "Skoda": ["Octavia", "Superb", "Kodiaq", "Karoq", "Scala", "Fabia", "Citigo", "Enyaq", "Rapid", "Yeti"],
    "Seat": ["Ibiza", "Leon", "Arona", "Ateca", "Tarraco", "Mii", "Alhambra", "Toledo", "Cupra", "Exeo"],
    "Dacia": ["Sandero", "Duster", "Logan", "Spring", "Lodgy", "Dokker", "Solenza", "Sandero Stepway"],
    "Suzuki": ["Swift", "Vitara", "Jimny", "S-Cross", "Ignis", "Baleno", "Celerio", "SX4", "Alto", "Kizashi"],
    "Lada": ["Granta", "Vesta", "4x4 Urban", "Kalina", "Niva", "XRAY", "Largus", "Priora"],
    "Geely": ["Coolray", "Azkarra", "Emgrand", "Bo Yue", "Borui", "Vision", "Jiaji", "Xingyue", "Atlas", "Emgrand X7"],
    "Chery": ["Tiggo 7", "Arrizo 5", "Tiggo 8", "Tiggo 4", "Arrizo 7", "Arrizo 3", "QQ", "Tiggo 3", "Tiggo 5",
              "Tiggo 2"],
    "BYD": ["Tang", "Han", "Yuan", "Song", "F3", "Qin", "e2", "S7", "e3", "e1", "e6", "F6", "S2"],
    "Great Wall": ["Haval H6", "Haval H9", "Haval F7", "Haval F5", "Haval H2", "Haval H4", "Haval H1", "Haval Jolion",
                   "Wey VV5", "Wey VV7", "Ora R1", "Ora Black Cat"],
    "BAIC": ["Senova X25", "Senova X55", "Senova X65", "Senova D20", "Senova D50", "Senova D70", "Senova D80",
             "Senova D60", "Senova D35", "Senova Zhidao", "BJ40", "EU-Series"],
    "Zotye": ["T600", "T300", "T700", "SR9", "T500", "T700EV", "E200", "Z100", "T600 Coupe", "Langyue", "T800",
              "Damai X7"],
    "JAC": ["S2", "S3", "S5", "S7", "iEV7S", "iEV6S", "iEV7", "iEV6E", "iEV6S", "iEV7S", "Refine", "J4"],
    "Wuling": ["Hong Guang S3", "Hong Guang S5", "Hong Guang MINI EV", "Zhiguang", "Rong Guang", "Zhiguang PLUS",
               "Zhiguang V", "Zhiguang ONE", "Zhiguang R", "Zhiguang C", "Baojun 510", "Baojun 730"],
    "WEY": ["VV5", "VV6", "P8", "Tank 300", "Tank 500", "Tank 600", "Tank 700", "Tank 800", "Tank X", "Tank X3", "VV7"],
    "Hongqi": ["HS5", "HS7", "HS3", "HS8", "E-HS3", "E-HS7", "E-HS9", "E-HS5", "H9", "H5", "L5", "E-HS3"],
    "Haval": ["Jolion", "Big Dog", "Little Dog", "F5", "F7", "F7X", "F9", "F3", "F3X", "M6", "M4", "H2S"],
    "Landwind": ["X7", "X5", "X8", "X2", "X9", "X4", "X6", "X3", "X1", "X2", "E33", "E36"]
}


class CarEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Car Entry")
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: 'Arial';
                font-size: 14px;
            }
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 10px;
                font-size: 16px;
            }
            QLabel {
                font-size: 16px;
                margin-bottom: 5px;
            }
            QDialogButtonBox {
                margin-top: 15px;
            }
            QPushButton {
                border: 1px solid #8f8f91;
                border-radius: 6px;
                background-color: #e7e7e7;
                min-width: 100px;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #d7d7d7;
            }
            QPushButton:pressed {
                background-color: #c7c7c7;
            }
        """)

        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(20)

        self.car_make_entry = QtWidgets.QLineEdit()
        self.car_make_entry.setPlaceholderText("Enter car make")
        self.car_model_entry = QtWidgets.QLineEdit()
        self.car_model_entry.setPlaceholderText("Enter car model")
        self.vin_code_entry = QtWidgets.QLineEdit()
        self.vin_code_entry.setPlaceholderText("Enter VIN code")
        # Adjust mask as needed for VIN format

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

        # Set up signals for updating and moving focus
        self.car_make_entry.textChanged.connect(self.update_model_completer)
        self.make_completer.activated.connect(lambda: self.car_model_entry.setFocus())
        self.model_completer.activated.connect(lambda: self.vin_code_entry.setFocus())

        layout.addRow("Make:", self.car_make_entry)
        layout.addRow("Model:", self.car_model_entry)
        layout.addRow("VIN Code:", self.vin_code_entry)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setFixedSize(400, 300)  # Set fixed size for the dialog

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
            vin_regex = re.compile(
                r'^[A-HJ-NPR-Za-hj-npr-z\d]{8}[\dX][A-HJ-NPR-Za-hj-npr-z\d]{2}\d{6}$')  # Basic VIN format validation
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
                self.db_conn.execute(
                    'INSERT INTO parking (car_make, car_model, vin_code, entry_time, spot_id) VALUES (?, ?, ?, ?, ?)',
                    (car_make, car_model, vin_code, entry_time, self.id))
                self.db_conn.commit()

    def confirm_remove_car(self):
        entry_info = self.db_conn.execute(
            'SELECT entry_time, car_make, car_model, vin_code FROM parking WHERE spot_id = ? AND exit_time IS NULL',
            (self.id,)).fetchone()

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
        car_info = self.db_conn.execute(
            'SELECT car_make, car_model, vin_code FROM parking WHERE spot_id = ? AND exit_time IS NULL',
            (self.id,)).fetchone()
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
    root.setStyleSheet("""
        QWidget {
            background-color: #333; /* Dark asphalt-like background for the main window to simulate road surface */
            color: #FFF; /* White text for better readability */
        }
        QPushButton {
            font-size: 12px;
            border: 2px solid #FFF; /* White border to simulate parking space lines */
            border-radius: 5px; /* Slightly rounded corners for a more realistic parking space look */
            padding: 5px;
            background-color: #555; /* Darker shade for the parking spot to resemble actual parking space */
            color: #FFF; /* White text color for visibility */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5); /* Subtle shadow for a 3D effect */
            margin: 8px; /* Ensure spacing between parking spots */
            min-width: 80px; /* Minimum width for each parking space */
            min-height: 40px; /* Minimum height for each parking space */
        }
        QPushButton:hover {
            background-color: #666; /* Slightly lighter shade on hover to indicate selection */
        }
        QPushButton:pressed {
            background-color: #777; /* Even lighter shade when pressed to simulate button press */
        }
        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #17a2b8; /* Color for the earnings label */
            padding: 5px;
            margin-top: 20px;
            margin-bottom: 20px; /* Space above and below the label */
        }
    """)

    layout = QtWidgets.QGridLayout(root)
    spots = [ParkingSpot(i + 1) for i in range(65)]  # Adjust the number of spots as needed
    row, col = 0, 0
    for spot in spots:
        layout.addWidget(spot, row, col)
        col += 1
        if col == 10:  # Adjust based on layout preference
            col = 0
            row += 1

    earnings_label = QLabel(f"Today's earnings: {ParkingSpot.get_today_earnings()} Lari")
    earnings_label.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(earnings_label, row + 1, 0, 1, 10)  # Span the label across the entire grid width

    root.setLayout(layout)
    root.resize(800, 600)  # Adjust the size of the main window as needed
    root.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
