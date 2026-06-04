from django.urls import path
from . import views

app_name = 'repayments'

urlpatterns = [
    path('', views.repayment_list_view, name='list'),
    path('loan/<int:loan_pk>/', views.loan_repayments_view, name='loan_repayments'),
    path('<int:pk>/record/', views.record_payment_view, name='record_payment'),
]
