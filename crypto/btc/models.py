# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class training(models.Model):
    time = models.DateTimeField()
    price = models.IntegerField()
    bid = models.IntegerField()
    ask = models.IntegerField()

class btc(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    bid = models.FloatField()
    ask = models.FloatField()
    predict_price_LR = models.FloatField()
    predict_price_LSTM = models.FloatField()
    predict_price_GP = models.FloatField()
    GP_LB = models.FloatField()
    GP_UB = models.FloatField()
class predictions(models.Model):
    timestamp = models.DateTimeField()
    predicted_price = models.IntegerField()