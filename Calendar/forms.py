import datetime
from django import forms
from Calendar.models import Day,EMOTION_CHOICES, MOOD_CHOICES


class DayForm(forms.ModelForm):
    
    mood = forms.CharField(
        label='Mood', 
        widget=forms.RadioSelect(choices=MOOD_CHOICES),
    )

    notes = forms.CharField(
        label="Notes", 
        required=False,
    )

    emotions = forms.MultipleChoiceField(
        label='Emotions', 
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=EMOTION_CHOICES,
    )

    date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}), 
        initial=datetime.date.today(),
    )

    class Meta:
        fields = ['mood', 'notes', 'emotions', 'date']
        exclude = ['user']
        model = Day
        widgets = {
            'date': forms.widgets.DateInput(attrs={'type': 'date'}),
        }

    def get(self, request):
        form = DayForm(forms.ModelForm)
        return form