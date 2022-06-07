from django.db import models


class Job_Status(models.Model):
    
    job_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(db_index = True, auto_now_add = True, null = True)
    finished_at = models.DateTimeField(blank = True, null = True)
    total_records = models.IntegerField(default = 0)
    total_processed = models.IntegerField(default = 0)
    job_status = models.CharField(max_length = 20, blank = True, null = True)

    class Meta:
        db_table = 'job_status'
        verbose_name = 'Job_Status'
        verbose_name_plural = 'Job_Status'