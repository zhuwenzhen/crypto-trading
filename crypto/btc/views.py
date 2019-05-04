# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import btc, training
from django.contrib.auth import get_user_model
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
def index(request):
   # return HttpResponse('This is where the BTC stuff will go :)')
#    data_list = btc.objects.all().order_by('-id')[:10][::-1]
   
#    data ={
#         'info': data_list
#     }
   print("hello")
#    for x in range(len(data['info'])): 
#     print data['info'][x].price
#     print("well hi")
#    print(len(data['info']))
   return render(request, 'btc/index.html')


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        numData = 800
        data_list = btc.objects.all().order_by('-id')[:numData][::-1]
        #predict_list = predictions.objects.all().order_by('-id')[:800][::-1]
        priceList=[]
        timestampList=[]
        askList=[]
        bidList=[]
        predictPriceList=[]
        predictGP=[]
        predictGPU=[]
        predictGPL=[]
        count = 0
        predictPriceList.append(None)
        for btcObject in data_list:
            priceList.append(btcObject.price)
            timestampList.append(btcObject.time)
            if(btcObject.predict_price_LR < 1):
                predictPriceList.append(None)
            else:
                predictPriceList.append(btcObject.predict_price_LR)
            if(btcObject.predict_price_GP < 1):
                predictGP.append(None)
                predictGPU.append(None)
                predictGPL.append(None)
            else:
                predictGP.append(btcObject.predict_price_GP)
                predictGPU.append(btcObject.GP_UB)
                predictGPL.append(btcObject.GP_LB)
            
            if(count>numData-51):
                bidList.append(btcObject.bid)
                askList.append(btcObject.ask)      
            count=count+1
        timestampList.append("Next 10 seconds")
        
        labels = [ "Blue", "Yellow", "Green", "Purple", "Orange"]
        default_items = [23, 2, 3, 12, 2]
        data = {
                "labels": labels,
                "default": default_items,
                "price":priceList,
                "time":timestampList,
                "ask": askList,
                "bid": bidList,
                "predict": predictPriceList,
                "gbpredict": predictGP,
                "gbupredict": predictGPU,
                "gblpredict": predictGPL
        }
        return Response(data)