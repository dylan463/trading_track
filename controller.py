from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QListWidgetItem
import os
from model import TradingProfile
from ui import TradingUI
import datetime
import pandas as pd

class TradingController:
    """Controller that manages communication between model and views"""
    
    def __init__(self, profile_model : TradingProfile, trading_ui : TradingUI) -> None:
        self.profile = profile_model
        self.ui = trading_ui
        self.return_signal = self.ui.quit_button.clicked
        
        # Connect UI signals to controller methods
        self.ui.place_trade_signal.connect(self.handle_place_trade)
        self.ui.close_trade_signal.connect(self.handle_close_trade)
        self.ui.delete_trade_signal.connect(self.handle_delete_trade)
        self.ui.on_selected_signal.connect(self.on_selected_item)
        self.ui.image_view.zone1.image_inserted.connect(self.save_image)
        self.ui.image_view.zone2.image_inserted.connect(self.save_image)

    def save_image(self):
        item : QListWidgetItem = self.ui.selected_item
        trade_id = self.ui.list_trades.itemWidget(item).trade_id
        before,after = self.ui.set_images(trade_id)
        df = pd.read_excel(self.profile.database_path)
        df["before"] = df["before"].astype(str)
        df["after"] = df["after"].astype(str)
        df.loc[df["trade_id"] == trade_id,"before"] = before
        df.loc[df["trade_id"] == trade_id,"after"] = after
        df.to_excel(self.profile.database_path,index = False)



    def on_selected_item(self,trade_id):
        df = pd.read_excel(self.profile.database_path)
        row = df[df["trade_id"] ==  trade_id].iloc[0]
        path_before = str(row["before"]) if pd.notna(row["before"]) else ""
        path_after = str(row["after"]) if pd.notna(row["after"]) else ""

        # Vérifie que les fichiers existent avant de les charger
        if path_before and os.path.exists(path_before):
            self.ui.image_view.zone1.load_image_from_file(path_before)
        else:
            print(f"Image 'before' introuvable: {path_before}")

        if path_after and os.path.exists(path_after):
            self.ui.image_view.zone2.load_image_from_file(path_after)
        else:
            print(f"Image 'after' introuvable: {path_after}")
    
    def setup_account(self, account_name):
        """Set up account - load or create if needed"""
        # Create account if it doesn't exist
        account_path = f"./database/{account_name}.xlsx"
        if not os.path.exists("./database"):
            os.makedirs("./database")
            
        if not os.path.exists(account_path):
            self.profile.create_account(account_name)
        
        # Load the account
        success = self.profile.load_account(account_name)
        if success:
            # Update UI with account info
            self.update_ui()
            # Load trades
            self.load_trades()
            return True
        else:
            QMessageBox.warning(None, "Error", f"Could not load account: {account_name}")
            return False
            
    def update_ui(self):
        """Update UI with current account information"""
        self.ui.update_profile_display(
            self.profile.name,
            self.profile.balance,
            self.profile.average_winrate
        )
    
    def load_trades(self):
        """Load trades from the account database and update UI"""
        try:
            self.ui.clear_trades()
            df = self.profile.get_trades()
            
            if not df.empty:
                for _, trade in df.iterrows():
                    status = trade['status']
                    if status == 'CLOSED' and trade['result'] is not None:
                        status = f"CLOSED ({trade['result']})"
                    
                    self.ui.add_trade(
                        trade['trade_id'],
                        trade['pair'],
                        trade['position'],
                        status,
                        trade['risk'],
                        trade['reward'],
                        trade["date"]
                    )
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not load trades: {str(e)}")
    
    def handle_place_trade(self, pair, risk, reward, position):
        """Handle place trade request from UI"""
        try:
            trade = self.profile.place_trade(
                self.profile.current_trade_id,
                pair,
                position,
                risk,
                reward,
                datetime.datetime.now()
            )
            
            # Add trade to UI
            self.ui.add_trade(
                trade['trade_id'],
                trade['pair'],
                trade['position'],
                trade['status'],
                trade['risk'],
                trade['reward'],
                trade["date"]
            )
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not place trade: {str(e)}")
    
    def handle_close_trade(self,trade : dict):
        """Handle close trade request from UI"""
        try:
            success = self.profile.close_trade(trade)
            if success:
                # Update the trade in UI
                status = f"CLOSED ({trade['result']})"
                self.ui.update_trade_status(trade["trade_id"], status)
                # Update account info
                self.update_ui()
            else:
                QMessageBox.warning(None, "Error", f"Could not close trade {trade['trade_id']}")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error closing trade: {str(e)}")
    
    def handle_delete_trade(self, trade_id):
        """Handle delete trade request from UI"""
        try:
            success = self.profile.delete_trade(trade_id)
            if success:
                # Remove the trade from UI
                self.ui.remove_trade(trade_id)
            else:
                QMessageBox.warning(None, "Error", f"Could not delete trade {trade_id}")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error deleting trade: {str(e)}")


