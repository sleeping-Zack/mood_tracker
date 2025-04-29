from django.db import models

class MoodEntry(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),  # 新增中性选项
    ]
    date = models.DateField()
    text = models.TextField()  # 确保有 'text' 字段，用于存储心情文本
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)  # 使用选项约束
    mood_note = models.TextField()

    def __str__(self):
        return f'{self.date}: {self.text} ({self.sentiment})' # 修改 __str__ 方法