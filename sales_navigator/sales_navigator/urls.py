from turtle import down
from django.contrib import admin
from django.urls import path, re_path
from scraping.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('v0/linked', Create_Job.as_view()),
    re_path('^v0/linked/download/(?P<job_id>.+)', Download_Job.as_view()),
    re_path('^v0/linked/(?P<job_id>.+)', Get_Job_Status.as_view())
]