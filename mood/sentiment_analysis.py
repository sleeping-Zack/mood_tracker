from transformers import pipeline
import random
import time
# 加载 HuggingFace 的 BERT 情感分析模型
# 明确指定模型名称和版本
sentiment_analyzer = pipeline(
    task="sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    revision="714eb0f"  # 指定git commit hash
)
def analyze_sentiment(text):
    """
    使用 BERT 模型进行情绪分析
    返回 'positive' 或 'negative'
    """
    result = sentiment_analyzer(text)
    sentiment_label = result[0]['label'].upper()  # 确保大写（如 'NEGATIVE'）
    sentiment_score = result[0]['score']
    print(f"[DEBUG] 文本: '{text}' | 标签: {sentiment_label} | 置信度: {sentiment_score:.2f}")
    # 设置置信度阈值
    confidence_threshold = 0.5

    if sentiment_label == 'POSITIVE' and sentiment_score >= confidence_threshold:
        return 'positive'
    elif sentiment_label == 'NEGATIVE' and sentiment_score >= confidence_threshold:
        return 'negative'
    else:
        return 'neutral'  # 低置信度或模型不确定时返回中性
def generate_motivational_quote(sentiment):
    random.seed(time.time())
    positive_quotes = [
        "今天又是充满希望的一天！",
        "今天，做一个快乐的人！"
    ]
    negative_quotes = [
        "负面的情绪只是暂时的，积极的心态才是长久的力量。",
        "不管今天有多难，明天一定会更好！",
        "你的坚持会带来更好的明天！"
    ]
    neutral_quotes = [
        "平凡的日子里，也能找到小确幸。",
        "放慢脚步，感受当下的宁静。"
    ]

    if sentiment == 'positive':
        return random.choice(positive_quotes)
    elif sentiment == 'negative':
        return random.choice(negative_quotes)
    else:
        return random.choice(neutral_quotes)