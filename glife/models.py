import os
from django.db import models
from django.utils.text import slugify
from datetime import datetime

def datasource_upload_path(instance, filename):
    base, extension = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    adjusted_filename = f'{base}-{timestamp}{extension}'
    return "glife/datasources/{0}/{1}".format(slugify(instance.name), adjusted_filename)

class DataSource(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    json_file = models.FileField(
        upload_to=datasource_upload_path,
        verbose_name='JSON File',
        help_text='Upload a JSON file containing the data for this data source.'
        )
    def __str__(self):
        return self.name

class OriginalText(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    text = models.TextField()
    def __str__(self):
        return f'{self.text} ({self.data_source})'