import talib
import time
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
import pandas as pd

from config import api_key, secret_key
from bybit import Bybit_api


def sleep_to_next_min():
    """
    Function to calculate and sleep until the start of the next minute
    """
    time_to_sleep = 60 - time.time() % 60 + 2
    print('sleep', time_to_sleep)
    time.sleep(time_to_sleep)


if __name__ == '__main__':
    # Initialize the Bybit API client
    client = Bybit_api(api_key, secret_key, futures=True)

    while True:
        # Wait for the start of the next minute
        sleep_to_next_min()

        # Get the latest 100 klines for ETHUSDT
        klines = client.get_klines(symbol="ETHUSDT", interval="1", limit=100)
        klines = klines['result']['list']

        # Extract close prices from klines
        close_prices = [float(i[4]) for i in klines]
        close_prices_np = np.array(close_prices)
        close_prices_np = close_prices_np[::-1]

        # Calculate Bollinger Bands
        upper_band, middle_band, lower_band = talib.BBANDS(close_prices_np, timeperiod=20, nbdevup=2, nbdevdn=2,
                                                           matype=0)

        # Create a DataFrame for Bollinger Bands
        bollinger_df = pd.DataFrame({
            'Close': close_prices_np,
            'upper_band': upper_band,
            'middle_band': middle_band,
            'lower_band': lower_band
        })

        # print(bollinger_df.tail())
        #
        # # Plot Bollinger Bands
        # plt.figure(figsize=(12, 6))
        # plt.plot(close_prices_np, label='Close')
        # plt.plot(upper_band, label='upper_band', linestyle='--')
        # plt.plot(middle_band, label='middle_band', linestyle='--')
        # plt.plot(lower_band, label='lower_band', linestyle='--')
        # plt.title('Bollinger Bands for ETHUSDT')
        # plt.legend()
        # plt.show()

        # Get the latest price and Bollinger Bands values
        price = bollinger_df.iloc[-1]['Close']
        ub = bollinger_df.iloc[-1]['upper_band']
        mb = bollinger_df.iloc[-1]['middle_band']
        lb = bollinger_df.iloc[-1]['lower_band']

        print('Price:', price)
        print('Upper Band:', ub)
        print('Middle Band:', mb)
        print('Lower Band:', lb)

        # Trading strategy based on Bollinger Bands
        if price > ub:
            print('Sell')
            client.post_market_order(symbol="ETHUSDT", side="Sell", qnt=1)
        elif price < lb:
            print('Buy')
            client.post_market_order(symbol="ETHUSDT", side="Buy", qnt=1)
        else:
            print('Hold')