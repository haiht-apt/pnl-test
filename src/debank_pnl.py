import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

class DebankPnLTest():

    def __init__(
        self,
        csv_folder: Path,
        current_time: datetime = datetime.now(),
        one_day_ago: datetime = datetime.now() - timedelta(days=1),
    ):
        self.csv_folder = csv_folder
        self.current_time = current_time
        self.one_day_ago = one_day_ago
        
        
    def __get_list_token_in_data(
        self,
        dataframe: pd.DataFrame
    ) -> list:
        
        data = dataframe.values.tolist()
        data = list(set(data))
        
        return data
    

    def __get_wallet_data_in_24h(
        self,
        dataframe: pd.DataFrame,
    ):
        
        list_token = self.__get_list_token_in_data(dataframe['token_symbol'])
        
        entry_price_dict = {}
        result_list = []
        for token in list_token:
            data = dataframe.query('token_symbol == @token')
            data_in = data.query('transfer_method == "in"')
            data_out = data.query('transfer_method == "out"')

            # turn the number from positive to negative
            data_out['amount'] *= -1
            
            # merge two DF together when reversing the number in the previous line of code.
            data = pd.concat([data_in, data_out]).sort_values(by='time').reset_index(drop=True)
            
            # cum-sum from the beginning to the current time to calculate the wallet’s pnl as accurately as possible
            data['amount'] = data['amount'].cumsum()
            data['time'] = pd.to_datetime(data['time'])

            temp_df = data[data['time'].dt.date == (self.current_time - timedelta(days=2)).date()].sort_values(by='time')
            entry_price = temp_df.iloc[-1]['amount']

            data = data[(data['time'] >= self.one_day_ago) & (data['time'] <= self.current_time)]
            data = data[['wallet', 'token_symbol', 'time', 'amount']]
            entry_price_dict[token] = entry_price
            result_list.append(data.values.tolist())
            
        result_list = [item for sublist in result_list for item in sublist]
        return entry_price_dict, result_list 


    def pnl_data_24h(
        self, 
        token_history_file: str,
        wallet_transaction_file: str,
        result_file: str = 'pnl_data_24h.csv'
    ):
        
        token_history = pd.read_csv(self.csv_folder/token_history_file)    
        token_history['time'] = pd.to_datetime(token_history['time'])
        
        # return 2 options [entry_price_dict, result_list] => data[0] = entry_price_dict, data[1] = result_list
        data = self.__get_wallet_data_in_24h(pd.read_csv(self.csv_folder/wallet_transaction_file))

        transations_data = pd.DataFrame(data[1], columns=['wallet', 'token', 'time', 'amount'])
        entry_price = data[0]
        
        list_token = self.__get_list_token_in_data(transations_data['token'])

        temp_list = []
        for token in list_token:
            transaction = transations_data.query('token == @token').sort_values(by='time')
            token_price = token_history.query('token == @token').sort_values(by='time')
            
            # Merging two dataframes together.
            merged_df = pd.merge_asof(token_price, transaction, on='time', direction='backward')
            
            merged_df['amount'] = merged_df['amount'].ffill().fillna(entry_price.get(token))
            
            merged_df['total_usd'] = merged_df['amount'] * merged_df['price']
            merged_df = merged_df[['time', 'total_usd']]
            
            temp_list.append(merged_df)
        
        data = pd.concat(temp_list).groupby('time').sum().reset_index()
        
        temp_list = data['total_usd'].tolist()
        
        percent_list = [(((i / temp_list[0]) - 1 ) * 100) for i in temp_list]
        
        value_list = [(i - temp_list[0]) for i in temp_list]
        
        data['percent_change'] = pd.DataFrame(percent_list).round(decimals=4)
        data['value_change'] = pd.DataFrame(value_list)
        
        return data.to_csv(self.csv_folder/result_file, index=False)