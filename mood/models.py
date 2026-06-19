from django.db import models
from django.utils import timezone

try:
    from ml.config import (
        LABEL_KEYS,
        LABEL_KEY_TO_LABEL,
        LABEL_NAMES,
        TREND_SCORE,
    )
except Exception:
    LABEL_NAMES = {0: '难过', 1: '焦虑', 2: '生气', 3: '平静', 4: '开心'}
    LABEL_KEYS = {0: 'sad', 1: 'anxious', 2: 'angry', 3: 'calm', 4: 'happy'}
    LABEL_KEY_TO_LABEL = {emotion_key: label for label, emotion_key in LABEL_KEYS.items()}
    TREND_SCORE = {0: -2, 1: -1, 2: -2, 3: 0, 4: 2}


class MoodEntry(models.Model):
    SENTIMENT_CHOICES = [
        ('sad', '难过'),
        ('anxious', '焦虑'),
        ('angry', '生气'),
        ('calm', '平静'),
        ('happy', '开心'),
    ]
    EMOTION_LABEL_CHOICES = [
        (0, '难过 (sad)'),
        (1, '焦虑 (anxious)'),
        (2, '生气 (angry)'),
        (3, '平静 (calm)'),
        (4, '开心 (happy)'),
    ]
    date = models.DateField()
    text = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    mood_note = models.TextField()
    emotion_label = models.IntegerField(choices=EMOTION_LABEL_CHOICES, null=True, blank=True)
    score = models.IntegerField(default=0)
    model_name = models.CharField(max_length=80, blank=True, default='')
    analysis_message = models.CharField(max_length=255, blank=True, default='')
    analyzed_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        label = self.emotion_label
        if isinstance(label, int) and label in TREND_SCORE:
            self.score = TREND_SCORE[label]
            self.sentiment = LABEL_KEYS[label]
        elif self.sentiment in LABEL_KEY_TO_LABEL:
            label = LABEL_KEY_TO_LABEL[self.sentiment]
            self.emotion_label = label
            self.score = TREND_SCORE[label]
        super().save(*args, **kwargs)

    @property
    def emotion_text(self):
        label = self.emotion_label
        if isinstance(label, int) and label in LABEL_NAMES:
            return LABEL_NAMES[label]
        if self.sentiment in LABEL_KEY_TO_LABEL:
            return LABEL_NAMES[LABEL_KEY_TO_LABEL[self.sentiment]]
        return '未知'

    @property
    def display_score(self):
        label = self.emotion_label
        if isinstance(label, int) and label in TREND_SCORE:
            return TREND_SCORE[label]
        if self.sentiment in LABEL_KEY_TO_LABEL:
            return TREND_SCORE[LABEL_KEY_TO_LABEL[self.sentiment]]
        return 0

    def __str__(self):
        return f'{self.date}: {self.text} ({self.emotion_text})'
