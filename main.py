import sys
import re
from PyQt5.QtCore import QStringListModel
from PySide6.QtWidgets import QCompleter
from PySide6.QtGui import QStandardItem
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QCompleter, QDialog, QFormLayout, QLineEdit, QVBoxLayout, QLabel, QDialogButtonBox, \
    QMessageBox, QApplication
from PySide6.QtCore import Qt, \
    QStringListModel  # Add any other needed modules but you might not need QStringListModel for PySide6
from PySide6.QtGui import QStandardItem, QStandardItemModel  # Ensure this is correctly placed
import subprocess
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox, QCompleter, QLabel, QVBoxLayout, QPushButton, QWidget, \
    QDialogButtonBox, QGridLayout, QFormLayout, QLineEdit
import sqlite3
from datetime import datetime
import os
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import requests
import os
import requests
import sqlite3
import webbrowser
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from zipfile import ZipFile


# T

class EnterMoveQLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.focusNextChild()  # Moves focus to next widget in the tab order
        else:
            super().keyPressEvent(event)  # Handle other key events normally


class CarEntryDialog(QDialog):
    def __init__(self, parent=None):  # Pass car_dict as parameter
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

        # Main layout
        main_layout = QVBoxLayout(self)

        # Car details layout
        car_details_layout = QFormLayout()
        self.ავტომობილის_მარკა_entry = EnterMoveQLineEdit()
        self.ავტომობილის_მოდელი_entry = EnterMoveQLineEdit()
        self.vin_კოდი_entry = EnterMoveQLineEdit()
        car_details_layout.addRow("მარკა:", self.ავტომობილის_მარკა_entry)
        car_details_layout.addRow("მოდელი:", self.ავტომობილის_მოდელი_entry)
        car_details_layout.addRow("VIN კოდი:", self.vin_კოდი_entry)
        main_layout.addLayout(car_details_layout)

        self.car_dict = {
            "Mitsubishi": ["Outlander", "Eclipse Cross", "Mirage", "Pajero", "L200", "ASX", "Triton", "Space Star",
                           "Montero",
                           "Galant"],
            "Chrysler": ["300", "Pacifica", "Voyager", "Aspen", "Sebring", "Crossfire", "PT Cruiser"],
            "Dodge": ["Charger", "Challenger", "Durango", "Journey", "Grand Caravan", "Dakota", "Viper", "Nitro",
                      "Avenger"],
            "Subaru": ["Outback", "Forester", "Crosstrek", "Legacy", "Impreza", "Ascent", "BRZ", "WRX", "Levorg",
                       "Baja",
                       "Tribeca"],
            "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Sienna", "Tacoma", "Tundra", "4Runner",
                       "Avalon",
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
            "Volvo": ["XC90", "XC60", "S60", "V60", "XC40", "S90", "V90", "V60 Cross Country", "V90 Cross Country",
                      "P1800",
                      "C30", "S80", "XC70"],
            "Buick": ["Encore", "Enclave", "Envision", "Regal", "Lacrosse", "Verano", "Cascada"],
            "Tesla": ["Model S", "Model 3", "Model X", "Model Y", "Roadster", "Cybertruck", "Model C"],
            "Audi": ["A4", "Q5", "A3", "Q7", "A6", "Q3", "A5", "Q8", "e-tron", "RS 3", "RS 6", "TT", "R8", "S4", "S5",
                     "S6"],
            "Ford": ["Fusion", "Escape", "Explorer", "F-150", "Mustang", "Edge", "Ranger", "Expedition", "EcoSport",
                     "Transit",
                     "Flex", "Bronco", "Focus", "C-Max", "Taurus"],
            "Chevrolet": ["Silverado", "Equinox", "Malibu", "Traverse", "Tahoe", "Suburban", "Camaro", "Colorado",
                          "Trailblazer", "Spark", "Blazer", "Cruze", "Impala", "Volt", "Bolt EV"],
            "Nissan": ["Altima", "Rogue", "Sentra", "Pathfinder", "Murano", "Versa", "Frontier", "Titan", "Kicks",
                       "Armada",
                       "Maxima", "Leaf", "370Z", "GT-R", "Juke"],
            "Mercedes-Benz": ["C-Class", "GLC", "E-Class", "GLE", "A-Class", "GLA", "S-Class", "GLS", "CLA", "CLS",
                              "GLB",
                              "SLC", "SL", "AMG GT", "G-Class", "Maybach"],
            "BMW": ["3 Series", "X3", "5 Series", "X5", "2 Series", "X1", "4 Series", "7 Series", "X7", "i3",
                    "8 Series", "Z4",
                    "X6", "M2", "M4", "M5", "i8"],
            "Land Rover": ["Range Rover", "Range Rover Sport", "Range Rover Evoque", "Discovery", "Discovery Sport",
                           "Defender",
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
            "Hyundai": ["Santa Fe", "Tucson", "Palisade", "Elantra", "Sonata", "Accent", "Veloster", "Venue", "Nexo",
                        "Ioniq",
                        "Kona", "Genesis", "Azera"],
            "Jeep": ["Wrangler", "Grand Cherokee", "Cherokee", "Renegade", "Compass", "Gladiator", "Wagoneer",
                     "Grand Wagoneer",
                     "Patriot", "Liberty"],
            "Mazda": ["CX-5", "CX-9", "CX-30", "Mazda3", "Mazda6", "MX-5 Miata", "MX-30", "RX-8", "Tribute", "Protege",
                      "CX-3"],
            "Volkswagen": ["Golf", "Jetta", "Passat", "Tiguan", "Atlas", "Arteon", "Taos", "ID.4", "Atlas Cross Sport",
                           "Beetle", "CC", "Eos", "Golf R"],
            "Renault": ["Clio", "Captur", "Megane", "Kadjar", "Duster", "Talisman", "Koleos", "Twingo", "Zoe", "Scenic",
                        "Espace", "Fluence"],
            "Peugeot": ["208", "2008", "308", "3008", "5008", "508", "Rifter", "Partner", "Traveller", "Expert", "RCZ",
                        "207"],
            "Citroen": ["C3", "C4", "C5 Aircross", "C1", "C3 Aircross", "C4 Cactus", "Berlingo", "SpaceTourer", "Jumpy",
                        "DS3",
                        "DS4", "DS5"],
            "Opel": ["Corsa", "Astra", "Crossland", "Grandland X", "Mokka", "Zafira", "Insignia", "Combo", "Vivaro",
                     "Movano",
                     "Meriva", "Adam"],
            "Fiat": ["500", "500X", "500L", "124 Spider", "Panda", "Tipo", "Punto", "Doblo", "Qubo", "Talento",
                     "Freemont",
                     "Linea"],
            "Alpine": ["A110", "A310", "A610", "A120", "Berlinette"],
            "Skoda": ["Octavia", "Superb", "Kodiaq", "Karoq", "Scala", "Fabia", "Citigo", "Enyaq", "Rapid", "Yeti"],
            "Seat": ["Ibiza", "Leon", "Arona", "Ateca", "Tarraco", "Mii", "Alhambra", "Toledo", "Cupra", "Exeo"],
            "Dacia": ["Sandero", "Duster", "Logan", "Spring", "Lodgy", "Dokker", "Solenza", "Sandero Stepway"],
            "Suzuki": ["Swift", "Vitara", "Jimny", "S-Cross", "Ignis", "Baleno", "Celerio", "SX4", "Alto", "Kizashi"],
            "Lada": ["Granta", "Vesta", "4x4 Urban", "Kalina", "Niva", "XRAY", "Largus", "Priora"],
            "Geely": ["Coolray", "Azkarra", "Emgrand", "Bo Yue", "Borui", "Vision", "Jiaji", "Xingyue", "Atlas",
                      "Emgrand X7"],
            "Chery": ["Tiggo 7", "Arrizo 5", "Tiggo 8", "Tiggo 4", "Arrizo 7", "Arrizo 3", "QQ", "Tiggo 3", "Tiggo 5",
                      "Tiggo 2"],
            "BYD": ["Tang", "Han", "Yuan", "Song", "F3", "Qin", "e2", "S7", "e3", "e1", "e6", "F6", "S2"],
            "Great Wall": ["Haval H6", "Haval H9", "Haval F7", "Haval F5", "Haval H2", "Haval H4", "Haval H1",
                           "Haval Jolion",
                           "Wey VV5", "Wey VV7", "Ora R1", "Ora Black Cat"],
            "BAIC": ["Senova X25", "Senova X55", "Senova X65", "Senova D20", "Senova D50", "Senova D70", "Senova D80",
                     "Senova D60", "Senova D35", "Senova Zhidao", "BJ40", "EU-Series"],
            "Zotye": ["T600", "T300", "T700", "SR9", "T500", "T700EV", "E200", "Z100", "T600 Coupe", "Langyue", "T800",
                      "Damai X7"],
            "JAC": ["S2", "S3", "S5", "S7", "iEV7S", "iEV6S", "iEV7", "iEV6E", "iEV6S", "iEV7S", "Refine", "J4"],
            "Wuling": ["Hong Guang S3", "Hong Guang S5", "Hong Guang MINI EV", "Zhiguang", "Rong Guang",
                       "Zhiguang PLUS",
                       "Zhiguang V", "Zhiguang ONE", "Zhiguang R", "Zhiguang C", "Baojun 510", "Baojun 730"],
            "WEY": ["VV5", "VV6", "P8", "Tank 300", "Tank 500", "Tank 600", "Tank 700", "Tank 800", "Tank X", "Tank X3",
                    "VV7"],
            "Hongqi": ["HS5", "HS7", "HS3", "HS8", "E-HS3", "E-HS7", "E-HS9", "E-HS5", "H9", "H5", "L5", "E-HS3"],
            "Haval": ["Jolion", "Big Dog", "Little Dog", "F5", "F7", "F7X", "F9", "F3", "F3X", "M6", "M4", "H2S"],
            "Landwind": ["X7", "X5", "X8", "X2", "X9", "X4", "X6", "X3", "X1", "X2", "E33", "E36"]
        }

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

        # Owner details layout
        owner_details_layout = QGridLayout()
        # Owner details layout continuation
        self.სახელი_entry = EnterMoveQLineEdit()
        self.გვარი_entry = EnterMoveQLineEdit()
        self.პირადი_ნომერი_entry = EnterMoveQLineEdit()
        self.ტელეფონის_ნომერი_entry = EnterMoveQLineEdit()  # Phone number field
        # In CarEntryDialog.__init__:
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
        # Parking fee entry

        car_details_layout.addRow("პარკინგის ტარიფი:",
                                  self.ინდივიდუალური_გადასახადი_entry)  # Add this to the form layout
        main_layout.addLayout(owner_details_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setFixedSize(800, 450)  # Adjusted size for new fields

    def update_model_completer(self, text):
        make = text.strip().title()  # Format text for consistency
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
        self.ავტომობილის_მოდელი_entry.setFocus()

    def move_cursor_to_vin(self, index):
        self.vin_კოდი_entry.setFocus()

    def validate_and_accept(self):
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
                if not self.vin_კოდი_exists_in_current(vin_კოდი):
                    self.accept()


                else:
                    self.show_warning("ავტომობილი ამ VIN კოდით უკვე დამატებულია.")
        else:
            self.accept()

    def show_warning(self, message):
        QMessageBox.warning(self, "გაფრთხილება", message)

    def show_confirm(self, message):
        return QMessageBox.question(self, "დაადასტურე", message, QMessageBox.Yes | QMessageBox.No)

    def vin_კოდი_exists_in_current(self, vin_კოდი):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parking WHERE vin_კოდი = ?", (vin_კოდი,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def get_result(self):
        # Ensure all seven fields are being returned:
        return (self.ავტომობილის_მარკა_entry.text().strip().title(),
                self.ავტომობილის_მოდელი_entry.text().strip(),
                self.vin_კოდი_entry.text().strip().upper(),
                self.სახელი_entry.text().strip(),  # Ensure this is correctly capturing input
                self.გვარი_entry.text().strip(),  # Ensure this is correctly capturing input
                self.პირადი_ნომერი_entry.text().strip(),  # Ensure this is correctly capturing input
                self.ტელეფონის_ნომერი_entry.text().strip())  # Ensure this is correctly capturing input


class ParkingSpot(QtWidgets.QPushButton):
    def refresh_earnings(self):
        earnings_label = self.parent().findChild(QLabel)
        if earnings_label:
            earnings_label.setText(f"დღის ნავაჭრია {self.get_today_earnings()} ლარი")

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
        if not self.is_occupied:
            self.add_car()
        else:
            self.confirm_remove_car()

    def add_car(self):
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
                    (ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი,
                     datetime.now(),
                     self.id, ინდივიდუალური_გადასახადი)
                )
                self.db_conn.commit()
                self.print_car_details(self.id, status="entry_check")
            except sqlite3.Error as e:
                print("An error occurred:", e)
            self.refresh_earnings()
            self.refresh_spot_status()

    def confirm_remove_car(self):

        # Fetch car entry information from the database
        entry_info = self.db_conn.execute(
            'SELECT ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა, პარკინგის_ადგილი, ინდივიდუალური_გადასახადი FROM parking WHERE პარკინგის_ადგილი = ? AND გამოსვლა IS NULL',
            (self.id,)).fetchone()

        # Check if car information is not found or already checked out
        if entry_info is None:
            self.show_warning("მანქანა უკვე გამოსულია.")
            return

        # Extract car details
        # Assuming 'entry_info' contains all necessary car and parking information.
        # Extract car details
        ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა_str, პარკინგის_ადგილი, ინდივიდუალური_გადასახადი = entry_info

        # Convert entry and exit timestamps to dates
        entry_date = datetime.strptime(შესვლა_str, "%Y-%m-%d %H:%M:%S.%f").date()
        exit_date = datetime.now().date()  # This removes the time part, keeping only the date

        ინდივიდუალური_გადასახადი = entry_info[-1]  # Assuming it's the last in the fetched data
        total_days = (exit_date - entry_date).days + 1
        self.ჯამში_გადახდილი = total_days * ინდივიდუალური_გადასახადი

        # Prepare payment information
        payment_info = f"<html><head/><body><p><span style='font-weight:600;'>ავტომობილი:</span> {ავტომობილის_მარკა} {ავტომობილის_მოდელი}</p>" \
                       f"<p><span style='font-weight:600;'>VIN კოდი:</span> {vin_კოდი}</p>" \
                       f"<p><span style='font-weight:600;'>მფლობელი:</span> {სახელი} {გვარი} ({პირადი_ნომერი})</p>" \
                       f"<p><span style='font-weight:600;'>ტელ:</span> {ტელეფონის_ნომერი}</p>" \
                       f"<p><span style='font-weight:600;'>ავტომობილი სადგომზე იმყოფებოდა:</span> {total_days} დღე</p>" \
                       f"<p style='margin-top:20px;'><span style='font-size:18px; font-weight:700;'>სულ გადასახდელია:</span> <span style='font-size:24px; color:#4A90E2;'>{self.ჯამში_გადახდილი} ლარი</span></p></body></html>"

        # Create new dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("ავტომობილის გადასახადის შესახებ ინფორმაცია")
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

        # Create layout and widgets
        # Create layout and widgets
        layout = QVBoxLayout()
        info_widget = QWidget()  # Use a QWidget to contain the label for styling
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

        # Create and style the 'Finish Parking' button
        finish_button = QPushButton("პარკინგის დასრულება")
        finish_button.setStyleSheet("""
            background-color: #4A90E2; /* Consistent blue color for action buttons */
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 5px;
            margin-top: 20px;
        """)
        finish_button.clicked.connect(lambda: self.user_confirmed_exit(dialog, self.confirm_exit_with_password()))
        layout.addWidget(finish_button)

        # Optionally add a 'Cancel' button
        cancel_button = QPushButton("გაუქმება")
        cancel_button.setStyleSheet("""
            background-color: #CCCCCC; /* Grey color for cancel button */
            color: #333333; /* Dark grey text */
            font-weight: normal;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 5px;
            margin-top: 10px;
        """)
        cancel_button.clicked.connect(lambda: self.user_confirmed_exit(dialog, False))
        layout.addWidget(cancel_button)

        # Set dialog layout
        dialog.setLayout(layout)
        dialog.exec()
        # Call this method instead of directly exiting

    def user_confirmed_exit(self, dialog, confirmed):
        dialog.close()
        if confirmed:
            self.exit_car()  # Call the exit operation

            # Now, delete the record from the parking system database

    def confirm_exit_with_password(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("პაროლის შეყვანა")
        dialog.setFixedSize(300, 200)
        # Remove window title bar and set modal
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)  # Make the background transparent
        dialog.setModal(True)

        # Create a layout
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

        # Add widgets to the layout
        label = QLabel("პაროლის შეყვანა:")
        layout.addWidget(label)

        password_entry = QLineEdit()
        password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_entry)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        # Connect buttons
        button_box.accepted.connect(lambda: self.check_password_and_exit(password_entry.text(), dialog))
        button_box.rejected.connect(dialog.reject)

        # Show the dialog
        dialog.exec()

    def check_password_and_exit(self, entered_password, dialog):
        # Read the correct password from the file
        with open('credentials.txt', 'r') as file:
            credentials = {}
            for line in file:
                key, value = line.strip().split(': ')
                credentials[key] = value.strip()  # Ensure to strip value

        # Check if the entered password is correct
        if entered_password == credentials.get('password', ''):
            self.exit_car()  # Proceed with exiting the car
            dialog.accept()
            # Assuming self.id contains the პარკინგის_ადგილი
            self.print_car_details(self.id, status="exit_check")

        # Call the print function with the parking spot ID
        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("პაროლი არასწორია")
            msg_box.setText("პაროლი არასწორია")

            # Resize the QMessageBox
            msg_box.setGeometry(1, 0, 400, 200)  # Modify these dimensions as needed

            # Show the QMessageBox
            msg_box.exec()

    def print_car_details(self, parking_spot, status):
        # Setup for script and fonts directory
        script_directory = os.path.dirname(os.path.abspath(__file__))
        fonts_directory = os.path.join(script_directory, 'fonts')

        # Georgian font for Georgian text
        georgian_font_name = 'NotoGeorgian'
        georgian_font_filename = 'NotoSansGeorgian-Regular.ttf'
        georgian_font_path = os.path.join(fonts_directory, georgian_font_filename)

        # Latin font for English text (ensure this font supports the necessary characters)
        latin_font_name = 'Helvetica'  # Using Helvetica as an example; replace with your Latin font if needed

        # Register fonts with ReportLab
        pdfmetrics.registerFont(TTFont(georgian_font_name, georgian_font_path))
        # pdfmetrics.registerFont(TTFont(latin_font_name, latin_font_path)) for custom Latin fonts

        # Define check size
        check_width, check_height = 6 * 72, 2.75 * 72

        pdf_filename = f"car_details.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=(check_width, check_height))

        if status == "entry_check":
            db_name = 'parking_system.db'
        elif status == "exit_check":
            db_name = 'parking_history.db'
        else:
            print("Invalid status")
            return


            # Connect to the database and fetch record
        conn = sqlite3.connect(os.path.join(script_directory, db_name))
        cursor = conn.cursor()
        if status == "entry_check":
            cursor.execute(
                "SELECT ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, შესვლა, ინდივიდუალური_გადასახადი FROM parking WHERE პარკინგის_ადგილი = ?",
                (parking_spot,))
            record = cursor.fetchone()
            ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, შესვლა, ინდივიდუალური_გადასახადი = record
            c.setFont('NotoGeorgian', 5)
            c.drawString(100, 700, f"ავტომობილის: {ავტომობილის_მარკა} {ავტომობილის_მოდელი}")
        else:
            cursor.execute(
                "SELECT ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა, გამოსვლა, ჯამში_გადახდილი FROM parking_history WHERE პარკინგის_ადგილი = ?",
                (parking_spot,))
            record = cursor.fetchone()
            ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა, გამოსვლა, ჯამში_გადახდილი = record
            c.setFont('NotoGeorgian', 5)
            c.drawString(100, 700, f"ავტომობილის: {ავტომობილის_მარკა} {ავტომობილის_მოდელი}")

        conn.close()


        c.save()

        absolute_path = os.path.abspath(pdf_filename)
        webbrowser.open(f'file://{absolute_path}')

    def show_warning(self, message):
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
        # Retrieve the car entry information from the database
        entry_info = self.db_conn.execute(
            'SELECT შესვლა, ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, ინდივიდუალური_გადასახადი FROM parking WHERE პარკინგის_ადგილი = ? AND გამოსვლა IS NULL',
            (self.id,)).fetchone()

        # Check if there is no car information found or if it's already checked out
        if entry_info is None:
            self.show_warning("ავტომობილი უკვე გამოსულია სადგომიდან.")  # Car has already exited
            return

        # Extracting car and parking informationEnterMoveQLineEdit
        შესვლა_str, ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, ინდივიდუალური_გადასახადი = entry_info
        შესვლა = datetime.strptime(შესვლა_str, "%Y-%m-%d %H:%M:%S.%f")
        გამოსვლა = datetime.now()
        total_days = (გამოსვლა.date() - შესვლა.date()).days + 1  # Including the current day
        ჯამში_გადახდილი = total_days * ინდივიდუალური_გადასახადი

        # Updating the database to reflect the car's exit
        self.db_conn.execute(
            'UPDATE parking SET გამოსვლა = ?, ჯამში_გადახდილი = ? WHERE პარკინგის_ადგილი = ? AND გამოსვლა IS NULL',
            (გამოსვლა.strftime("%Y-%m-%d %H:%M:%S"), ჯამში_გადახდილი, self.id))
        self.db_conn.commit()

        # Inserting the exit record into the parking history database
        self.db_conn_history.execute(
            'INSERT INTO parking_history (ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი, შესვლა, გამოსვლა, ჯამში_გადახდილი,პარკინგის_ადგილი) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი, სახელი, გვარი, პირადი_ნომერი, ტელეფონის_ნომერი,
                შესვლა_str,
                გამოსვლა.strftime("%Y-%m-%d %H:%M:%S"), ჯამში_გადახდილი, self.id), )
        self.db_conn_history.commit()
        self.db_conn.execute(
            'DELETE FROM parking WHERE პარკინგის_ადგილი = ?',
            (self.id,))
        self.db_conn.commit()
        # Refreshing UI components and updating the parking spot status
        self.is_occupied = False
        self.setStyleSheet("background-color: green; color: white; font-weight: bold; font-size: 14px;")
        self.setText(f'ადგილი {self.id}')
        self.refresh_earnings()
        self.refresh_spot_status()

    def refresh_spot_status(self):

        car_info = self.db_conn.execute(
            'SELECT ავტომობილის_მარკა, ავტომობილის_მოდელი, vin_კოდი FROM parking WHERE პარკინგის_ადგილი = ? AND გამოსვლა IS NULL',
            (self.id,)).fetchone()
        if car_info:
            self.is_occupied = True
            self.ავტომობილის_მარკა, self.ავტომობილის_მოდელი, self.vin_კოდი = car_info
            # Updated styles for occupied spots
            self.setStyleSheet("""
                background-color: #D22F2F; /* Darker red for occupied spot */
                color: white;
                font-weight: 200; /* Extra bold font */
                font-size: 20px; /* Increased font size for better visibility */
                padding: 20px; /* Add more padding for a larger button */
                border-radius: 15px; /* Rounded corners for a smoother look */
                min-height: 40px; /* Minimum button height */
                min-width: 40px; /* Minimum button width */
            """)
            self.setText(f'ადგილი {self.id}')
        else:
            self.is_occupied = False
            # Updated styles for unoccupied spots
            self.setStyleSheet("""
                background-color: #004225; /* Darker green for available spot */
                color: white;
                font-weight: 200; /* Extra bold font */
                font-size: 20px; /* Consistent increased font size */
                padding: 20px; /* Consistent padding with occupied spots */
                border-radius: 15px; /* Consistent rounded corners */
                min-height: 40px; /* Consistent minimum button height */
                min-width: 40px; /* Consistent minimum button width */
            """)
            self.setText(f'ადგილი {self.id}')

    @staticmethod
    def get_today_earnings():
        today = datetime.now().date()
        conn = sqlite3.connect('parking_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(ჯამში_გადახდილი) FROM parking_history WHERE DATE(გამოსვლა) = ?", (today,))
        today_earnings = cursor.fetchone()[0]
        conn.close()
        return today_earnings if today_earnings else 0


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

    @staticmethod
    def read_credentials():
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

        MainApplication.init_db()  # Initialize the database
        self.init_ui()  # Initialize the UI

    def init_ui(self):
        # Setting up the window title and stylesheet
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

        # Main layout setup
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Top layout setup for earnings label and minimize/exit buttons
        self.top_layout = QtWidgets.QHBoxLayout()
        # Modify the alignment of the earnings label to be centered
        self.earnings_label = QtWidgets.QLabel(
            f"\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tდღის ნავაჭრი: {self.get_today_earnings()} ლარი")
        self.earnings_label.setAlignment(QtCore.Qt.AlignCenter)  # Align the label in the center

        self.minimize_button = CustomButton("ჩაკეცვა")
        self.exit_button = CustomButton("გამორთვა")
        self.top_layout.addWidget(self.earnings_label)
        self.top_layout.addStretch(1)  # This pushes the following items to the right
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
        rows, cols = (num_buttons, 8)  # Adjust based on your needs
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

    def confirm_exit(self):
        reply = QtWidgets.QMessageBox.question(self, 'დაზუსტება',
                                               "დარწმუნებული ხარ?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.instance().quit()

    def get_today_earnings(self):

        today = datetime.now().date()
        conn = sqlite3.connect('parking_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(ჯამში_გადახდილი) FROM parking_history WHERE DATE(გამოსვლა) = ?", (today,))
        today_earnings = cursor.fetchone()[0]
        conn.close()
        return today_earnings if today_earnings else 0


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApplication()
    window.showFullScreen()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
