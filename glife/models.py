from django.db import models

# Create your models here.
class DataSource(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    json_file = models.FileField(upload_to='datasources/')
    def __str__(self):
        return self.name

class OriginalText(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    text = models.TextField()
    def __str__(self):
        return f'{self.text} ({self.data_source})'