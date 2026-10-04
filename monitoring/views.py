from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

import json
import os
import joblib
import pandas as pd

from .models import (
    MoodEntry,
    SleepEntry,
    JournalEntry,
    StressEntry,
    BreathingEntry,
    FacialExpression,
    HeartRateEntry,
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

    facial_expressions = FacialExpression.objects.filter(
        user=request.user
    ).order_by('-created_at')

    heart_rates = HeartRateEntry.objects.filter(
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

    model_path = os.path.join(
        settings.BASE_DIR,
        'ai_model',
        'distress_model.pkl'
    )

    dashboard_distress_level = 'Model not trained yet'

    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)

            if moods:
                mood_values = {
                    'very_sad': 1,
                    'sad': 2,
                    'okay': 3,
                    'good': 4,
                    'excellent': 5,
                }

                dashboard_mood = mood_values.get(
                    moods[0].mood,
                    3
                )
            else:
                dashboard_mood = 3

            if sleeps:
                dashboard_sleep_hours = sleeps[0].hours
                dashboard_sleep_quality = sleeps[0].quality
            else:
                dashboard_sleep_hours = 7
                dashboard_sleep_quality = 3

            if stresses:
                dashboard_stress_score = stresses[0].score
            else:
                dashboard_stress_score = 10

            if journals:
                dashboard_journal_sentiment = journals[0].sentiment_score

                if dashboard_journal_sentiment is None:
                    dashboard_journal_sentiment = 0

                if dashboard_journal_sentiment > 0:
                    dashboard_journal_sentiment = 1
                elif dashboard_journal_sentiment < 0:
                    dashboard_journal_sentiment = -1
                else:
                    dashboard_journal_sentiment = 0
            else:
                dashboard_journal_sentiment = 0

            if facial_expressions:
                expression = facial_expressions[0].expression.lower()

                if expression in ['happy', 'surprise']:
                    dashboard_facial_expression = 5
                elif expression == 'neutral':
                    dashboard_facial_expression = 3
                elif expression in ['sad', 'fear', 'angry', 'disgust']:
                    dashboard_facial_expression = 1
                else:
                    dashboard_facial_expression = 3
            else:
                dashboard_facial_expression = 3

            if heart_rates:
                dashboard_heart_rate = heart_rates[0].heart_rate
            else:
                dashboard_heart_rate = 75

            dashboard_input = pd.DataFrame([
                {
                    'mood': dashboard_mood,
                    'sleep_hours': dashboard_sleep_hours,
                    'sleep_quality': dashboard_sleep_quality,
                    'stress_score': dashboard_stress_score,
                    'journal_sentiment': dashboard_journal_sentiment,
                    'facial_expression': dashboard_facial_expression,
                    'heart_rate': dashboard_heart_rate,
                }
            ])

            dashboard_prediction = model.predict(
                dashboard_input
            )[0]

            if dashboard_prediction == 0:
                dashboard_distress_level = 'Low'
            elif dashboard_prediction == 1:
                dashboard_distress_level = 'Moderate'
            else:
                dashboard_distress_level = 'High'

        except Exception:
            dashboard_distress_level = 'Prediction unavailable'

    context = {
        'moods': moods,
        'sleeps': sleeps,
        'journals': journals,
        'stresses': stresses,
        'breathings': breathings,
        'facial_expressions': facial_expressions,
        'heart_rates': heart_rates,
        'wellness_score': wellness_score,
        'wellness_status': wellness_status,
        'dashboard_distress_level': dashboard_distress_level,
    }

    return render(
        request,
        'monitoring/dashboard.html',
        context
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


@login_required
def heart_rate(request):
    if request.method == "POST":
        heart_rate = request.POST.get("heart_rate")

        if heart_rate and heart_rate.isdigit():
            heart_rate = int(heart_rate)

            if 30 <= heart_rate <= 220:
                HeartRateEntry.objects.create(
                    user=request.user,
                    heart_rate=heart_rate
                )

                return redirect("heart_rate")

    heart_rates = HeartRateEntry.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "monitoring/heart_rate.html",
        {
            "heart_rates": heart_rates
        }
    )


@login_required
def heart_rate_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            heart_rate = data.get("heart_rate")

            if heart_rate is not None:
                heart_rate = int(heart_rate)

                if 30 <= heart_rate <= 220:
                    HeartRateEntry.objects.create(
                        user=request.user,
                        heart_rate=heart_rate
                    )

                    return JsonResponse({
                        "message": "Heart rate saved",
                        "heart_rate": heart_rate
                    })

        except (ValueError, TypeError, json.JSONDecodeError):
            pass

        return JsonResponse({
            "message": "Invalid heart rate"
        }, status=400)

    return JsonResponse({
        "message": "Only POST requests are allowed"
    }, status=405)


@login_required
def distress_prediction(request):
    model_path = os.path.join(
        settings.BASE_DIR,
        'ai_model',
        'distress_model.pkl'
    )

    if not os.path.exists(model_path):
        return render(
            request,
            'monitoring/distress_prediction.html',
            {
                'distress_level': 'Model not trained yet',
                'mood': 3,
                'sleep_hours': 7,
                'sleep_quality': 3,
                'stress_score': 10,
                'journal_sentiment': 0,
                'facial_expression': 3,
                'heart_rate': 75
            }
        )

    model = joblib.load(model_path)

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

    facial_expressions = FacialExpression.objects.filter(
        user=request.user
    ).order_by('-created_at')

    heart_rates = HeartRateEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    if moods:
        mood_values = {
            'very_sad': 1,
            'sad': 2,
            'okay': 3,
            'good': 4,
            'excellent': 5,
        }

        mood = mood_values.get(
            moods[0].mood,
            3
        )
    else:
        mood = 3

    if sleeps:
        sleep_hours = sleeps[0].hours
        sleep_quality = sleeps[0].quality
    else:
        sleep_hours = 7
        sleep_quality = 3

    if stresses:
        stress_score = stresses[0].score
    else:
        stress_score = 10

    if journals:
        journal_sentiment = journals[0].sentiment_score

        if journal_sentiment is None:
            journal_sentiment = 0

        if journal_sentiment > 0:
            journal_sentiment = 1
        elif journal_sentiment < 0:
            journal_sentiment = -1
        else:
            journal_sentiment = 0
    else:
        journal_sentiment = 0

    if facial_expressions:
        expression = facial_expressions[0].expression.lower()

        if expression in ['happy', 'surprise']:
            facial_expression = 5
        elif expression == 'neutral':
            facial_expression = 3
        elif expression in ['sad', 'fear', 'angry', 'disgust']:
            facial_expression = 1
        else:
            facial_expression = 3
    else:
        facial_expression = 3

    if heart_rates:
        heart_rate = heart_rates[0].heart_rate
    else:
        heart_rate = 75

    input_data = pd.DataFrame([
        {
            'mood': mood,
            'sleep_hours': sleep_hours,
            'sleep_quality': sleep_quality,
            'stress_score': stress_score,
            'journal_sentiment': journal_sentiment,
            'facial_expression': facial_expression,
            'heart_rate': heart_rate,
        }
    ])

    prediction = model.predict(
        input_data
    )[0]

    if prediction == 0:
        distress_level = 'Low'
    elif prediction == 1:
        distress_level = 'Moderate'
    else:
        distress_level = 'High'

    return render(
        request,
        'monitoring/distress_prediction.html',
        {
            'distress_level': distress_level,
            'mood': mood,
            'sleep_hours': sleep_hours,
            'sleep_quality': sleep_quality,
            'stress_score': stress_score,
            'journal_sentiment': journal_sentiment,
            'facial_expression': facial_expression,
            'heart_rate': heart_rate
        }
    )