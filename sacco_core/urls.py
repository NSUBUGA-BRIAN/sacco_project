"""
SACCO Loan Management System - URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('loans/', include('loans.urls')),
    path('repayments/', include('repayments.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
    path('api/', include('accounts.api_urls')),
    path('api/loans/', include('loans.api_urls')),
    path('api/repayments/', include('repayments.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin
admin.site.site_header = "SACCO Loan Management"
admin.site.site_title = "SACCO Admin"
admin.site.index_title = "Administration Dashboard"
