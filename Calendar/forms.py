import datetime
from django import forms
from Calendar.models import Day


class DayForm(forms.ModelForm):
    # mood =
    MOOD_CHOICES = [
        ("1", "1: very bad"),
        ("2", "2: bad"),
        ("3", "3: meh"),
        ("4", "4: fine"),
        ("5", "5: okay"),
        ("6", "6: good"),
        ("7", "7: very good"),
    ]
    EMOTION_CHOICES = [
        ("1", "Happy"),
        ("2", "Excited"),
        ("3", "Proud"),
        ("4", "Relaxed"),
        ("5", "Laughative"),
        ("6", "Neutral"),
        ("7", "Sad"),
        ("8", "Angry"),
        ("9", "Annoyed"),
        ("10", "Depressed"),
        ("11", "Stressed"),
        ("12", "Tired"),
        ("13", "Anxious"),
        ("14", "Lonely"),
    ]
    #mood = forms.ChoiceField(
    #    widget=forms.RadioSelect,
    #    choices=CHOICES,
    #)

    mood = forms.CharField(label='Mood', widget=forms.RadioSelect(choices=MOOD_CHOICES))
    notes = forms.CharField(label="Notes")
    emotions = forms.CharField(label='Mood', widget=forms.RadioSelect(choices=EMOTION_CHOICES))
    date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), initial=datetime.date.today())

    class Meta:
        fields = ['mood', 'notes', 'emotions', 'date']
        model = Day
        widgets = {
            'date': forms.widgets.DateInput(attrs={'type': 'date'})
        }

    def get(self, request):
        form = DayForm(forms.ModelForm)
        return form