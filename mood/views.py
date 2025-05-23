import matplotlib
matplotlib.use('Agg')
import os
import matplotlib.pyplot as plt
from django.conf import settings
from .models import MoodEntry
from django.shortcuts import render, redirect
from datetime import date
from .sentiment_analysis import analyze_sentiment, generate_motivational_quote

def index(request):
    generate_mood_trend()
    records = MoodEntry.objects.all().order_by('-date')  # 从数据库获取所有记录，并按日期降序排列
    quote = None

    if request.method == 'POST':
        mood_text = request.POST.get('mood_note')
        if mood_text:
            sentiment_result = analyze_sentiment(mood_text)

            if sentiment_result == 'positive':
                emotion = 'positive'
            elif sentiment_result == 'negative':
                emotion = 'negative'
            else:
                emotion = 'neutral'  # 处理中性情况
            # 保存记录到数据库
            MoodEntry.objects.create(
                date=date.today(),
                text=mood_text,
                sentiment=emotion
            )
            quote = generate_motivational_quote(sentiment_result)
            return redirect('index')

    if not quote:
        latest_sentiment = MoodEntry.objects.last().sentiment if MoodEntry.objects.exists() else 'positive'
        quote = generate_motivational_quote(latest_sentiment)

    return render(request, 'mood/index.html', {
        'records': records,
        'quote': quote,
    })


def generate_mood_trend():
    entries = MoodEntry.objects.all().order_by('date')
    if not entries:
        return

    dates = [entry.date for entry in entries]

    # 根据情绪类型赋值：positive=1, neutral=0.5, negative=0
    sentiments = []
    for entry in entries:
        if entry.sentiment == 'positive':
            sentiments.append(1)
        elif entry.sentiment == 'neutral':
            sentiments.append(0.5)
        else:
            sentiments.append(0)

    plt.figure()
    plt.plot(dates, sentiments, marker='o', color='b', linestyle='-', markersize=5)
    plt.xlabel('Date')
    plt.ylabel('Sentiment (1=positive, 0.5=neutral, 0=negative)')
    plt.title('Mood Trend')
    plt.xticks(rotation=45)
    plt.ylim(-0.1, 1.1)  # 设置y轴范围更美观
    plt.tight_layout()

    static_dir = os.path.join(settings.BASE_DIR, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    plt.savefig(os.path.join(static_dir, 'mood_trend.png'))
    plt.close()