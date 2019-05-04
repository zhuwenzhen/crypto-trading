from django.conf.urls import url, include
from . import views
from .views import ChartData
urlpatterns=[
    url(r'^$', views.index, name='index'),
    url(r'^api/chart/$$', ChartData.as_view())
]