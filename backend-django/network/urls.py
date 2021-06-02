from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_html, name='get_html'),
    path('image', views.get_image, name='get_image'),
]