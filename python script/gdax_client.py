import grequests
import logging
import os
import glob
import json
import pandas as pd
import numpy as np
import threading


class GdaxClient:
    def __init__(self, api_url='https://api.gdax.com', product_id='BTC-USD', data_per_file=100, interval_seconds=5):
        self.url = api_url.rstrip('/')
        self.product_id = product_id
        self.logger = self.__set_logger__()
        # a list of requests to be sent to the server every given interval
        self.requests = self.__construct_urls__()
        self.interval_seconds = interval_seconds

        self.df = pd.DataFrame()
        self.data_dir = './data/'
        self.file_index = 0 # The first file will be 0, second will be 1, etc.
        self.data_index = 0
        self.data_per_file = data_per_file # number of records saved in per file
        self.__set_data_dir__()

    def __construct_urls__(self):
        """
        construct three urls, these three requests should be sent at the same time
        time_url: get current time
        tikcer_url: get current price
        order_book_url: get current order book
        :return:
        """
        time_url = self.url + '/time'
        ticker_url = self.url + '/products/{}/ticker'.format(self.product_id)
        order_book_url = self.url + '/products/{}/book?level=2'.format(self.product_id)
        return [grequests.get(i, timeout=1.0) for i in time_url, ticker_url, order_book_url]

    def __set_logger__(self):
        logger = logging.getLogger("gdax_client_logger")
        # create the log directory
        log_file = './logs/gdax_client_logger.log'
        if not os.path.exists(log_file):
            os.makedirs(os.path.dirname(log_file))

        hdlr = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        return logger

    def __set_data_dir__(self):
        # set the data directory
        if not os.path.exists(self.data_dir):
            os.makedirs(os.path.dirname(self.data_dir))
        # list existed data files and get index
        files = glob.glob(self.data_dir+'/'+self.product_id+'-*.csv')
        if not files:
            self.file_index = 0
        else:
            self.file_index = max([int(i.strip(".csv").split('-')[-1]) for i in files]) + 1
        file_columns = ['time_epoch', 'time_iso', 'bid', 'ask', 'price', 'volumne', 'bid_orders', 'ask_orders']
        self.df = pd.DataFrame(index=np.arange(0, self.data_per_file), columns=file_columns)

    def request_exception_handler(self, request, exception):
        self.logger.error("Request failed:", exc_info=1)

    def make_request(self):
        time, ticker, order_book = grequests.map(self.requests, exception_handler=self.request_exception_handler)
        time_json = time.json()
        ticker_json = ticker.json()
        orders_json = order_book.json()
        result = {'time': time_json, "ticker": ticker_json, "orders": orders_json}
        return result

    def update_df(self):
        # 1) save the current df to file
        file_name = self.product_id +'-{0:05d}.csv'.format(self.file_index)
        self.df.to_csv(os.path.join(self.data_dir, file_name), index=False)
        self.logger.info("File saved to: "+file_name)

        # 2) create a new df, update the index
        file_columns = ['time_epoch', 'time_iso', 'bid', 'ask', 'price', 'volumne', 'bid_orders', 'ask_orders']
        self.df = pd.DataFrame(index=np.arange(0, self.data_per_file), columns=file_columns)
        # assign a file and data index
        self.file_index += 1
        self.data_index = 0

    def update_data(self):
        # save the request to file
        threading.Timer(self.interval_seconds, self.update_data).start()
        response = self.make_request()
        result = [response['time']['epoch'],
                  response['time']['iso'],
                  response['ticker']['bid'],
                  response['ticker']['ask'],
                  response['ticker']['price'],
                  response['ticker']['volume'],
                  json.dumps(response['orders']['bids']),
                  json.dumps(response['orders']['asks'])]
        print self.data_index, response['time']['iso']
        self.df.loc[self.data_index] = result
        self.data_index += 1

        # If the current df have enough data, save it and open a new file
        if self.data_index == self.data_per_file:
            self.update_df()


def main():
    client = GdaxClient(data_per_file=5, interval_seconds=5)
    client.update_data()

if __name__ == "__main__":
    main()