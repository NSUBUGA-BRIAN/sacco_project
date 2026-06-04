from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loan_list_view, name='list'),
    path('apply/', views.loan_apply_view, name='apply'),
    path('<int:pk>/', views.loan_detail_view, name='detail'),
    path('<int:pk>/submit/', views.loan_submit_view, name='submit'),
    path('<int:pk>/action/', views.loan_action_view, name='action'),
    path('api/calculate/', views.calculate_installment_api, name='calculate'),
]
