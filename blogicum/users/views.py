from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
    template_name = 'registration/registration_form.html'
# Create your views here.
