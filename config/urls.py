"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from apps.core.views import error_404_preview, error_500_preview, error_404_view, error_500_view
from apps.core.views import clear_messages


handler404 = 'apps.core.views.error_404_view'
handler500 = 'apps.core.views.error_500_view'
urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("apps.core.urls")),

    path("accounts/", include("apps.accounts.urls")),

    path("products/", include("apps.products.urls")),

    path("cart/", include("apps.cart.urls")),

    path("orders/", include("apps.orders.urls")),

    path("dashboard/", include("apps.dashboard.urls")),
    path('blog/', include('apps.blog.urls')),
    path('clear-messages/', clear_messages, name='clear_messages'),
    path('discounts/', include('apps.discounts.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('404/', error_404_preview, name='error_404_preview'),
        path('500/', error_500_preview, name='error_500_preview'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

