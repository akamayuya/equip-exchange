from django.urls import path

from . import views

urlpatterns = [
    path("buy/<int:product_pk>/", views.trade_create, name="trade_create"),
    path("<int:pk>/", views.trade_detail, name="trade_detail"),
    path("<int:pk>/status/", views.trade_update_status, name="trade_update_status"),
    path("<int:pk>/chat/", views.chat, name="chat"),
    path("<int:pk>/chat/api/", views.chat_messages_api, name="chat_messages_api"),
]
