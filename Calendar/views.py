import base64
import calendar
import datetime
from io import BytesIO
from multiprocessing.managers import BaseManager
import os
import matplotlib
from matplotlib.transforms import Bbox
import numpy
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from calendar import HTMLCalendar, monthrange

from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views import generic
from django import forms
from django.contrib.auth.decorators import login_required

from Calendar.forms import DayForm
from Calendar.models import Day, Month
from Calendar.utils import Calendar

# track dates
state = {
    "cal_date": datetime.date.today(),
    "review_date": datetime.date.today(),
    "stat_type": "monthly", # 'monthly' or 'yearly'
    "stat_date": datetime.date.today()
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
        
        if request.POST.get("monthly") == "":
             state["stat_type"] = "monthly"
             return redirect("/#stats")
        
        if request.POST.get("yearly") == "":
             state["stat_type"] = "yearly"
             return redirect("/#stats")
            
        if request.POST.get("current") == "":
            state["cal_date"] = datetime.date.today()
            return redirect("/#calendar")
        
        if request.POST.get("statprev") == "":
            if state["stat_type"] == "monthly":
                state["stat_date"] = state["stat_date"].replace(month=(state["stat_date"].month-1))
            else:
                state["stat_date"] = state["stat_date"].replace(year=(state["stat_date"].year-1))
            return redirect("/#stats")
        
        if request.POST.get("statnext") == "":
            if state["stat_type"] == "monthly":
                state["stat_date"] = state["stat_date"].replace(month=(state["stat_date"].month+1))
            else:
                state["stat_date"] = state["stat_date"].replace(year=(state["stat_date"].year+1))
            return redirect("/#stats")
        
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

    month = state["cal_date"].month
    year = state["cal_date"].year
    stat_type = state["stat_type"]
    stat_date = state["stat_date"]

    if stat_type == "monthly":
        try:
            days = Day.objects.all().filter(user = user).filter(date__year=stat_date.year).filter(date__month=stat_date.month)
        except:
            days = []
        axes = {int(day.date.day): int(day.mood) for day in days}
        
        dates = numpy.array(range(1, monthrange(stat_date.year, stat_date.month)[1]+1))
        moods = numpy.array([axes[day] if day in axes else None for day in dates])
        moods = numpy.ma.masked_where(moods == None, moods)

        plt.figure(figsize=(10,5))
        plt.plot(dates, moods, 'o-', color='black')
        plt.xticks(dates)
        plt.yticks(range(1, 8))

        tmpfile = BytesIO()
        plt.savefig(tmpfile, format='png', bbox_inches='tight')
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

        context["stats"] = '<img src=\'data:image/png;base64,{}\' alt="stats">'.format(encoded)
        
        plt.figure().clear()

    if stat_type == "yearly":
        try:
            days = Day.objects.all().filter(user = user).filter(date__year=stat_date.year)
        except:
            days = Day.objects.none()
        month_ratings = {}
        for m in range(1, 13):
            month_days = days.filter(date__month=m)
            try:
                avg = float(numpy.average([int(day.mood) for day in month_days if int(day.mood)]))
            except:
                avg = None
            month_ratings[m] = avg
        
        x = numpy.array(range(1, 13))
        y = [month_ratings[m] for m in range(1, 13)]
        y = numpy.ma.masked_where(y == None, y)

        plt.plot(x, y, 'o-', color='black')
        plt.xticks(x)
        plt.yticks(range(1, 8))

        tmpfile = BytesIO()
        plt.savefig(tmpfile, format='png')
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

        context["stats"] = '<img src=\'data:image/png;base64,{}\' alt="stats">'.format(encoded)

        plt.figure().clear()
    
    context["stat_type"] = stat_type
    if stat_type == "monthly":
        context["stat_date"] = "%s %s" % (calendar.month_abbr[stat_date.month], stat_date.year)
    else:
        context["stat_date"] = "%s" % (stat_date.year)

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
        form = DayForm(request.POST, request.FILES)
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
            Day.objects.filter(date = review.date).delete()
            print(Day.objects.all())

            review.save()
            return redirect("/#calendar")
    
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
            return redirect("/review/#calendar")
        
        # if next is clicked
        if request.POST.get("next") == "":
            y = state["cal_date"].year
            m = state["cal_date"].month
            if m == 12:
                state["cal_date"] = datetime.date(y+1, 1, 1)
            else:
                state["cal_date"] = datetime.date(y, m+1, 1)
            return redirect("/review/#calendar")
        
        # if current is clicked
        if request.POST.get("current") == "":
            state["cal_date"] = datetime.date.today()
            return redirect("/review/#calendar")
        
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