from django.db import models
from django.contrib.auth.models import User


class MoodEntry(models.Model):

    MOOD_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('okay', 'Okay'),
        ('sad', 'Sad'),
        ('very_sad', 'Very Sad'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES
    )

    note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.mood}"


class SleepEntry(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    hours = models.FloatField()

    quality = models.IntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.hours} hours"

class JournalEntry(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    content = models.TextField()

    sentiment = models.CharField(
        max_length=20,
        blank=True
    )

    sentiment_score = models.FloatField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
        

class StressEntry(models.Model):

    STRESS_LEVELS = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    score = models.IntegerField()

    level = models.CharField(
        max_length=20,
        choices=STRESS_LEVELS
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.level}"

class BreathingEntry(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    duration = models.IntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.duration} minutes"

class FacialExpression(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expression = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.expression


class HeartRateEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heart_rate = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.heart_rate} BPM"    
class Recommendation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    distress_level = models.CharField(
        max_length=20
    )

    recommendation = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username + " - " + self.distress_level    
    