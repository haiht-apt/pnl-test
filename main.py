from src.debank_pnl import DebankPnLTest
from datetime import datetime, timedelta
from pathlib import Path

csv_folder_path = Path('../pnl-test/csv')

debank_pnl_test = DebankPnLTest(
    csv_folder=csv_folder_path,
    current_time=datetime.now() - timedelta(days=1),
    one_day_ago=datetime.now() - timedelta(days=2)
)

if __name__ == '__main__':
    
    debank_pnl_test.pnl_data_24h(
        token_history_file='sample_token_price_history.csv',
        wallet_transaction_file='sample_wallet_transaction_data.csv',
    )