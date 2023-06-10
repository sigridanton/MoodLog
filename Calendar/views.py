import base64
from io import BytesIO

import matplotlib
import calendar
import numpy
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from calendar import monthrange

from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required

from Calendar.forms import DayForm
from Calendar.models import Day
from Calendar.utils import Calendar, Date, date_from_dict


today = Date.today()

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

def home(request):
    request.session.setdefault("cal_date", today.as_dict())
    request.session.setdefault("review_date", today.as_dict())
    request.session.setdefault("stat_type", "monthly")
    request.session.setdefault("stat_date", today.as_dict())

    cal_date = request.session.get("cal_date")
    stat_type = request.session.get("stat_type")
    stat_date = request.session.get("stat_date")

    if request.method == "POST":

        # previous calendar month
        if request.POST.get("previous") == "":
            y = cal_date["year"]
            m = cal_date["month"]

            if m == 1:
                request.session["cal_date"] = Date(y-1, 12, 1).as_dict()
            else:
                request.session["cal_date"] = Date(y, m-1, 1).as_dict()
            
            return redirect("/#calendar")
        
        # next calendar month
        if request.POST.get("next") == "":
            y = cal_date["year"]
            m = cal_date["month"]
            if m == 12:
                request.session["cal_date"] = Date(y+1, 1, 1).as_dict()
            else:
                request.session["cal_date"] = Date(y, m+1, 1).as_dict()
            return redirect("/#calendar")
        
        # go to current calendar month
        if request.POST.get("current") == "":
            request.session["cal_date"] = Date.today().as_dict()
            return redirect("/#calendar")
        
        # switch between monthly and yearly stats
        if request.POST.get("monthly") == "":
             request.session["stat_type"] = "monthly"
             return redirect("/#stats")
    
        if request.POST.get("yearly") == "":
             request.session["stat_type"] = "yearly"
             return redirect("/#stats")
        
        # previous statistics month or year
        if request.POST.get("statprev") == "":
            if request.session.get("stat_type") == "monthly":
                if stat_date["month"] > 1:
                    request.session["stat_date"] = date_from_dict(stat_date).replace(month=(stat_date["month"]-1)).as_dict()
                else:
                    request.session["stat_date"] = date_from_dict(stat_date).replace(month=12, year=stat_date["year"]-1).as_dict()
            else:
                request.session["stat_date"] = date_from_dict(stat_date).replace(year=stat_date["year"]-1).as_dict()
            return redirect("/#stats")
        
        # next statistics month or year
        if request.POST.get("statnext") == "":
            if stat_type == "monthly":
                if stat_date["month"] < 12:
                    request.session["stat_date"] = date_from_dict(stat_date).replace(month=(stat_date["month"]+1)).as_dict()
                else:
                    request.session["stat_date"] = date_from_dict(stat_date).replace(month=1, year=stat_date["year"]+1).as_dict()
            else:
                request.session["stat_date"] = date_from_dict(stat_date).replace(year=(stat_date["year"]+1)).as_dict()
            return redirect("/#stats")
        
        # go to current stat month or year
        if request.POST.get("stats_current") == "":
            if stat_type == "monthly":
                request.session["stat_date"] = date_from_dict(stat_date).replace(month=(Date.today().month)).as_dict()
            else:
                request.session["stat_date"] = date_from_dict(stat_date).replace(year=(Date.today().year)).as_dict()
            return redirect("/#stats")
        
        # handle cursor presses on calendar days
        for day in range(1, 32):
            if request.POST.get(str(day)) == "":
                request.session["review_date"] = date_from_dict(cal_date).replace(day=day).as_dict()
                return redirect('review')
            
    try:
        user = request.user
    except:
        user = None

    context = {}
    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(request.session.get("cal_date")["year"], request.session.get("cal_date")["month"], user)

    if stat_type == "monthly":
        try:
            days = Day.objects.all().filter(user = user).filter(date__year=stat_date['year']).filter(date__month=stat_date['month'])
        except:
            days = []

        # dict with x and y values (x: y)
        axes = {int(day.date.day): int(day.mood) for day in days}
        
        # get x axis values
        dates = numpy.array(range(1, monthrange(stat_date["year"], stat_date['month'])[1]+1))

        # get all moods and mask none values
        moods = numpy.array([axes[day] if day in axes else None for day in dates])
        moods = numpy.ma.masked_where(moods == None, moods)

        # create plot
        plt.figure(figsize=(10,5))
        plt.plot(dates, moods, 'o-', color='black')
        plt.xticks(dates)
        plt.yticks(range(1, 8))

        # make temp file for plot
        tmpfile = BytesIO()
        plt.savefig(tmpfile, format='png', bbox_inches='tight')
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

        context["stats"] = '<img src=\'data:image/png;base64,{}\' alt="stats">'.format(encoded)
        
        plt.figure().clear()
        plt.close()

    if stat_type == "yearly":
        try:
            days = Day.objects.all().filter(user = user).filter(date__year=stat_date['year'])
        except:
            days = Day.objects.none()

        # dict for month: avgmood
        month_ratings = {}
        for m in range(1, 13):
            month_days = days.filter(date__month=m)
            try:
                avg = float(numpy.average([int(day.mood) for day in month_days if int(day.mood)]))
            except:
                avg = None
            month_ratings[m] = avg
        
        # x and y values
        dates = numpy.array(range(1, 13))
        moods = [month_ratings[m] for m in range(1, 13)]
        moods = numpy.ma.masked_where(moods == None, moods)

        # create plot
        plt.figure(figsize=(5,5))
        plt.plot(dates, moods, 'o-', color='black')
        plt.xticks(dates)
        plt.yticks(range(1, 8))

        # temp file
        tmpfile = BytesIO()
        plt.savefig(tmpfile, format='png', bbox_inches='tight')
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

        context["stats"] = '<img src=\'data:image/png;base64,{}\' alt="stats">'.format(encoded)

        plt.figure().clear()
        plt.close()
    
    context["stat_type"] = stat_type

    # display the month and year above graph
    if stat_type == "monthly":
        context["stat_date"] = "%s %s" % (calendar.month_name[stat_date['month']], stat_date['year'])
    else:
        context["stat_date"] = "%s" % (stat_date['year'])

    return render(request, "home.html", context)

@login_required(login_url='/login/')
def review(request):
    request.session.setdefault("cal_date", today.as_dict())
    request.session.setdefault("review_date", today.as_dict())
    request.session.setdefault("stat_type", "monthly")
    request.session.setdefault("stat_date", today.as_dict())

    cal_date = request.session.get("cal_date")
    review_date = request.session.get("review_date")

    context = {}
    user = request.user

    # find any reviews already made
    try:
        currents = Day.objects.all().filter(user = user).filter(date = date_from_dict(review_date))
        current = currents[len(currents)-1]
    except:
        current = None

    # handle review form
    if request.method == "POST" and request.POST.get("review") == "":
        form = DayForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user

            # delete duplicates
            Day.objects.filter(date = review.date).delete()

            review.save()
            return redirect("/#calendar")
    
    # handle calendar 
    elif request.method == "POST":

        # if previous is clicked
        if request.POST.get("previous") == "":
            y = cal_date["year"]
            m = cal_date["month"]
            if m == 1:
                request.session["cal_date"] = Date(y-1, 12, 1).as_dict()
            else:
                request.session["cal_date"] = Date(y, m-1, 1).as_dict()
            return redirect("/review/#calendar")
        
        # if next is clicked
        if request.POST.get("next") == "":
            y = cal_date["year"]
            m = cal_date["month"]
            if m == 12:
                request.session["cal_date"] = Date(y+1, 1, 1).as_dict()
            else:
                request.session["cal_date"] = Date(y, m+1, 1).as_dict()
            return redirect("/review/#calendar")
        
        # if current is clicked
        if request.POST.get("current") == "":
            request.session["cal_date"] = Date.today().as_dict()
            return redirect("/review/#calendar")
        
        # if a day is clicked
        for day in range(1, 32):
            if request.POST.get(str(day)) == "":
                request.session["review_date"] = date_from_dict(cal_date).replace(day=day).as_dict()
                return redirect("/review/")

    # if no review exist of the day
    if current == None:
        context['form'] = DayForm(
            initial={
                'date': date_from_dict(review_date),
            }
        )
    else:
        context['form']= DayForm(
            initial={
                'mood': current.mood,
                'notes': current.notes,
                'emotions': current.emotions,
                'date': date_from_dict(review_date),
            }
        )

    context["calendar"] = Calendar(calendar.MONDAY).formatmonth(cal_date["year"], cal_date["month"], user)
    request.session["review_date"] = Date.today().as_dict()

    return render(request, "review.html", context)