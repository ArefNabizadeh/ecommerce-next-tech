from django.urls import path
from . import views

app_name = 'apps.cart'

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    # ← این باید باشه
    path('update/<int:item_id>/', views.update_cart_item_view, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('move-to-wishlist/<int:item_id>/', views.move_to_wishlist_view,
         name='move_to_wishlist'),
    path('clear/', views.clear_cart_view, name='clear_cart'),
    path('apply-coupon/', views.apply_coupon_view, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon_view, name='remove_coupon'),
]
