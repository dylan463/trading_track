import os
import pandas as pd

class TradingProfile:
    def __init__(self):
        self.name = ""
        self.balance = 10000
        self.average_winrate = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.database_path = ""
        self.current_trade_id = 1

    def place_trade(self, trade_id, pair, position, risk, reward,date):
        """Add a new trade to the account database"""
        try:
            # Try to load existing data
            df = pd.read_excel(self.database_path)
        except:
            # Create a new dataframe if file doesn't exist or is empty
            df = pd.DataFrame(columns=['trade_id', 'pair', 'position', 'risk', 'reward', 'status', 'result',"date","before","after"])
        
        # Add new trade
        new_trade = {
            'trade_id': trade_id,
            'pair': pair,
            'position': position,
            'risk': risk,
            'reward': reward,
            'status': 'OPEN',
            'result': None,
            'date': date,
            'before': None,
            'after':None
        }
        
        new_trade_df = pd.DataFrame([new_trade])
        for col in df.columns:
            if col in new_trade_df.columns:
                new_trade_df[col] = new_trade_df[col].astype(df[col].dtype)
        df = pd.concat([df, new_trade_df], ignore_index=True)
        df.to_excel(self.database_path, index=False)
        self.current_trade_id = trade_id + 1
        return new_trade

    def close_trade(self,trade):
        """Close an existing trade in the account database"""
        trade_id = trade["trade_id"]
        closed_at = trade["closed_at"]
        result = trade["result"]
        before = trade["before"]
        after = trade["after"]

        try:
            df = pd.read_excel(self.database_path)
            trade = df[df['trade_id'] == trade_id].iloc[0]
            if trade['status'] == 'OPEN':
                # Update trade status and result
                df.loc[df['trade_id'] == trade_id, 'status'] = 'CLOSED'
                
                # Either convert the column to object type first:
                df['result'] = df['result'].astype(object)
                df.loc[df['trade_id'] == trade_id, 'result'] = result

                # Then use appropriate columns based on data type
                if isinstance(result, (int, float)):
                    df.loc[df['trade_id'] == trade_id, 'result'] = result
                else:
                    df.loc[df['trade_id'] == trade_id, 'result_type'] = result
                
                # Update balance based on result
                self.balance += closed_at
                if closed_at > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1
                
                df.loc[df['trade_id'] == trade_id, 'closed_at'] = closed_at
                df.loc[df['trade_id'] == trade_id, 'balance'] = self.balance

                if not before ==  None:
                    if os.path.exists(before):
                        df.loc[df['trade_id'] == trade_id, 'before'] = before
                        
                if not after == None:
                    if os.path.exists(after):
                        df.loc[df['trade_id'] == trade_id, 'after'] = after
                    

                # Save changes
                df.to_excel(self.database_path, index=False)
                self.calculate_winrate()
                self.save_profile_data()
                return True
        except Exception as e:
            print(f"Error closing trade: {e}")
        return False

    def calculate_winrate(self):
        """Calculate the win rate percentage based on closed trades"""
        total_trades = self.winning_trades + self.losing_trades
        if total_trades > 0:
            self.average_winrate = (self.winning_trades / total_trades) * 100
        return self.average_winrate

    def show_balance(self):
        print(f'{self.name} has ${self.balance} in the account')
    
    def create_account(self, name):
        """Create a new trading account with default values"""
        # Make sure database directory exists
        if not os.path.exists("./database"):
            os.makedirs("./database")
        
        self.name = name
        self.winning_trades = 0
        self.losing_trades = 0
        self.average_winrate = 0
        self.current_trade_id = 1
        self.database_path = f'./database/{self.name}.xlsx'
        
        # Create empty trade dataframe
        trade_df = pd.DataFrame(columns=['trade_id', 'pair', 'position', 'risk', 'reward', 'status', 'result', 'closed_at', 'balance',"date","before","after"])
        trade_df.to_excel(self.database_path, index=False)
        
        # Save profile data
        self.save_profile_data()
        return True

    def save_profile_data(self):
        """Save profile metadata to a separate file"""
        # Create users directory if it doesn't exist
        if not os.path.exists("./database/users"):
            os.makedirs("./database/users")
            
        # Open the profile file
        profile_path = './database/users/profile.xlsx'
        try:
            if not os.path.exists(profile_path):
                profile_df = pd.DataFrame(columns=['name', 'balance', 'winning_trades', 'losing_trades', 'average_winrate'])
            else:
                profile_df = pd.read_excel(profile_path)

            # Check if we need to add the name column as index
            if 'name' not in profile_df.columns:
                profile_df['name'] = ''
                
            # Make a copy with name as normal column for manipulation
            profile_data = {'name': self.name, 'balance': self.balance, 
                        'winning_trades': self.winning_trades, 
                        'losing_trades': self.losing_trades, 
                        'average_winrate': self.average_winrate}
            
            # Check if profile exists
            if self.name in profile_df['name'].values:
                # Update existing profile
                idx = profile_df.index[profile_df['name'] == self.name].tolist()[0]
                for key, value in profile_data.items():
                    if key != 'name':  # Don't update the name
                        profile_df.at[idx, key] = value
            else:
                # Add new profile - using loc to avoid FutureWarning
                new_idx = len(profile_df)
                for key, value in profile_data.items():
                    profile_df.loc[new_idx, key] = value
            
            # Save profile data
            profile_df.to_excel(profile_path, index=False)
        except Exception as e:
            print(f"Error saving profile data: {e}")

    def load_account(self, name):
        """Load account data from Excel file"""
        self.name = name
        self.database_path = f'./database/{name}.xlsx'
        
        try:
            # Load profile metadata if it exists
            profile_path = './database/users/profile.xlsx'
            if os.path.exists(profile_path):
                profile_df = pd.read_excel(profile_path)
                # Find the profile by name
                profile_row = profile_df[profile_df['name'] == name]
                if not profile_row.empty:
                    self.balance = profile_row['balance'].iloc[0]
                    self.winning_trades = profile_row['winning_trades'].iloc[0]
                    self.losing_trades = profile_row['losing_trades'].iloc[0]
                    self.average_winrate = profile_row['average_winrate'].iloc[0]
            
            # Load trade data
            df = pd.read_excel(self.database_path)
            
            # Recalculate wins and losses in case profile data is corrupted
            wins = len(df[df['result'] == 'TP'])
            losses = len(df[df['result'] == 'SL'])
            if wins != self.winning_trades or losses != self.losing_trades:
                self.winning_trades = wins
                self.losing_trades = losses
                self.calculate_winrate()
            
            # Get next trade ID
            if not df.empty:
                self.current_trade_id = df['trade_id'].max() + 1
            else:
                self.current_trade_id = 1
                
            return True
        except Exception as e:
            print(f"Error loading account: {e}")
            return False

    def delete_account(self):
        """Delete account files"""
        try:
            if os.path.exists(self.database_path):
                os.remove(self.database_path)
            # Delete profile metadata
            profile_path = './database/users/profile.xlsx'
            if os.path.exists(profile_path):
                profile_df = pd.read_excel(profile_path)
                profile_df = profile_df[profile_df['name'] != self.name]
                profile_df.to_excel(profile_path, index=False)
            return True
        except Exception as e:
            print(f"Error deleting account: {e}")
            return False

    def delete_trade(self, trade_id):
        """Delete a trade from the account database"""
        try:
            df = pd.read_excel(self.database_path)
            df = df[df['trade_id'] != trade_id]
            df.to_excel(self.database_path, index=False)
            return True
        except Exception as e:
            print(f"Error deleting trade: {e}")
            return False

    def get_trades(self):
        """Get all trades for the current account"""
        try:
            return pd.read_excel(self.database_path)
        except Exception as e:
            print(f"Error getting trades: {e}")
            return pd.DataFrame()
