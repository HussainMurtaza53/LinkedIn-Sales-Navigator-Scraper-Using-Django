from django.contrib import admin
from django.urls import path
from scraping.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('v0/linked', LinkedIn_Scraping.as_view()),
]
