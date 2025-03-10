from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem, QLabel, QSizePolicy, QFrame, QLineEdit, QPushButton, QMessageBox, QSpinBox,QStackedWidget
from PyQt5 import uic
from PyQt5.QtCore import QSize, pyqtSignal
import datetime
import os
from clipboard import ImageViewer

class CustomListElement(QWidget):
    """Custom list item widget for displaying trade information"""
    def __init__(self, parent, trade_id, pair, position, status, risk, reward,date) -> None:
        super().__init__(parent)
        uic.loadUi("./ui/listelement.ui", self)
        self.trade_id = trade_id
        self.pair = pair
        self.position = position
        self.status = status
        self.risk = risk
        self.reward = reward
        self.date = date
        
        self.init_ui()
    
    def init_ui(self):
        self.pair_label : QLabel = self.findChild(QLabel, "pair")
        self.position_label : QLabel = self.findChild(QLabel, "position")
        self.status_label : QLabel = self.findChild(QLabel, "status")
        self.date_label : QLabel = self.findChild(QLabel, "date")


        self.pair_label.setText(self.pair)
        self.status_label.setText(self.status)
        bg_color = "#f0bcb9" if self.position == "sell" else "#bcf0b9"
        self.position_label.setStyleSheet(f"background-color: {bg_color}; color: #ffffff;font-weight:bold;")
        self.position_label.setText(self.position)
        current_data = datetime.datetime.now()
        temp = current_data - self.date

        if temp.days == 0:
            date_text = "Today"
        elif temp.days == 1:
            date_text = "Yesterday"
        else:
            date_text = f"{temp.days}d"

        self.date_label.setText(date_text)



class TradingUI(QWidget):
    """Main trading interface that displays account information and trade management"""
    # Define signals for communication with controllers
    place_trade_signal = pyqtSignal(str, float, int, str)  # pair, risk, reward, position
    close_trade_signal = pyqtSignal(dict)  # trade_id, closed_at, result
    delete_trade_signal = pyqtSignal(int)  # trade_id
    on_selected_signal = pyqtSignal(int)

    
    def __init__(self, parent) -> None:
        super().__init__(parent)
        uic.loadUi("./ui/trading_track_ui.ui", self)
        self.isPaire_valid = False
        self.isRisk_valid = False
        self.selected_item = None
        self.init_ui()
        self.init_controls()
        self.setup_connections()
        self.check_valid()
    
    def init_ui(self):
        """Initialize UI components"""
        self.acount_name : QLabel = self.findChild(QLabel, "account_name")
        self.balance : QLabel = self.findChild(QLabel, "balance")
        self.winrate : QLabel = self.findChild(QLabel, "winrate")
        self.quit_button : QPushButton = self.findChild(QPushButton,"quit")

        self.pair : QLineEdit = self.findChild(QLineEdit, "pair")
        self.risk : QLineEdit = self.findChild(QLineEdit, "risk")

        self.buy_button : QPushButton = self.findChild(QPushButton, "buy")
        self.sell_button : QPushButton = self.findChild(QPushButton, "sell")

        self.reward : QSpinBox = self.findChild(QSpinBox, "reward")

        self.list_trades : QListWidget = self.findChild(QListWidget, "listWidget")
        self.list_trades.clear()
        
        # Set the list widget to adjust its size policy
        self.list_trades.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.stacked : QStackedWidget = self.findChild(QStackedWidget, "sta")
        self.stacked.setCurrentIndex(0)
        
        self.label_pair : QLabel = self.findChild(QLabel, "label_pair")
        self.label_position : QLabel = self.findChild(QLabel, "position")
        
        # Find trade management buttons
        self.TP_button : QPushButton = self.findChild(QPushButton, "TP_button")
        self.SL_button : QPushButton = self.findChild(QPushButton, "SL_button")
        self.TP_mul : QSpinBox = self.findChild(QSpinBox, "TP_mul")
        self.SL_mul : QSpinBox = self.findChild(QSpinBox, "SL_mul")
        self.manual_close : QPushButton = self.findChild(QPushButton, "manual_close")
        self.manual_close_value : QLineEdit = self.findChild(QLineEdit, "manual_close_value")
        self.import_wi :QWidget = self.findChild(QWidget,"widget_25")
        self.image_view = ImageViewer()
        self.import_wi.layout().addWidget(self.image_view)

        self.delete_trade : QPushButton = self.findChild(QPushButton, "remove")

    def init_controls(self):
        """Initialize default values for controls"""
        self.reward.setRange(1, 10)
        self.reward.setValue(2)  # Default 1:2 risk/reward
        
    def setup_connections(self):
        """Connect UI signals to handlers"""
        self.list_trades.itemClicked.connect(self.on_selected)
        self.pair.textChanged.connect(self.on_pair_changed)
        self.risk.textChanged.connect(self.on_risk_changed)
        
        # Connect trading buttons
        self.buy_button.clicked.connect(self.on_buy_clicked)
        self.sell_button.clicked.connect(self.on_sell_clicked)
        
        # Connect trade management buttons
        self.TP_button.clicked.connect(self.on_TP_clicked)
        self.SL_button.clicked.connect(self.on_SL_clicked)
        self.delete_trade.clicked.connect(self.on_delete_trade)
        self.manual_close_value.textChanged.connect(self.on_manual_close_change)
        self.manual_close.clicked.connect(self.on_manual_close_clicked)

    def on_manual_close_change(self):
        """Handle manual close value changes"""
        try:
            float(self.manual_close_value.text())
            self.manual_close.setEnabled(True)
        except:
            self.manual_close.setEnabled(False)

    def on_pair_changed(self, text):
        """Validate pair input"""
        self.isPaire_valid = len(text) > 0
        self.check_valid()
    
    def on_risk_changed(self, text):
        """Validate risk input"""
        try:
            if text == "":
                self.isRisk_valid = False
            risk = float(text)
            self.isRisk_valid = risk > 0
        except:
            self.isRisk_valid = False
        self.check_valid()
    
    def check_valid(self):
        """Check if inputs are valid and enable/disable buttons accordingly"""
        if self.isPaire_valid and self.isRisk_valid:
            self.enable_button_position()
            return
        else:
            self.disable_button_position()
            return


    def disable_button_position(self):
        """Disable buy/sell buttons"""
        self.buy_button.setEnabled(False)
        self.sell_button.setEnabled(False)
    
    def enable_button_position(self):
        """Enable buy/sell buttons"""
        self.buy_button.setEnabled(True)
        self.sell_button.setEnabled(True)
        
    def update_profile_display(self, name, balance, winrate):
        """Update account information display"""
        self.acount_name.setText(name)
        self.balance.setText(f"${balance:.2f}")
        self.winrate.setText(f"{winrate:.1f}%")

    def on_buy_clicked(self):
        """Handle buy button click"""
        try:
            if not self.isPaire_valid or not self.isRisk_valid:
                return
            pair = self.pair.text()
            risk_text = self.risk.text()
            risk = float(risk_text)
            reward = self.reward.value()
            
            # Emit signal for controller to handle
            self.place_trade_signal.emit(pair, risk, reward, "buy")
            
            # Clear inputs
            self.pair.setText("")
            self.risk.setText("")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"akato le: {str(e)}")

    def on_sell_clicked(self):
        """Handle sell button click"""
        try:
            if not self.isPaire_valid or not self.isRisk_valid:
                return
            pair = self.pair.text()
            risk = float(self.risk.text())
            reward = self.reward.value()
            
            # Emit signal for controller to handle
            self.place_trade_signal.emit(pair, risk, reward, "sell")
            
            # Clear inputs
            self.pair.clear()
            self.risk.clear()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not place trade: {str(e)}")

    def set_images(self, trade_id):
        image_before = self.image_view.zone1.image_label.original_pixmap
        image_after = self.image_view.zone2.image_label.original_pixmap

        pathname_before = None
        pathname_after = None

        if image_before is not None:
            pathname_before = f"./assets/{self.acount_name.text().replace(' ', '')}_{trade_id}_before.jpg"
            image_before.save(pathname_before, "JPG")

        if image_after is not None:
            pathname_after = f"./assets/{self.acount_name.text().replace(' ', '')}_{trade_id}_after.jpg"
            image_after.save(pathname_after, "JPG")
        
        return pathname_before,pathname_after



    def on_TP_clicked(self):
        """Close selected trade as win"""
        if self.selected_item:
            custom_widget = self.list_trades.itemWidget(self.selected_item)
            close_at = self.TP_mul.value() * float(custom_widget.risk)
            trade_id = custom_widget.trade_id
            before,after = self.set_images(trade_id)

            trade = {
                "trade_id":trade_id,
                "closed_at":close_at,
                "result":"TP",
                "before":before,
                "after":after
            }
            # Emit signal for controller to handle

            self.close_trade_signal.emit(trade)

    def on_SL_clicked(self):
        """Close selected trade as loss"""
        if self.selected_item:
            custom_widget = self.list_trades.itemWidget(self.selected_item)
            close_at = self.SL_mul.value() * float(custom_widget.risk)
            trade_id = custom_widget.trade_id
            before,after = self.set_images(trade_id)
            
            trade = {
                "trade_id":trade_id,
                "close_at":close_at,
                "result":"SL",
                "before":before,
                "after":after
            }
            # Emit signal for controller to handle

            self.close_trade_signal.emit(trade)

    def on_manual_close_clicked(self):
        """Handle manual trade close"""
        if self.selected_item:
            custom_widget = self.list_trades.itemWidget(self.selected_item)
            close_at = float(self.manual_close_value.text())
            trade_id = custom_widget.trade_id
            before,after = self.set_images(trade_id)
            
            trade = {
                "trade_id":trade_id,
                "close_at":close_at,
                "result":"MANUAL",
                "before":before,
                "after":after
            }
            # Emit signal for controller to handle

            self.close_trade_signal.emit(trade)

    def on_delete_trade(self):
        """Handle delete trade button click"""
        if self.selected_item:
            custom_widget = self.list_trades.itemWidget(self.selected_item)
            self.image_view.reset_images()
            # Emit signal for controller to handle
            self.delete_trade_signal.emit(custom_widget.trade_id)

    def on_selected(self, item : QListWidgetItem):
        """Handle trade selection in list"""
        self.image_view.reset_images()
        self.manual_close.setEnabled(False)
        if not self.selected_item == item:
            self.stacked.setCurrentIndex(2)
            self.selected_item = item
            
        temp : CustomListElement = self.list_trades.itemWidget(item)
        self.label_pair.setText(temp.pair)
        self.label_position.setText(temp.position)
        self.TP_mul.setRange(0, temp.reward)
        self.TP_mul.setValue(temp.reward)
        self.SL_mul.setRange(-1, temp.reward)  # Default to 1x for stop loss
        self.SL_mul.setValue(-1)
        self.on_selected_signal.emit(temp.trade_id)
       
        # Only enable win/loss buttons if the trade is open
        is_open = "OPEN" in temp.status
        self.TP_button.setEnabled(is_open)
        self.SL_button.setEnabled(is_open)
        self.manual_close.setEnabled(False)
        self.manual_close_value.clear()

    def clear_trades(self):
        """Clear all trades from the list"""
        self.stacked.setCurrentIndex(0)
        self.list_trades.clear()
        self.selected_item = None
        self.stacked.setCurrentIndex(0)

    def add_trade(self, trade_id, pair, position, status, risk, reward,date):
        """Add a trade to the list"""
        custom_widget = CustomListElement(None, trade_id, pair, position, status, risk, reward,date)
        
        # Create a QListWidgetItem
        item = QListWidgetItem(self.list_trades)
        item.setSizeHint(QSize(0, 50))
        
        # Set the custom widget as the item widget
        self.list_trades.setItemWidget(item, custom_widget)
        
        # Force the list to update its layout
        self.list_trades.update()
        
    def update_trade_status(self, trade_id, new_status):
        """Update the status of a trade in the list"""
        for i in range(self.list_trades.count()):
            item = self.list_trades.item(i)
            widget = self.list_trades.itemWidget(item)
            CustomListElement().lab
            if widget.trade_id == trade_id:
                widget.status = new_status
                widget.status_label.setText(new_status)
                if self.selected_item == item:
                    self.stacked.setCurrentIndex(0)
                    self.selected_item = None
                break

    def remove_trade(self, trade_id):
        """Remove a trade from the list"""
        for i in range(self.list_trades.count()):
            item = self.list_trades.item(i)
            widget = self.list_trades.itemWidget(item)
            if widget.trade_id == trade_id:
                self.list_trades.takeItem(i)
                if self.selected_item == item:
                    self.stacked.setCurrentIndex(0)
                    self.selected_item = None
                break

# main.py - Application entry point
