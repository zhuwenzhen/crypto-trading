import os
import pandas as pd
from ast import literal_eval
import time
import numpy as np


class Preprocess():

    def process(self, df):
        col_names = ["time", "price", "bid", "ask", "sell_history", "buy_history"]

        for i in col_names[2:]:
            df[i] = df[i].apply(literal_eval)

        bid_size = [sum(np.array(df['bid'][i])[:, 1]) for i in range(len(df))]
        ask_size = [sum(np.array(df['ask'][i])[:, 1]) for i in range(len(df))]

        df2 = pd.DataFrame(
            {
                'time': df.index.values,
                'price': df['price'].values,
                'bid_size': bid_size,
                'ask_size': ask_size
            },
            columns=['time', 'price', 'bid_size', 'ask_size'],
        )

        df2 = df2.set_index(['time'])
        df2 = df2.resample('10s').mean()

        with open('processed_data/btc_process.csv', 'a') as f:
            df2.to_csv(f, header=False)

    def data_preprocess(self, csv):
        """

        :param data: crypto currency price series raw data (every 2s)
        :return: price series (10 s)
        """

        def date_parser(string_list):
            return [time.ctime(float(x)) for x in string_list]

        chunksize = 10 ** 2

        col_names = ["time", "price", "bid", "ask", "sell_history", "buy_history"]

        datapoints = 0
        for chunk in pd.read_csv(csv, \
                                 chunksize=chunksize, \
                                 sep=',', \
                                 quotechar='"', \
                                 names=col_names, \
                                 date_parser=date_parser, \
                                 parse_dates=True, \
                                 index_col='time'):
            self.process(chunk)
            datapoints += chunksize
            print("processed", datapoints, "datapoints")

        print("finished processing, processed", datapoints, "data points in total.")


def main():
    data_directory = os.path.join(os.getcwd(), 'processed_data')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    prep = Preprocess()
    prep.data_preprocess('data/btc_1.csv')


main()