import random
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

csv_folder = Path('../pnl-test/csv')


def add(x, y):
    return x + y


def subtract(x, y):
    return x - y


def random_num(
    num_type: str, 
    num_a, 
    num_b
):
    if num_type == 'int':
        return random.randint(num_a, num_b)
    elif num_type == 'float':
        return random.uniform(num_a, num_b)


def random_function(x, y):
    func = random.choice([add, subtract])
    return func(x, y)


def gen_data(
    start: datetime, 
    end: datetime,
    token: str,
    base_price,
    num_type: str,
    num_a,
    num_b
) -> pd.DataFrame:

    time_list = []
    while start <= end:
        rand_price = random_function(base_price, random_num(num_type, num_a, num_b))
        temp_list = [token, start, rand_price]
        time_list.append(temp_list)
        start += timedelta(minutes=5)
        
    return time_list


def gen_random_history_price_48h_5m(
    list_token_info_dict: list,
    current_time: datetime,
):
    rounded_minutes = (current_time.minute // 5) * 5

    start_time = datetime(current_time.year, current_time.month, current_time.day, current_time.hour, rounded_minutes) - timedelta(days=1)
    end_time = start_time + timedelta(days=1)
    
    list_time = []
    for token in list_token_info_dict:
        data = gen_data(
            start_time, 
            end_time, 
            token.get('symbol'), 
            token.get('base_price'), 
            token.get('type'), 
            token.get('num_a'), 
            token.get('num_b')
        )
        
        list_time.append(data)

    list_time = list_time[0] + list_time[1]
    
    return pd.DataFrame(list_time, columns=['token', 'time', 'price']).sort_values(by='time').to_csv(csv_folder/'sample_token_price_history.csv', index=False)
        
  
if __name__ == '__main__':

    list_token = [
        {
            'symbol': 'WBNB',
            'base_price': 300,
            'type': 'int',
            'num_a': 5,
            'num_b': 15,
        },
        {
            'symbol': 'ZOON',
            'base_price': 0.0007,
            'type': 'float',
            'num_a': 0.00001,
            'num_b': 0.0001,
        }
    ]
    
    gen_random_history_price_48h_5m(list_token, datetime.now() - timedelta(days=1))
