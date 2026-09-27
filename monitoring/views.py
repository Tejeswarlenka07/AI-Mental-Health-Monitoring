from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import (
    MoodEntry,
    SleepEntry,
    JournalEntry,
    StressEntry,
    BreathingEntry
)

from textblob import TextBlob


@login_required
def dashboard(request):

    moods = MoodEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    sleeps = SleepEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    journals = JournalEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    stresses = StressEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    breathings = BreathingEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    wellness_score = 0

    if moods:

        latest_mood = moods[0].mood

        if latest_mood == 'excellent':
            wellness_score += 25

        elif latest_mood == 'good':
            wellness_score += 20

        elif latest_mood == 'okay':
            wellness_score += 15

        elif latest_mood == 'sad':
            wellness_score += 8

        else:
            wellness_score += 3

    if sleeps:

        latest_sleep = sleeps[0].hours

        if 7 <= latest_sleep <= 9:
            wellness_score += 25

        elif 6 <= latest_sleep < 7 or 9 < latest_sleep <= 10:
            wellness_score += 20

        elif 5 <= latest_sleep < 6:
            wellness_score += 12

        else:
            wellness_score += 5

    if stresses:

        latest_stress = stresses[0].level

        if latest_stress == 'low':
            wellness_score += 30

        elif latest_stress == 'moderate':
            wellness_score += 18

        else:
            wellness_score += 5

    if breathings:
        wellness_score += 20

    if wellness_score >= 75:
        wellness_status = 'Good'

    elif wellness_score >= 50:
        wellness_status = 'Moderate'

    else:
        wellness_status = 'Needs Attention'

    return render(
        request,
        'monitoring/dashboard.html',
        {
            'moods': moods,
            'sleeps': sleeps,
            'journals': journals,
            'stresses': stresses,
            'breathings': breathings,
            'wellness_score': wellness_score,
            'wellness_status': wellness_status
        }
    )


def mood(request):
    return render(
        request,
        'monitoring/mood.html'
    )


@login_required
def sleep(request):

    if request.method == 'POST':

        hours = request.POST.get('hours')
        quality = request.POST.get('quality')

        SleepEntry.objects.create(
            user=request.user,
            hours=hours,
            quality=quality
        )

        return redirect('sleep')

    sleeps = SleepEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'monitoring/sleep.html',
        {
            'sleeps': sleeps
        }
    )


@login_required
def journal(request):

    if request.method == 'POST':

        title = request.POST.get('title')
        content = request.POST.get('content')

        result = TextBlob(content)

        polarity = result.sentiment.polarity

        if polarity > 0:
            sentiment = 'Positive'

        elif polarity < 0:
            sentiment = 'Negative'

        else:
            sentiment = 'Neutral'

        JournalEntry.objects.create(
            user=request.user,
            title=title,
            content=content,
            sentiment=sentiment,
            sentiment_score=polarity
        )

        return redirect('journal')

    journals = JournalEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'monitoring/journal.html',
        {
            'journals': journals
        }
    )


@login_required
def stress(request):

    if request.method == 'POST':

        score = 0

        for i in range(1, 11):

            answer = request.POST.get(f'q{i}')
            score += int(answer)

        if score <= 10:
            level = 'low'

        elif score <= 20:
            level = 'moderate'

        else:
            level = 'high'

        StressEntry.objects.create(
            user=request.user,
            score=score,
            level=level
        )

        return render(
            request,
            'monitoring/stress_result.html',
            {
                'score': score,
                'level': level
            }
        )

    return render(
        request,
        'monitoring/stress.html'
    )


@login_required
def breathing(request):

    if request.method == 'POST':

        BreathingEntry.objects.create(
            user=request.user,
            duration=5
        )

        return redirect('breathing')

    breathings = BreathingEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'monitoring/breathing.html',
        {
            'breathings': breathings
        }
    )


def home(request):
    return render(
        request,
        'home.html'
    )


    