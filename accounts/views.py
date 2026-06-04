"""
Accounts Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import User
from .forms import MemberRegistrationForm, LoginForm, ProfileUpdateForm
from loans.models import Loan


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to SACCO, {user.first_name}! Your account has been created.')
            return redirect('dashboard:index')
    else:
        form = MemberRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def member_list_view(request):
    """Admin only - list all members."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:index')
    members = User.objects.filter(role=User.ROLE_MEMBER).order_by('-date_joined')
    return render(request, 'accounts/member_list.html', {'members': members})


@login_required
def member_detail_view(request, pk):
    """Admin only - view member details."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:index')
    member = get_object_or_404(User, pk=pk)
    loans = Loan.objects.filter(applicant=member)
    return render(request, 'accounts/member_detail.html', {'member': member, 'loans': loans})


@login_required
def toggle_member_status(request, pk):
    """Admin only - activate/deactivate member."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:index')
    member = get_object_or_404(User, pk=pk)
    member.is_active = not member.is_active
    member.save()
    status = 'activated' if member.is_active else 'deactivated'
    messages.success(request, f'Member {member.get_full_name()} has been {status}.')
    return redirect('accounts:member_list')
