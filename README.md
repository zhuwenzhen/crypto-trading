# Final Project: Crypto Trading
This project contains 2 parts:
1. Implemented and trained a Bayesian regression model proposed from a paper. Also trained a Gaussian process model with same features and (much less) data.
2. A Django, real-time visualization forecasting tool to display the crypto price (from Coinbase / Gdax) and 
the predicted crypto price in real time. This visualization tool can help us with 
testing our trained prediction model.

## Project Design

```
CryptoTrading
├── backend/
│   ├── gdaxCrawler50.py: crawler that collect data for training
│   ├── publicClient.py: client connect with Coinbase API
│   └── writeToDB.py: write testing data to dabase
├── crypto/
│   ├── btc
│   ├── crypto
│   ├── manage.py
│   └── db.sqlite3
├── data/
│   └── btc.csv: training data (1.47GB) emitted because the file is too large
├── model/
│   ├── GP.wxf: smaller GP model trained with first 5000 datapoints (~ 200 MB)
│   ├── GP_big.wxf: bigger and better GP model with 10,000 datapoints (~ 800 MB)
│   ├── p1.wxf: predict price change deltaP1 based on previous 30 mins data
│   ├── p2.wxf: predict price change deltaP2 based on previous 60 mins data
│   ├── p3.wxf: predict price change deltaP2 based on previous 120 mins data
│   └── pFinal.wxf: bayesian regression model with input (p1, p2, p3, gamma)
├── test/
│   ├── lr_test.wl
│   └── gp_test.wl
└── train/: contains model training scripts
    ├── GaussianProcess.nb
    └── BayesianRegression.nb
```

## Usage

To store the current price into database:
```
python3 backend/writeToDB.py
```

To run Bayesian Regression / Gaussian Process model evaluation:
```
wolframscript -f test/lr_test.wl
wolframscript -f test/gp_model_test.wl 
```

## Front-end 

Uses Django framework to display a chart of current Bitcoin price as well as forecasting predicted price

## Back-end

We split Back-end into two parts:

+ Model
    + Crawler to collect data (timestamp, price, bid_volume, ask_volume) every 10s 
    for training purpose.
    + Implemented a Bayesian Regression model proposed on paper.
    + Trained several models:
        + Bayesian Regression model
        + Gaussian Process model
    + Python script that query the real-time data and evaluate on pre-trained models

+ DJANGO Framework
    + Takes information from the database, presented as a model in the django framework and sends it to the user trying to access the webside

## Database

Because the model utilize the orderbook information to make predictions, 
we need to store such information for testing purpose.

+ Created a SQL database called crypto
+ Created a table: btc_btc with the following fields:
    + id (int)
    + time (timestamp)
    + price (float): BTC price on Coinbase
    + bid (float): top 50 bid orders total volume
    + ask (float): top 50 ask orders total volume
    + predict_price_LR (float): predicted price by linear regression model
    + predict_price_LSTM (float): predicted price by LSTM (Long-short term memory) model
    + predict_price_GP (float): predicted price by Gaussian process model
    + GP_LB (float): Gaussian process confidence interval's lower bound
    + GP_UB (float): Gaussian process confidence interval's upper bound
    
To train a model, we would need 4 features (timestamp, price, bid_volume, ask_volume).
To test our model performance in real time, we would query the previous 30 mins, 60 mins, 
120 mins data and write the computed / predicted price into the database.
