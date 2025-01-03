from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # Use your custom user model
        fields = ('username', 'password1', 'password2')  # Include only the fields you want

        