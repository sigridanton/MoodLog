from calendar import HTMLCalendar, day_abbr, month_name
import datetime
from django.db import models
from Calendar.models import Day

year = 2023
month = 5

class Date():
    def __init__(self, day, month, year) -> None:
        self.day = day
        self.month = month
        self.year = year

class Calendar(HTMLCalendar):
    def __init__(self, firstweekday: int = 0) -> None:
        super().__init__(firstweekday)

    def formatday(self, day: int, weekday: int, user) -> str:
        if day == 0 or user == None:
            mood = 0
        else:
            try:
                days = Day.objects.all().filter(user = user).filter(date = datetime.date(year, month, day))
                mood = days[len(days)-1].mood
            except:
                mood = 0
        #string = r"{% static 'images/six.png' %}"
        if mood == "0":
            color = "white"
        elif mood == "1":
            color = "#0C3F0D"
        elif mood == "2":
            color = "#448936"
        elif mood == "3":
            color = "#6DB25E"
        elif mood == "4":
            color = "#A2CF8A"
        elif mood == "5":
            color= "#C9E079"
        elif mood == "6":
            color = "#EBEC76"
        elif mood == "7":
            color = "#F0E456"
        else:
            color = "white"

        #<img src="%s" width = "100" height = "auto" alt="">

        if day == 0:
            num = ""
        else:
            num = str(day)
        
        return '<td class="%s" bgcolor="%s"><button class="daybt" type="submit" name="%s">%s</td>' % (self.cssclasses[weekday], color, num, num)
    
    def formatweek(self, theweek, user):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, user) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s
    
    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="%s"><div class="p2">%s</div></th>' % (
            self.cssclasses_weekday_head[day], day_abbr[day])

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr>%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        prevbt = '<button type="submit" name="previous" class="previous">Previous</button>'
        nextbt = '<button type="submit" name="next" class="next">Next</button>'
        currentbt = '<button type="submit" name="current" class="current">Current</button>'
        return '<tr><th colspan="7" class="%s"><div class="p">%s%s%s</div>%s</th></tr>' % (self.cssclass_month_head, prevbt, s, nextbt, currentbt)
    
    def formatmonth(self, theyear, themonth, user, withyear=True):
        """
        Return a formatted month as a table.
        """
        global year
        global month
        year = theyear
        month = themonth
        v = []
        a = v.append
        a('<table border="0" cellpadding="20" cellspacing="0" class="%s">' % (
            self.cssclass_month))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, user))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)