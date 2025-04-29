import os
from .models import MoodEntry
from datetime import date
# 定义记录文件路径（这里放在应用目录下，实际可根据需要调整路径）
DATA_FILE = os.path.join(os.path.dirname(__file__), 'mood_history.json')

def save_record(text, emotion_chinese):
    # 将中文情绪转换为英文
    sentiment_map = {
        '积极': 'positive',
        '消极': 'negative'
    }
    sentiment = sentiment_map.get(emotion_chinese, 'neutral')  # 默认中性

    MoodEntry.objects.create(
        date=date.today(),
        sentiment=sentiment,
        mood_note=text
    )