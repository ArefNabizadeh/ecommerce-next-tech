from django.urls import path
from . import views

app_name = 'apps.blog'

urlpatterns = [
    path('', views.blog_list_view, name='blog_list'),
    path('categories/', views.category_list_view, name='category_list'),
    path('<slug:slug>/', views.blog_detail_view, name='blog_detail'),

]
