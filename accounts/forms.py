"""
Accounts Forms
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class MemberRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    national_id = forms.CharField(max_length=20, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'National ID Number'}))
    phone_number = forms.CharField(max_length=15, required=True,
        widget=forms.TextInput(attrs={'placeholder': '+256 700 000 000'}))
    address = forms.CharField(required=True,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Physical Address'}))
    occupation = forms.CharField(max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Occupation / Job Title'}))
    monthly_income = forms.DecimalField(max_digits=12, decimal_places=2, required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Monthly Income (UGX)'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'national_id',
                  'phone_number', 'address', 'occupation', 'monthly_income',
                  'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_MEMBER
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'autofocus': True}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number',
                  'address', 'occupation', 'monthly_income', 'profile_photo')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
