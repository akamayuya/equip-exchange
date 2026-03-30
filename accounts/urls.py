from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("mypage/", views.mypage, name="mypage"),
    path("payment-methods/new/", views.payment_method_create, name="payment_method_create"),
    path("payment-methods/<int:pk>/default/", views.payment_method_set_default, name="payment_method_set_default"),
]
