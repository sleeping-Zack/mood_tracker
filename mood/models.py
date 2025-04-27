from django.db import models

class MoodEntry(models.Model):
    date = models.DateField()
    sentiment = models.CharField(max_length=10)  # 'positive' 或 'negative'
    mood_note = models.TextField()  # 用户输入的心情记录

    def __str__(self):
        return f'{self.date}: {self.sentiment}'
