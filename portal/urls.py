from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("payments/", views.payments, name="payments"),
    path("progress/", views.progress, name="progress"),
    path("progress/<int:entry_id>/", views.progress_update, name="progress_update"),
    path("history/", views.history, name="history"),
    path("book/", views.book_plan, name="book_plan"),
]
