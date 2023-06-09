from __future__ import unicode_literals

from multiselectfield import MultiSelectField

from django.db import models
from django.conf import settings

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

MOOD_CHOICES = [
    ("0", "none"),
    ("1", "very bad"),
    ("2", "bad"),
    ("3", "meh"),
    ("4", "fine"),
    ("5", "okay"),
    ("6", "good"),
    ("7", "very good"),
]

class Day(models.Model):

    mood = models.CharField(
        max_length=1,
        choices=MOOD_CHOICES,
    )

    notes = models.CharField(max_length=500)

    emotions = MultiSelectField(
        max_length=100,
        choices=EMOTION_CHOICES
    )

    date = models.DateField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )