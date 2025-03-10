from PyQt5.QtWidgets import (QWidget, QPushButton, QListWidget, QListWidgetItem, 
                            QLabel, QVBoxLayout, QHBoxLayout, QDialog, QLineEdit,
                            QMessageBox, QFrame, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QFont, QColor
from PyQt5 import uic
import json
import pandas as pd
from model import TradingProfile
import os

class AccountItem(QWidget):
    """Custom widget for account items in the list widget"""
    deleteClicked = pyqtSignal(QWidget)
    
    def __init__(self, account_name, balance, parent_item=None):
        super().__init__()
        self.account_name = account_name
        self.balance = balance
        self.parent_item = parent_item
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Account info section
        info_layout = QVBoxLayout()
        
        # Account name
        self.name_label = QLabel(account_name)
        self.name_label.setFont(QFont("Arial", 12, QFont.Bold))

        # Set background color to non
        self.name_label.setStyleSheet("background-color: none;color: black")
        info_layout.addWidget(self.name_label)
        
        # Account balance
        self.balance_label = QLabel(f"Balance: ${balance:.2f}")
        self.balance_label.setFont(QFont("Arial", 10))
        self.balance_label.setStyleSheet("background-color: none;color : black")
        info_layout.addWidget(self.balance_label)
        
        layout.addLayout(info_layout, 1)  # Stretch factor 1
        
        # Delete button (hidden by default)
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.delete_button.setVisible(False)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        layout.addWidget(self.delete_button, 0)  # Stretch factor 0
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D30;
                color: #FFFFFF;
                border-radius: 4px;
            }
        """)
        
    def enterEvent(self, event):
        """Show delete button when mouse enters widget"""
        self.delete_button.setVisible(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Hide delete button when mouse leaves widget"""
        self.delete_button.setVisible(False)
        super().leaveEvent(event)
        
    def on_delete_clicked(self):
        """Emit signal when delete button is clicked"""
        if self.parent_item:
            self.deleteClicked.emit(self)


class CreateAccountDialog(QDialog):
    """Dialog for creating a new account"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Account")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Account name input
        layout.addWidget(QLabel("Account Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter account name")
        self.name_input.setText(f"Account {self.generate_default_name()}")
        layout.addWidget(self.name_input)
        
        # Starting balance input
        layout.addWidget(QLabel("Starting Balance:"))
        self.balance_input = QLineEdit()
        self.balance_input.setPlaceholderText("Enter starting balance")
        self.balance_input.setText("1000.00")
        layout.addWidget(self.balance_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.create_button = QPushButton("Create Account")
        self.create_button.clicked.connect(self.validate_and_accept)
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D30;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                background-color: #1E1E1E;
                color: #FFFFFF;
                selection-background-color: #3E3E42;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
        """)
    
    def generate_default_name(self):
        """Generate a default account name"""
        import random
        return random.randint(1000, 9999)
    
    def validate_and_accept(self):
        """Validate inputs before accepting"""
        name = self.name_input.text().strip()
        balance_text = self.balance_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter an account name")
            return
        
        try:
            balance = float(balance_text)
            if balance < 0:
                raise ValueError("Balance cannot be negative")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid positive number for balance")
            return
        
        self.accept()
    
    def get_account_data(self):
        """Return account name and balance"""
        return {
            "name": self.name_input.text().strip(),
            "balance": float(self.balance_input.text().strip())
        }



class LoginWidget(QWidget):
    """Widget for account login and management"""
    
    loginSuccessful = pyqtSignal(dict)  # Signal with account data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.accounts_file = "./database/users/profile.xlsx"
        self.accounts: pd.DataFrame
        uic.loadUi("ui/login.ui", self)
        self.init_ui()
        self.load_accounts()
        self.populate_accounts_list()
    
    def init_ui(self):
        """Initialize the UI components"""
        # Title
        self.title = self.findChild(QLabel, "title")
        # Accounts list
        self.accounts_list = self.findChild(QListWidget, "accounts_list")
        # Buttons
        self.login_button = self.findChild(QPushButton, "login_button")
        self.create_account_button = self.findChild(QPushButton, "create_account_button")
                
        # Initialize the controls
        self.init_controls()
    
    def init_controls(self):
        """Initialize the UI controls"""
        self.login_button.setEnabled(False)
        self.title.setFont(QFont("Arial", 16, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.accounts_list.setMinimumHeight(250)
        self.accounts_list.setSpacing(5)
        
        # Connect signals
        self.accounts_list.itemClicked.connect(self.on_account_selected)
        self.accounts_list.itemDoubleClicked.connect(self.login_selected_account)
        self.login_button.clicked.connect(self.login_selected_account)
        self.create_account_button.clicked.connect(self.show_create_account_dialog)
        
        # Style the create account button
        self.create_account_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D30;
                color: #FFFFFF;
            }
            
            QListWidget {
                background-color: #1E1E1E;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                outline: none;
            }
            
            QListWidget::item {
                border-bottom: 1px solid #3E3E42;
                padding: 5px;
            }
            
            QListWidget::item:selected {
                background-color: #0078D7;
            }
            
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #1C97EA;
            }
            
            QPushButton:disabled {
                background-color: #3E3E42;
                color: #9D9D9D;
            }
        """)

    def load_accounts(self):
        """Load accounts from xlsx file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.accounts_file), exist_ok=True)
            
            if os.path.exists(self.accounts_file):
                df = pd.read_excel(self.accounts_file)
                self.accounts = df
            else:
                self.accounts = pd.DataFrame()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load accounts: {str(e)}")
            self.accounts = pd.DataFrame()

    def populate_accounts_list(self):
        """Fill the list widget with account items"""
        self.accounts_list.clear()
        
        if os.path.exists(self.accounts_file):
            self.accounts = pd.read_excel(self.accounts_file)
            for index, row in self.accounts.iterrows():
                self.add_account_to_list(row)
    
    def add_account_to_list(self, account):
        """Add a single account to the list widget"""
        item = QListWidgetItem()
        account_widget = AccountItem(account["name"], account["balance"], item)
        
        # Connect delete signal
        account_widget.deleteClicked.connect(self.delete_account)
        
        # Set size hint for proper display
        item.setSizeHint(QSize(self.accounts_list.width(), 70))
        
        # Add to list
        self.accounts_list.addItem(item)
        self.accounts_list.setItemWidget(item, account_widget)
    
    def on_account_selected(self, item):
        """Enable login button when an account is selected"""
        self.login_button.setEnabled(True)
    
    def show_create_account_dialog(self):
        """Show dialog for creating a new account"""
        dialog = CreateAccountDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            account_data = dialog.get_account_data()
        else:
            return
            
        name: str = account_data["name"]
        balance = account_data["balance"]

        import re

        if not self.accounts.empty:
            # Vérifier si le nom existe déjà
            pattern = f"^{re.escape(name)}(\_[0-9]+)?$"
            if self.accounts["name"].str.contains(pattern, regex=True).any():
                # Extraire les noms existants similaires
                existing_names = self.accounts["name"][self.accounts["name"].str.startswith(name)]
                suffixes = [int(re.search(r"_(\d+)$", n).group(1)) for n in existing_names if re.search(r"_(\d+)$", n)]
                
                # Déterminer le prochain suffixe disponible
                next_suffix = max(suffixes) + 1 if suffixes else 1
                name = f"{name}_{next_suffix}"
        # Add new account to list
        profile = TradingProfile()
        profile.balance = balance
        profile.create_account(name)


        self.populate_accounts_list()        
        # Select the newly created account
        self.accounts_list.setCurrentRow(self.accounts_list.count() - 1)
        self.login_button.setEnabled(True)
    
    def login_selected_account(self):
        """Login with the currently selected account"""
        current_item: QListWidgetItem = self.accounts_list.currentItem()
        item_widget = self.accounts_list.itemWidget(current_item)

        if current_item:
            account_name = item_widget.account_name  # Suppose que AccountItem stocke le nom dans `account_name`
            selected_row = self.accounts.loc[self.accounts["name"] == account_name]

            if not selected_row.empty:
                account_data = selected_row.iloc[0].to_dict()  # Convertir la première ligne en dictionnaire
                self.loginSuccessful.emit(account_data)
    
    def delete_account(self, AccountItem: AccountItem):
        """Delete an account from the list"""
        account_name = AccountItem.account_name
        item = AccountItem.parent_item
        row = self.accounts_list.row(item)

        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete account '{account_name}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from list and data
            self.accounts_list.takeItem(row)
            if account_name in self.accounts["name"].values:
                profile = TradingProfile()
                profile.load_account(account_name)
                profile.delete_account()
                self.accounts = self.accounts[self.accounts["name"] != account_name]

                self.populate_accounts_list()  # Rafraîchir la liste
            
            # Disable login button if no accounts left
            if self.accounts_list.count() == 0:
                self.login_button.setEnabled(False)
