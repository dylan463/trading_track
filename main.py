import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QStackedWidget, QWidget,QGridLayout
from PyQt5 import uic
from model import TradingProfile
from controller import TradingController
from ui import TradingUI
from login import LoginWidget



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)
        
        layout = QVBoxLayout()
        self.centralWidget().setLayout(layout)
        # create a layout for the central widget
        self.stacked = QStackedWidget()
        
        # Create model, view, and controller
        self.profile_model = TradingProfile()

        widget_login = QWidget()
        lay2 = QGridLayout()
        widget_login.setLayout(lay2)
        widget_login.layout().setContentsMargins(0, 0, 0, 0)
        self.stacked.addWidget(widget_login)
        self.login_ui = LoginWidget(widget_login)
        self.login_ui.loginSuccessful.connect(lambda account : self.setup_account(account["name"]))

        lay2.addWidget(self.login_ui)

        widget_trade = QWidget()
        widget_trade.setStyleSheet("background-color: #f0f0f0;")  # Bleu
        lay1 = QVBoxLayout()
        widget_trade.setLayout(lay1)
        widget_trade.layout().setContentsMargins(0, 0, 0, 0)
        self.stacked.addWidget(widget_trade)
        self.trading_ui = TradingUI(widget_trade)
        lay1.addWidget(self.trading_ui)
        
        self.stacked.setCurrentIndex(0)

        self.controller = TradingController(self.profile_model, self.trading_ui)
        self.controller.return_signal.connect(self.init_ui)
        
        # Add UI to main window
        self.centralWidget().layout().addWidget(self.stacked)

    def init_ui(self):
        self.stacked.setCurrentIndex(0)

    def setup_account(self,acount_name):
        self.controller.setup_account(acount_name)
        self.stacked.setCurrentIndex(1)
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())