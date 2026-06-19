import os
from .models import MoodEntry
from datetime import date
from ml.config import EMOTION_TO_LABEL, LABEL_KEYS

# 定义记录文件路径（这里放在应用目录下，实际可根据需要调整路径）
DATA_FILE = os.path.join(os.path.dirname(__file__), 'mood_history.json')

def save_record(text, emotion_chinese):
    label = EMOTION_TO_LABEL.get(emotion_chinese)
    sentiment = LABEL_KEYS.get(label, 'calm')

    MoodEntry.objects.create(
        date=date.today(),
        text=text,
        sentiment=sentiment,
        emotion_label=label,
        mood_note=text
    )
