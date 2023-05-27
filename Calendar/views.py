import calendar
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django import forms
from Calendar.forms import DayForm
from calendar import HTMLCalendar

from Calendar.utils import Calendar

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

def home(request):
    context = {}
    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(datetime.date.today().year, datetime.date.today().month)
    print(Calendar(calendar.MONDAY).formatmonth(2023, 5))
    return render(request, "home.html", context)

def review(request):
    context ={}
    context['form']= DayForm()
    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(datetime.date.today().year, datetime.date.today().month)
    print(Calendar(calendar.MONDAY).formatmonth(2023, 5))
    return render(request, "review.html", context)


#def review(request):
    #form = DayForm(forms.ModelForm)
    #return render(request, "review.html", context={"form": form})