
from django.contrib import admin
from .models import MoodEntry  # 导入你的模型

admin.site.register(MoodEntry)  # 注册模型