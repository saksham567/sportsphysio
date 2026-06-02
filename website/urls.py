from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("plans/", views.plans, name="plans"),
    path("book-consultation/", views.book_consultation, name="book_consultation"),
    path("book/", views.book, name="book"),
    path("payment/", views.payment, name="payment"),
    path("payment/razorpay/create/", views.razorpay_create_order, name="razorpay_create_order"),
    path("payment/razorpay/verify/", views.razorpay_verify, name="razorpay_verify"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/submitted/", views.payment_submitted, name="payment_submitted"),
    path("reviews/", views.reviews, name="reviews"),
]
