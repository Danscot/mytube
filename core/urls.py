
from django.urls import path


from . import views

urlpatterns = [

    path('', views.downloader, name='downloader'),
]


