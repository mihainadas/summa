from django.contrib import admin
from .models import DataSource, OriginalText
from django.contrib.admin import register, ModelAdmin

# Register your models here.
@register(DataSource)
class DataSourceAdmin(ModelAdmin):
    list_display = ('name', 'description', 'json_file')
    list_filter = ('name', 'description', 'json_file')

@register(OriginalText)
class OriginalTextAdmin(ModelAdmin):
    list_display = ('data_source', 'text')
    list_filter = ('data_source', 'text')

