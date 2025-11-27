from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hours = models.FloatField(default=1)
    importance = models.IntegerField(default=5)
    dependencies = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title
