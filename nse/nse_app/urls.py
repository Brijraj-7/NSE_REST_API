# nse_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    FristFiveIndexView, 
    IndexPriceByDateView, 
    csvupload,
    FilterIndexPriceView,
    FiltersIndexPriceView,
    IndexesIndexView,
    indexesDetailView
    )

router = DefaultRouter()
router.register(r'indexes', views.IndexViewSet)
router.register(r'indexprices', views.IndexPriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('csvupload/', csvupload, name='csvupload'),
    path('index/<int:num>/', FristFiveIndexView.as_view(), name='first_five_index'),
    path('indexes/<int:pk>/<int:id>', IndexesIndexView.as_view(), name= 'indexes_name_index_data' ),
    path('indexesdelete/<int:pk>/', indexesDetailView.as_view(), name='indexes-detate'),
    path('date/<str:date>/', IndexPriceByDateView.as_view(), name='index_price_by_date'),   
    path('filter/<str:field>/', FilterIndexPriceView.as_view(), name='filter_index_price'),
    path('fld/<str:fields>/', FiltersIndexPriceView.as_view(), name='filter_index_price'),
]
