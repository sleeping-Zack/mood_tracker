from django.db import models

class MoodEntry(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),  # 新增中性选项
    ]
    date = models.DateField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)  # 使用选项约束
    mood_note = models.TextField()
    def __str__(self):
        return f'{self.date}: {self.sentiment}'
