#!/usr/bin/env python

import publicClient
import numpy as np
import pandas as pd
import time
import os
import math
import sys

def separate_buy_and_sell(trade):
    sell = [x for x in trade if x['side'] == 'sell']
    buy = [x for x in trade if x['side'] == 'buy']
    return [sell, buy]

def get_top50_order_book(public_client, product_id):
    """
    :param public_client: 
    :param product_id: btc / eth / ...
    :return: 
    """
    orderbook = public_client.get_product_order_book(product_id, level=2)
    bids = np.array(orderbook["bids"])
    bids = bids.astype(np.float).tolist()
    asks = np.array(orderbook["asks"])
    asks = asks.astype(np.float).tolist()
    return {"bids": bids, "asks": asks}

def get_trade_history(public_client, product_id):
    """
    :param public_client: 
    :param product_id: 
    :return: sell_history and buy_history
    """
    trade_history = public_client.get_product_trades(product_id=product_id)
    [sell, buy] = separate_buy_and_sell(trade_history)
    sell_price = [x['price'] for x in sell]
    sell_size = [x['size'] for x in sell]
    buy_price = [x['price'] for x in buy]
    buy_size = [x['size'] for x in buy]

    sell_history = np.transpose(np.stack((sell_price, sell_size))).astype(np.float).tolist()
    buy_history = np.transpose(np.stack((buy_price, buy_size))).astype(np.float).tolist()
    return [sell_history, buy_history]

def merge_trade_data(public_client, product_id):
    orderbook = get_top50_order_book(public_client, product_id)
    bid = orderbook['bids']
    ask = orderbook['asks']
    [sell_history, buy_history] = get_trade_history(public_client, product_id)
    return [bid, ask, sell_history, buy_history]

def export_trade_data(public_client, product_id):
    epoch = public_client.get_time()['epoch']
    price = float(public_client.get_product_ticker(product_id)['price'])
    [bid, ask, sell_history, buy_history] = merge_trade_data(public_client, product_id)
    data = {'time': epoch, 'price': price,
            'bid': bid, 'ask': ask,
            'sell_history': sell_history, 'buy_history': buy_history}
    data = pd.DataFrame([data], columns = ["time", "price", "bid", "ask", "sell_history", "buy_history"])
    return data

def wait_until_next_data_collection(interval):
    current_time = time.time()
    next_time = math.ceil(current_time / interval) * interval
    time.sleep(next_time - current_time)

def main():
    btc = "BTC-USD"
    disk_write_interval = 60
    data_collection_interval = 2

    data_directory = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    public_client = publicClient.PublicClient()
    while(True):
        df =  pd.DataFrame([], columns = ["time", "price", "bid", "ask", "sell_history", "buy_history"])
        collection_period_start = time.time()
        datapoints = 0
        
        while time.time() < collection_period_start + disk_write_interval:
            wait_until_next_data_collection(data_collection_interval)
            try:
                data = export_trade_data(public_client, btc)
                df = df.append(data, ignore_index=True)
                datapoints += 1
            except:
                print("Error downloading data:", sys.exc_info()[0])
                pass

        with open('data/btc.csv', 'a') as f:
            df.to_csv(f, index = False, header = False)

        print("recorded", datapoints, "datapoints")

main()

