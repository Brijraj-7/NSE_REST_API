from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import csvupload, IndexesIndexView  


router = DefaultRouter()
router.register(r'indexe', views.IndexViewSet)
router.register(r'indexprices', views.IndexPriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('csvupload/', csvupload, name='csvupload'),
    path('indexes/<int:pk>/', IndexesIndexView.as_view(), name='indexes-list'),  
]
