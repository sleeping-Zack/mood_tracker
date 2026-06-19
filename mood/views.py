import os
from datetime import date

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from django.conf import settings
from django.shortcuts import redirect, render

from ml.predict import predict_emotion

from .models import MoodEntry
from .sentiment_analysis import generate_motivational_quote


def index(request):
    quote = None
    latest_result = None
    latest_error = None

    if request.method == 'POST':
        mood_text = request.POST.get('mood_note', '').strip()
        if mood_text:
            result = predict_emotion(mood_text)
            if result['label'] is None:
                request.session['last_error'] = result['message']
                return redirect('index')
            entry = MoodEntry.objects.create(
                date=date.today(),
                text=mood_text,
                mood_note=mood_text,
                sentiment=result['sentiment'],
                emotion_label=result['label'],
                model_name=result['model_name'],
                analysis_message=result['message'],
            )
            request.session['last_entry_id'] = entry.id
            return redirect('index')

    last_entry_id = request.session.pop('last_entry_id', None)
    if last_entry_id:
        latest_result = MoodEntry.objects.filter(id=last_entry_id).first()
    latest_error = request.session.pop('last_error', None)

    latest = MoodEntry.objects.order_by('-analyzed_at', '-id').first()
    latest_emotion = latest.sentiment if latest else 'happy'
    quote = generate_motivational_quote(latest_emotion)

    generate_mood_trend()
    records = MoodEntry.objects.all().order_by('-analyzed_at', '-id')
    return render(
        request,
        'mood/index.html',
        {
            'records': records,
            'quote': quote,
            'latest_result': latest_result,
            'latest_error': latest_error,
        },
    )


def generate_mood_trend():
    entries = MoodEntry.objects.all().order_by('date', 'id')
    if not entries:
        return

    dates = [entry.date for entry in entries]
    scores = [entry.display_score for entry in entries]

    plt.figure(figsize=(7, 4))
    plt.plot(dates, scores, marker='o', color='#2f5f8f', linestyle='-', markersize=5)
    plt.axhline(0, color='#bbbbbb', linewidth=0.8)
    plt.xlabel('Date')
    plt.ylabel('Mood Score (-2=sad/angry, -1=anxious, 0=calm, 2=happy)')
    plt.title('Mood Trend')
    plt.xticks(rotation=45)
    plt.ylim(-2.2, 2.2)
    plt.tight_layout()

    static_dir = os.path.join(settings.BASE_DIR, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    plt.savefig(os.path.join(static_dir, 'mood_trend.png'))
    plt.close()
