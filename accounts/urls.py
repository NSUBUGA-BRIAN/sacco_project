from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('members/', views.member_list_view, name='member_list'),
    path('members/<int:pk>/', views.member_detail_view, name='member_detail'),
    path('members/<int:pk>/toggle/', views.toggle_member_status, name='toggle_status'),
]
