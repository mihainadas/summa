from django.contrib import admin

class MyAdminSite(admin.AdminSite):
    site_header = 'Project Summa - Galandriel'
    site_title = 'Project Summa'
    index_title = 'Administration'