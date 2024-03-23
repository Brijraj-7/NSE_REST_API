from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomAuthToken, csvupload, IndexesIndexView ,send_mail_all


router = DefaultRouter()
router.register(r'indexe', views.IndexViewSet)
router.register(r'indexprices', views.IndexPriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('csvupload/', csvupload, name='csvupload'),
    path('custom-token-auth/', CustomAuthToken.as_view()),
    path('sendmail/', send_mail_all, name= 'send_mail'),
    path('indexes/<int:pk>/', IndexesIndexView.as_view(), name='indexes-list'),  
]
