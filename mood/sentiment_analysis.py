from transformers import pipeline
import random

# 加载 HuggingFace 的 BERT 情感分析模型
sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    """
    使用 BERT 模型进行情绪分析
    返回 'positive' 或 'negative'
    """
    result = sentiment_analyzer(text)
    sentiment = result[0]['label']  # 'POSITIVE' 或 'NEGATIVE'

    if sentiment == 'POSITIVE':
        return 'positive'
    else:
        return 'negative'

def generate_motivational_quote(sentiment):
    """
    根据情绪生成一句励志语录
    """
    positive_quotes = [
        "今天又是充满希望的一天！",
        "无论昨天多么艰难，今天依然充满阳光！",
        "今天，做一个快乐的人！"
    ]
    negative_quotes = [
        "负面的情绪只是暂时的，积极的心态才是长久的力量。",
        "不管今天有多难，明天一定会更好！",
        "你的坚持会带来更好的明天！"
    ]

    if sentiment == 'positive':
        return random.choice(positive_quotes)
    else:
        return random.choice(negative_quotes)
