# apps/orders/urls.py
from django.urls import path
from . import views

app_name = 'apps.orders'

urlpatterns = [
    path('', views.order_list_view, name='order_list'),
    path('<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('cancel/<int:order_id>/', views.cancel_order_view, name='cancel_order'),
]