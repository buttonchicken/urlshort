from django.urls import path,include
from .views import *

urlpatterns = [
    path('create',GenerateShortURL.as_view(),name="create_short_url")
]