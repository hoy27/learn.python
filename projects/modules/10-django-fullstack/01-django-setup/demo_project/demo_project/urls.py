"""
URL configuration for demo_project.

The `urlpatterns` list routes URLs to views. For more information:
https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path

# Each path() call maps a URL pattern to a view.
# "admin/" maps to Django's built-in admin interface.
# You will add more patterns here as you create views.
urlpatterns = [
    path("admin/", admin.site.urls),
]
