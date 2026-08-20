from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'apps.accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/change_password.html',
             success_url='/accounts/password-change-done/'
         ),
         name='change_password'),

    path('password-change-done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ),
         name='password_change_done'),

]