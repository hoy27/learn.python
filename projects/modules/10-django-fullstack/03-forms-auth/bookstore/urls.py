# ============================================================================
# Bookstore URL Patterns — Forms & Auth Project
# ============================================================================

from django.urls import path

from . import views

urlpatterns = [
    path("", views.book_list, name="book_list"),
    path("<int:pk>/", views.book_detail, name="book_detail"),
    path("add/", views.add_book, name="add_book"),
    path("<int:pk>/edit/", views.edit_book, name="edit_book"),
    path("<int:pk>/delete/", views.delete_book, name="delete_book"),
]
