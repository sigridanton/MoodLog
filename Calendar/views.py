import calendar
import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views import generic
from django import forms
import matplotlib.pyplot as plt
from Calendar.forms import ButtonForm, DayForm
from calendar import HTMLCalendar
from Calendar.models import Day, Month
from django.contrib.auth.decorators import login_required

from Calendar.utils import Calendar

# track dates
state = {
    "cal_date": datetime.date.today(),
    "review_date": datetime.date.today(),
    "stat_type": "monthly",
}

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

def home(request):
    global state
    if request.method == "POST":
        if request.POST.get("previous") == "":
            y = state["cal_date"].year
            m = state["cal_date"].month
            if m == 1:
                state["cal_date"] = datetime.date(y-1, 12, 1)
            else:
                state["cal_date"] = datetime.date(y, m-1, 1)
            
            return redirect("/#calendar")
        if request.POST.get("next") == "":
            y = state["cal_date"].year
            m = state["cal_date"].month
            if m == 12:
                state["cal_date"] = datetime.date(y+1, 1, 1)
            else:
                state["cal_date"] = datetime.date(y, m+1, 1)
            return redirect("/#calendar")
            
        if request.POST.get("current") == "":
            state["cal_date"] = datetime.date.today()
            return redirect("/#calendar")
        for day in range(1, 32):
            if request.POST.get(str(day)) == "":
                state["review_date"] = datetime.date(state["cal_date"].year, state["cal_date"].month, day)
                return redirect('review')
    
    try:
        user = request.user
    except:
        user = None

    context = {}
    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(state["cal_date"].year, state["cal_date"].month, user)
    return render(request, "home.html", context)

@login_required(login_url='/login/')
def review(request):
    context = {}
    user = request.user

    # find any reviews already made
    try:
        currents = Day.objects.all().filter(user = user).filter(date = state["review_date"])
        current = currents[len(currents)-1]
    except:
        current = None

    # handle review form
    if request.method == "POST" and request.POST.get("review") == "":
        form = DayForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            try:
                review.month = Month.objects.filter(user = request.user).filter(month = int(state["review_date"].month)).get(year = int(state["review_date"].year))
            except:
                review.month = Month.objects.create(month=state["review_date"].month, year=state["review_date"].year, user=request.user)
            print(review.month)
            if not review.month:
                review.month = Month.objects.create(month=state["review_date"].month, year=state["review_date"].year, user=request.user)

            # delete duplicates
            others = Day.objects.filter(date = review.date)
            [x.delete() for x in others[1:(len(others)-1)]]
            print(Day.objects.all())

            review.save()
            return redirect("/review/")
    
    # handle calendar 
    elif request.method == "POST":

        # if previous is clicked
        if request.POST.get("previous") == "":
            y = state["cal_date"].year
            m = state["cal_date"].month
            if m == 1:
                state["cal_date"] = datetime.date(y-1, 12, 1)
            else:
                state["cal_date"] = datetime.date(y, m-1, 1)
            return redirect("/review/")
        
        # if next is clicked
        if request.POST.get("next") == "":
            y = state["cal_date"].year
            m = state["cal_date"].month
            if m == 12:
                state["cal_date"] = datetime.date(y+1, 1, 1)
            else:
                state["cal_date"] = datetime.date(y, m+1, 1)
            return redirect("/review/")
        
        # if current is clicked
        if request.POST.get("current") == "":
            state["cal_date"] = datetime.date.today()
            return redirect("/review/")
        
        # if a day is clicked
        for day in range(1, 32):
            if request.POST.get(str(day)) == "":
                state["review_date"] = datetime.date(state["cal_date"].year, state["cal_date"].month, day)
                return redirect("/review/")
    
    # if no review exist of the day
    if current == None:
        context['form'] = DayForm(
            initial={
                'date': state["review_date"],
            }
        )
    else:
        context['form']= DayForm(
            initial={
                'mood': current.mood,
                'notes': current.notes,
                'emotions': current.emotions,
                'date': state["review_date"],
            }
        )

    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(state["cal_date"].year, state["cal_date"].month, user)
    state["review_date"] = datetime.date.today()
    return render(request, "review.html", context)

@login_required(login_url='/login/')
def stats(request):
    context = {}

    if request.method == "POST":
        if request.POST.get("previous") == "":
            y = state["cal_date"].year
            m = state["cal_date"].month
            if m == 1:
                state["cal_date"] = datetime.date(y-1, 12, 1)
            else:
                state["cal_date"] = datetime.date(y, m-1, 1)
            
            return redirect("/stats/#calendar")
        if request.POST.get("next") == "":
            y = state["cal_date"].year
            m = state["cal_date"].month
            if m == 12:
                state["cal_date"] = datetime.date(y+1, 1, 1)
            else:
                state["cal_date"] = datetime.date(y, m+1, 1)
            return redirect("/stats/#calendar")
            
        if request.POST.get("current") == "":
            state["cal_date"] = datetime.date.today()
            return redirect("/stats/#calendar")
        for day in range(1, 32):
            if request.POST.get(str(day)) == "":
                state["review_date"] = datetime.date(state["cal_date"].year, state["cal_date"].month, day)
                return redirect('/stats/#calendar')
    
    try:
        user = request.user
    except:
        user = None
    
    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(state["cal_date"].year, state["cal_date"].month, user)

    month = state["cal_date"].month
    year = state["cal_date"].year
    stat_type = state["stat_type"]

    if stat_type == "monthly":
        axes = []
        days = Day.objects.all().filter(user = user).filter(date__year=year).filter(date__month=month)
        for day in days:
            axes.append((int(day.date.day), int(day.mood)))
        
        moods = [x[1] for x in axes]
        days = [x[0] for x in axes]

        plt.plot(days, moods)
        plt.savefig('static/media/mood.png')

        #context["mood_graph"] = 

    return render(request, "stats.html", context)