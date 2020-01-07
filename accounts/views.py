
# accoutns/views.py
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.views.generic import CreateView
from . import forms

# Create your views here.

class RegisterUser(CreateView):
    form_class = forms.UserRegistrationForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"
