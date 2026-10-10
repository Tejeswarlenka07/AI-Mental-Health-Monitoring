from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

import json
import os
import joblib
import pandas as pd

from textblob import TextBlob

from .models import (
    MoodEntry,
    SleepEntry,
    JournalEntry,
    StressEntry,
    BreathingEntry,
    FacialExpression,
    HeartRateEntry,
    Recommendation,
)


@login_required
def dashboard(request):
    moods = MoodEntry.objects.filter(user=request.user).order_by('-created_at')[:10]
    sleeps = SleepEntry.objects.filter(user=request.user).order_by('-created_at')[:10]
    journals = JournalEntry.objects.filter(user=request.user).order_by('-created_at')[:10]
    stresses = StressEntry.objects.filter(user=request.user).order_by('-created_at')[:10]
    breathings = BreathingEntry.objects.filter(user=request.user).order_by('-created_at')[:10]
    facial_expressions = FacialExpression.objects.filter(user=request.user).order_by('-created_at')[:10]
    heart_rates = HeartRateEntry.objects.filter(user=request.user).order_by('-created_at')[:10]

    latest_mood = moods[0] if moods else None
    latest_sleep = sleeps[0] if sleeps else None
    latest_stress = stresses[0] if stresses else None
    latest_breathing = breathings[0] if breathings else None
    latest_journal = journals[0] if journals else None
    latest_facial = facial_expressions[0] if facial_expressions else None
    latest_heart_rate = heart_rates[0] if heart_rates else None

    # ---------- Wellness score ----------
    wellness_score = 0

    if latest_mood:
        mood_scores = {
            'excellent': 25,
            'good': 20,
            'okay': 15,
            'sad': 10,
            'very_sad': 5,
        }
        wellness_score += mood_scores.get(latest_mood.mood, 0)

    if latest_sleep:
        if latest_sleep.hours >= 7:
            wellness_score += 25
        elif latest_sleep.hours >= 6:
            wellness_score += 20
        elif latest_sleep.hours >= 5:
            wellness_score += 10

    if latest_stress:
        if latest_stress.score <= 10:
            wellness_score += 30
        elif latest_stress.score <= 20:
            wellness_score += 20
        else:
            wellness_score += 10

    if latest_breathing:
        wellness_score += 20

    if wellness_score >= 75:
        wellness_status = "Good"
    elif wellness_score >= 50:
        wellness_status = "Moderate"
    else:
        wellness_status = "Needs Attention"

    # ---------- Model input defaults ----------
    prediction = "Prediction unavailable"

    model_path = os.path.join(settings.BASE_DIR, 'ai_model', 'distress_model.pkl')

    mood = 3
    sleep_hours = 7
    sleep_quality = 3
    stress_score = 10
    journal_sentiment = 0
    facial_expression = 3
    heart_rate = 75

    if latest_mood:
        mood_map = {
            'excellent': 5,
            'good': 4,
            'okay': 3,
            'sad': 2,
            'very_sad': 1,
        }
        mood = mood_map.get(latest_mood.mood, 3)

    if latest_sleep:
        sleep_hours = float(latest_sleep.hours)
        sleep_quality = int(latest_sleep.quality)

    if latest_stress:
        stress_score = latest_stress.score

    if latest_journal:
        journal_sentiment = TextBlob(latest_journal.content).sentiment.polarity

    if latest_facial:
        expression_map = {
            'happy': 5,
            'surprise': 5,
            'neutral': 3,
            'sad': 1,
            'fear': 1,
            'angry': 1,
            'disgust': 1,
        }
        facial_expression = expression_map.get(latest_facial.expression.lower(), 3)

    if latest_heart_rate:
        heart_rate = latest_heart_rate.heart_rate

    # ---------- AI prediction ----------
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)

            data = pd.DataFrame([{
                'mood': mood,
                'sleep_hours': sleep_hours,
                'sleep_quality': sleep_quality,
                'stress_score': stress_score,
                'journal_sentiment': journal_sentiment,
                'facial_expression': facial_expression,
                'heart_rate': heart_rate,
            }])

            result = model.predict(data)[0]

            if result == 0:
                prediction = "Low Distress"
            elif result == 1:
                prediction = "Moderate Distress"
            else:
                prediction = "High Distress"

        except Exception:
            prediction = "Prediction unavailable"

    # ---------- Recommendations ----------
    recommendations_list = []

    if latest_mood and latest_mood.mood in ['sad', 'very_sad']:
        recommendations_list.append(
            'Try a relaxing activity such as listening to music, taking a walk, or talking to someone you trust.'
        )

    if sleep_hours < 6:
        recommendations_list.append(
            'Your sleep duration is low. Try maintaining a regular sleep schedule and aim for 7 to 9 hours of sleep.'
        )

    if stress_score > 20:
        recommendations_list.append(
            'Your stress level is high. Try the breathing exercise and take short breaks during the day.'
        )
    elif stress_score > 10:
        recommendations_list.append(
            'Your stress level is moderate. Practice relaxation or breathing exercises regularly.'
        )

    if journal_sentiment < 0:
        recommendations_list.append(
            'Your recent journal entry appears negative. Continue writing your thoughts and consider talking to someone you trust.'
        )

    if latest_facial:
        expression = latest_facial.expression.lower()
        if expression in ['sad', 'fear', 'angry', 'disgust']:
            recommendations_list.append(
                'Your recent facial expression indicates possible negative emotions. Take some time to relax and talk to someone you trust if needed.'
            )

    if heart_rate > 100:
        recommendations_list.append(
            'Your recent heart rate is elevated. Rest for a while and try slow, controlled breathing.'
        )

    if prediction == 'High Distress':
        recommendations_list.append(
            'Your current AI distress prediction is high. Consider taking a break, practicing relaxation, and talking to a trusted person or qualified mental-health professional if distress continues.'
        )
    elif prediction == 'Moderate Distress':
        recommendations_list.append(
            'Your current AI distress prediction is moderate. Focus on sleep, relaxation, breathing exercises, and regular self-monitoring.'
        )
    elif prediction == 'Low Distress':
        recommendations_list.append(
            'Your current AI distress prediction is low. Continue maintaining your healthy daily routine.'
        )

    if not recommendations_list:
        recommendations_list.append(
            'Continue monitoring your mood, sleep, stress, journal, facial expression, and heart rate regularly.'
        )

    return render(
        request,
        'monitoring/dashboard.html',
        {
            'moods': moods,
            'sleeps': sleeps,
            'journals': journals,
            'stresses': stresses,
            'breathings': breathings,
            'facial_expressions': facial_expressions,
            'heart_rates': heart_rates,
            'wellness_score': wellness_score,
            'wellness_status': wellness_status,
            'prediction': prediction,
            'dashboard_distress_level': prediction,
            'recommendations': recommendations_list,
        },
    )


def mood(request):
    return render(request, 'monitoring/mood.html')


@login_required
def sleep(request):
    if request.method == 'POST':
        hours = request.POST.get('hours')
        quality = request.POST.get('quality')

        SleepEntry.objects.create(
            user=request.user,
            hours=hours,
            quality=quality,
        )

        return redirect('sleep')

    sleeps = SleepEntry.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'monitoring/sleep.html', {'sleeps': sleeps})


@login_required
def journal(request):
    if request.method == 'POST':
        content = request.POST.get('content')

        analysis = TextBlob(content)
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            sentiment = 'Positive'
        elif polarity < 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        JournalEntry.objects.create(
            user=request.user,
            content=content,
            sentiment=sentiment,
        )

        return redirect('journal')

    journals = JournalEntry.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'monitoring/journal.html', {'journals': journals})


@login_required
def stress(request):
    if request.method == 'POST':
        score = 0

        for i in range(1, 11):
            answer = request.POST.get(f'q{i}', '0')
            score += int(answer)

        if score <= 10:
            level = 'Low'
        elif score <= 20:
            level = 'Moderate'
        else:
            level = 'High'

        StressEntry.objects.create(
            user=request.user,
            score=score,
            level=level,
        )

        return render(
            request,
            'monitoring/stress_result.html',
            {'score': score, 'level': level},
        )

    return render(request, 'monitoring/stress.html')


@login_required
def breathing(request):
    if request.method == 'POST':
        BreathingEntry.objects.create(user=request.user, duration=5)
        return redirect('breathing')

    breathings = BreathingEntry.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'monitoring/breathing.html', {'breathings': breathings})


def home(request):
    return render(request, 'home.html')


@login_required
def heart_rate(request):
    if request.method == 'POST':
        heart_rate_value = request.POST.get('heart_rate')

        if heart_rate_value and heart_rate_value.isdigit():
            heart_rate_value = int(heart_rate_value)

            if 30 <= heart_rate_value <= 220:
                HeartRateEntry.objects.create(
                    user=request.user,
                    heart_rate=heart_rate_value,
                )

        return redirect('heart_rate')

    heart_rates = HeartRateEntry.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'monitoring/heart_rate.html', {'heart_rates': heart_rates})


@login_required
def heart_rate_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            heart_rate_value = data.get('heart_rate')

            if heart_rate_value is not None:
                heart_rate_value = int(heart_rate_value)

                if 30 <= heart_rate_value <= 220:
                    HeartRateEntry.objects.create(
                        user=request.user,
                        heart_rate=heart_rate_value,
                    )

                    return JsonResponse({
                        'status': 'success',
                        'heart_rate': heart_rate_value,
                    })

                return JsonResponse({
                    'status': 'error',
                    'message': 'Heart rate must be between 30 and 220 BPM.',
                }, status=400)

        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid heart rate data.',
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed.',
    }, status=405)


@login_required
def distress_prediction(request):
    latest_mood = MoodEntry.objects.filter(user=request.user).order_by('-created_at').first()
    latest_sleep = SleepEntry.objects.filter(user=request.user).order_by('-created_at').first()
    latest_stress = StressEntry.objects.filter(user=request.user).order_by('-created_at').first()
    latest_journal = JournalEntry.objects.filter(user=request.user).order_by('-created_at').first()
    latest_facial = FacialExpression.objects.filter(user=request.user).order_by('-created_at').first()
    latest_heart_rate = HeartRateEntry.objects.filter(user=request.user).order_by('-created_at').first()

    mood = 3
    sleep_hours = 7
    sleep_quality = 3
    stress_score = 10
    journal_sentiment = 0
    facial_expression = 3
    heart_rate = 75

    if latest_mood:
        mood_map = {
            'excellent': 5,
            'good': 4,
            'okay': 3,
            'sad': 2,
            'very_sad': 1,
        }
        mood = mood_map.get(latest_mood.mood, 3)

    if latest_sleep:
        sleep_hours = float(latest_sleep.hours)
        sleep_quality = int(latest_sleep.quality)

    if latest_stress:
        stress_score = latest_stress.score

    if latest_journal:
        journal_sentiment = TextBlob(latest_journal.content).sentiment.polarity

    if latest_facial:
        expression_map = {
            'happy': 5,
            'surprise': 5,
            'neutral': 3,
            'sad': 1,
            'fear': 1,
            'angry': 1,
            'disgust': 1,
        }
        facial_expression = expression_map.get(latest_facial.expression.lower(), 3)

    if latest_heart_rate:
        heart_rate = latest_heart_rate.heart_rate

    model_path = os.path.join(settings.BASE_DIR, 'ai_model', 'distress_model.pkl')

    prediction = 'Prediction unavailable'

    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)

            data = pd.DataFrame([{
                'mood': mood,
                'sleep_hours': sleep_hours,
                'sleep_quality': sleep_quality,
                'stress_score': stress_score,
                'journal_sentiment': journal_sentiment,
                'facial_expression': facial_expression,
                'heart_rate': heart_rate,
            }])

            result = model.predict(data)[0]

            if result == 0:
                prediction = 'Low Distress'
            elif result == 1:
                prediction = 'Moderate Distress'
            else:
                prediction = 'High Distress'

        except Exception:
            prediction = 'Prediction unavailable'

    return render(
        request,
        'monitoring/distress_prediction.html',
        {
            'prediction': prediction,
            'mood': mood,
            'sleep_hours': sleep_hours,
            'sleep_quality': sleep_quality,
            'stress_score': stress_score,
            'journal_sentiment': journal_sentiment,
            'facial_expression': facial_expression,
            'heart_rate': heart_rate,
        },
    )


@login_required
def recommendations(request):
    latest_mood = MoodEntry.objects.filter(user=request.user).order_by('-created_at').first()
    latest_sleep = SleepEntry.objects.filter(user=request.user).order_by('-created_at').first()
    latest_journal = JournalEntry.objects.filter(user=request.user).order_by('-created_at').first()
    latest_stress = StressEntry.objects.filter(user=request.user).order_by('-created_at').first()
    latest_facial = FacialExpression.objects.filter(user=request.user).order_by('-created_at').first()
    latest_heart_rate = HeartRateEntry.objects.filter(user=request.user).order_by('-created_at').first()

    recommendations_list = []

    mood = 'okay'
    sleep_hours = 7
    stress_score = 10
    journal_sentiment = 0
    expression = 'neutral'
    heart_rate = 75

    if latest_mood:
        mood = latest_mood.mood

    if latest_sleep:
        sleep_hours = float(latest_sleep.hours)

    if latest_stress:
        stress_score = latest_stress.score

    if latest_journal:
        journal_sentiment = TextBlob(latest_journal.content).sentiment.polarity

    if latest_facial:
        expression = latest_facial.expression.lower()

    if latest_heart_rate:
        heart_rate = latest_heart_rate.heart_rate

    if mood in ['sad', 'very_sad']:
        recommendations_list.append(
            'Try a relaxing activity such as listening to music, taking a walk, or talking to someone you trust.'
        )

    if sleep_hours < 6:
        recommendations_list.append(
            'Your sleep duration is low. Try maintaining a regular sleep schedule and aim for 7 to 9 hours of sleep.'
        )

    if stress_score > 20:
        recommendations_list.append(
            'Your stress level is high. Try the breathing exercise and take short breaks during the day.'
        )
    elif stress_score > 10:
        recommendations_list.append(
            'Your stress level is moderate. Practice relaxation or breathing exercises regularly.'
        )

    if journal_sentiment < 0:
        recommendations_list.append(
            'Your recent journal entry appears negative. Continue writing your thoughts and consider talking to someone you trust.'
        )

    if expression in ['sad', 'fear', 'angry', 'disgust']:
        recommendations_list.append(
            'Your recent facial expression indicates possible negative emotions. Take some time to relax and talk to someone you trust if needed.'
        )

    if heart_rate > 100:
        recommendations_list.append(
            'Your recent heart rate is elevated. Rest for a while and try slow, controlled breathing.'
        )

    if (
        sleep_hours >= 7
        and stress_score <= 10
        and mood in ['excellent', 'good']
    ):
        recommendations_list.append(
            'Your recent wellness indicators look positive. Continue your healthy sleep, relaxation, and daily wellness routine.'
        )

    if not recommendations_list:
        recommendations_list.append(
            'Continue monitoring your mood, sleep, stress, journal, facial expression, and heart rate regularly.'
        )

    distress_level = 'Low'

    if stress_score > 20 or mood == 'very_sad':
        distress_level = 'High'
    elif stress_score > 10 or mood == 'sad':
        distress_level = 'Moderate'

    if heart_rate > 100:
        distress_level = 'High'

    for recommendation in recommendations_list:
        Recommendation.objects.create(
            user=request.user,
            distress_level=distress_level,
            recommendation=recommendation,
        )

    return render(
        request,
        'monitoring/recommendations.html',
        {
            'recommendations': recommendations_list,
            'mood': mood,
            'sleep_hours': sleep_hours,
            'stress_score': stress_score,
            'journal_sentiment': journal_sentiment,
            'expression': expression,
            'heart_rate': heart_rate,
            'distress_level': distress_level,
        },
    )


@login_required
def recommendation_history(request):
    recommendation_history = Recommendation.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'monitoring/recommendation_history.html',
        {'recommendation_history': recommendation_history},
    )


@login_required
def delete_recommendation(request, id):
    recommendation = Recommendation.objects.get(id=id, user=request.user)

    if request.method == 'POST':
        recommendation.delete()

    return redirect('recommendation_history')


@login_required
def clear_recommendation_history(request):
    if request.method == 'POST':
        Recommendation.objects.filter(user=request.user).delete()

    return redirect('recommendation_history')


@login_required
def facial_expression(request):
    if request.method == 'POST':
        expression = request.POST.get('expression')

        if expression:
            FacialExpression.objects.create(
                user=request.user,
                expression=expression,
            )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

        return redirect('facial_expression')

    facial_expressions = FacialExpression.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'monitoring/facial_expression.html',
        {'facial_expressions': facial_expressions},
    )
