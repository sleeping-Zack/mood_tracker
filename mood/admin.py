
from django.contrib import admin
from .models import MoodEntry  # 导入你的模型

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'text',
        'sentiment',
        'emotion_label',
        'score',
        'model_name',
        'analyzed_at',
    )
    list_filter = ('sentiment', 'emotion_label', 'model_name')
    search_fields = ('text', 'analysis_message')
