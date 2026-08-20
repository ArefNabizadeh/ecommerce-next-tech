# apps/products/urls.py
from django.urls import path
from . import views

app_name = 'apps.products'

urlpatterns = [
    # ===== لیست محصولات =====
    path('', views.product_list_view, name='product_list'),

    # ===== جزئیات محصول =====
    path('<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('<int:product_id>/<slug:slug>/', views.product_detail_view, name='product_detail_slug'),

    # ===== دسته‌بندی‌ها =====
    path('categories/', views.category_list_view, name='category_list'),

    # ===== برندها =====
    path('brands/', views.brand_list_view, name='brand_list'),

    # ===== علاقه‌مندی‌ها =====
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist_view, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist_view, name='remove_from_wishlist'),
]