from django.contrib import admin
from django.urls import path, re_path
from scraping.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('v0/linked', Create_Job.as_view()),
    re_path('^v0/linked/download/(?P<job_id>.+)', Download_Job.as_view()),
    re_path('^v0/linked/(?P<job_id>.+)', Get_Job_Status.as_view()),
    re_path('^v0/linked/stop_the_job/(?P<job_id>.+)', Stop_Job.as_view()),
    re_path('^v0/linked/get_all_running_jobs', Get_All_Running_Jobs.as_view())
]