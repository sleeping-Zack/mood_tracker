import matplotlib
matplotlib.use('Agg')
import os
import matplotlib.pyplot as plt
from django.conf import settings
from .models import MoodEntry
from django.shortcuts import render, redirect
from datetime import date
from .utils import load_records, save_record
from .sentiment_analysis import analyze_sentiment, generate_motivational_quote
def index(request):
    records = load_records()

    if request.method == 'POST':
        mood_text = request.POST.get('mood_note')
        if mood_text:
            # 情绪分析
            sentiment_result = analyze_sentiment(mood_text)  # 返回 'positive' 或 'negative'

            # 转换成中文情绪
            emotion = '积极' if sentiment_result == 'positive' else '消极'

            # 保存记录
            save_record(mood_text, emotion)

            # 为展示添加最新一条记录
            records.append({
                'date': date.today().strftime('%Y-%m-%d'),
                'text': mood_text,
                'emotion': emotion
            })

            return redirect('index')  # 提交后刷新页面，避免重复提交

    # 默认展示时，给出一个每日正能量语录
    quote = generate_motivational_quote('positive')  # 默认传 'positive'，防止出错

    return render(request, 'mood/index.html', {
        'records': records,
        'quote': quote,
    })
def generate_mood_trend():
    entries = MoodEntry.objects.all().order_by('date')
    if not entries:
        return  # 没有记录就不画图了

    dates = [entry.date for entry in entries]
    sentiments = [1 if entry.sentiment == 'positive' else 0 for entry in entries]

    plt.plot(dates, sentiments, marker='o', color='b', linestyle='-', markersize=5)
    plt.xlabel('Date')
    plt.ylabel('Sentiment (1=positive, 0=negative)')
    plt.title('Mood Trend')
    plt.xticks(rotation=45)
    plt.tight_layout()

    static_dir = os.path.join(settings.BASE_DIR, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    plt.savefig(os.path.join(static_dir, 'mood_trend.png'))
    plt.close()
