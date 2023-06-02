import calendar
import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django import forms
from Calendar.forms import ButtonForm, DayForm
from calendar import HTMLCalendar
from Calendar.models import Day

from Calendar.utils import Calendar

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

def home(request):
    date = datetime.date.today()
    if request.method == "POST":
        for day in range(1, 32):
            print(request.POST.get(str(day)))
            if request.POST.get(str(day)) == "":
                date = date.replace(day=int(day))
                print("hi")
                return redirect("/review/", args=(date))

    context = {}
    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(date.year, date.month)
    return render(request, "home.html", context)

def review(request, date=None):
    context ={}
    try:
        currents = Day.objects.all().filter(date = date)
        current = currents[len(currents)-1]
        print(current)
        print(currents)
    except:
        current = None
    if request.method == "POST":
        form = DayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
        
    if current == None and date != None:
        context['form'] = DayForm(
            initial={
                'date': date,
            }
        )
    elif date == None:
        context['form'] = DayForm(
            initial={
                'date': datetime.date.today(),
            }
        )
    else:
        context['form']= DayForm(
            initial={
                'mood': current.mood,
                'notes': current.notes,
                'emotions': current.emotions,
                'date': date,
            }
        )

    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(datetime.date.today().year, datetime.date.today().month)
    return render(request, "review.html", context)


#def review(request):
    #form = DayForm(forms.ModelForm)
    #return render(request, "review.html", context={"form": form})