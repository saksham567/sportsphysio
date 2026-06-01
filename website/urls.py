from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("plans/", views.plans, name="plans"),
    path("book/", views.book, name="book"),
    path("payment/", views.payment, name="payment"),
    path("payment/submitted/", views.payment_submitted, name="payment_submitted"),
    path("reviews/", views.reviews, name="reviews"),
]
