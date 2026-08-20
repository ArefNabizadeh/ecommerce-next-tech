from django.urls import path
from . import views

app_name = 'apps.dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('orders/', views.orders_view, name='orders'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('addresses/', views.addresses_view, name='addresses'),
    path('address/add/', views.add_address_view, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address_view,
         name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address_view,
         name='delete_address'),
    path('address/default/<int:address_id>/', views.set_default_address_view,
         name='set_default_address'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_wishlist_view,
      name='remove_wishlist'),
]