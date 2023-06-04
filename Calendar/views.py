import calendar
import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views import generic
from django import forms
from Calendar.forms import ButtonForm, DayForm
from calendar import HTMLCalendar
from Calendar.models import Day
from django.contrib.auth.decorators import login_required

from Calendar.utils import Calendar

date = datetime.date.today()

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

def home(request):
    global date
    today = datetime.date.today()
    if request.method == "POST":
        for day in range(1, 32):
            print(request.POST.get(str(day)))
            if request.POST.get(str(day)) == "":
                date = date.replace(day=int(day))
                print("hi")
                return redirect('review')
    
    try:
        user = request.user
    except:
        user = None

    context = {}
    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(today.year, today.month, user)
    return render(request, "home.html", context)

@login_required(login_url='/login/')
def review(request):
    global date
    context = {}
    user = request.user
    try:
        currents = Day.objects.all().filter(user = user).filter(date = date)
        print(currents)
        current = currents[len(currents)-1]
        print(current)
        print(currents)
    except:
        current = None
    if request.method == "POST":
        form = DayForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect("/")
        
    if current == None:
        context['form'] = DayForm(
            initial={
                'date': date,
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

    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(datetime.date.today().year, datetime.date.today().month, user)
    date = date.replace(day=int(datetime.date.today().day))
    return render(request, "review.html", context)


#def review(request):
    #form = DayForm(forms.ModelForm)
    #return render(request, "review.html", context={"form": form})