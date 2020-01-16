
# analysis/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


class Unit(models.Model):
    name = models.CharField(max_length=256, default="unit")
    measurement_type = models.CharField(max_length=256, default=None)
    
    def __str__(self):
        return self.name

class Well(models.Model):
    name = models.CharField(max_length=256, default=None)
    location = models.CharField(max_length=256, default=None)

    def __str__(self):
        return self.name

class WellReport(models.Model):
    well = models.ForeignKey(Well, on_delete=models.CASCADE)
    title = models.CharField(max_length=256, default='untitled')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    graph = models.ImageField(upload_to='reports/%Y/%m/%d/', default=None)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    mean = models.FloatField(default=None)
    minimum= models.FloatField(default=None)
    maximum = models.FloatField(default=None)
    last = models.FloatField(default=None)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('analysis:report_detail',
            args=[str(self.id)]
        )

class MetaReport(models.Model):
    title = models.CharField(max_length=256, default='untitled')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    csv = models.FileField(upload_to='reports/%Y/%m/%d/', default=None)
    
    def __str__(self):
        return('{} - {}'.format(self.start_date, self.end_date))

class WellReading(models.Model):
    origin_file = models.CharField(max_length=256, null=True, default=None)
    well = models.ForeignKey(Well, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    value = models.FloatField(default=None)
    quality_code = models.FloatField(null=True, default=None)
    tag_comments = models.CharField(max_length=256, default='')

    def __str__(self):
        return "{}, {}, {} {}".format(
            self.well,
            self.date,
            self.value,
            self.unit
        )
