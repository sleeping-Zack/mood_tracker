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
        "今天又是崭新的一天，好运正在路上！",
        "你的笑容是世界上最美的风景～",
        "保持热爱，奔赴下一场山海！",
        "你正在成为自己想成为的人，超棒的！",
        "今天的阳光和你一样灿烂！",
        "小事也能带来快乐，比如一杯咖啡、一朵花。",
        "你的存在让这个世界多了一份可爱！",
        "去做让你眼睛发光的事吧！",
        "每一天都是礼物，拆开它，里面藏着惊喜。",
        "你积极的样子，真的超有感染力！",
        "生活偶尔偏心，把糖都撒给了你～",
        "你的能量，足够改变今天的一切！",
        "今天也要做自己的小太阳呀！",
        "快乐会传染，而你是源头！",
        "宇宙正在悄悄帮你实现愿望呢！",
        "你走过的每一步，都在靠近更好的自己。",
        "微风、阳光、好心情——今天三连击！",
        "你值得所有美好，就像春天值得花开。",
        "把普通的日子过成纪念日，你就是生活的艺术家！"
        "你的努力，时间都看得见。",
        "今天的目标：比昨天更快乐一点！",
        "世界很大，但你独一无二。",
        "好运藏在你的自律和善良里。",
        "今天会发生一件让你微笑的小事！",
        "你是自己人生剧本里最耀眼的主角！",
        "向前走，前方有无数种可能等你解锁。",
        "你的好心情，就是今天的VIP通行证！",
        "生活偶尔淘气，但对你偏爱有加～",
        "保持这份热情，你会点亮更多角落！",
        "今天的你，是未来最年轻的你——尽情享受吧！",
        "今天，做一个快乐的人！"
    ]
    negative_quotes = [
        "我知道你现在很累，但请记得，你从来都不是一个人。",
        "难过没关系，我会陪你慢慢等乌云散开。",
        "你不必总是坚强，想哭就哭吧，眼泪也是疗愈的一部分。",
        "这个世界偶尔对你不好，不是你的错。",
        "低谷只是暂时的，你值得更好的明天。",
        "如果现在看不到光，那就先做自己的光。",
        "你的感受很重要，我愿意认真听你说。",
        "慢慢来，有些伤口需要时间，我会等你。",
        "你已经做得很好了，真的。",
        "你不是失败，你只是在学习如何成功。",
        "累了就休息，但别放弃——你比想象中更强大。",
        "黑暗中的每一步，都在带你靠近黎明。",
        "别人怎么看不重要，你永远是自己人生的主角。",
        "有些事无法改变，但你可以温柔对待自己。",
        "你现在的挣扎，未来会变成你的故事。",
        "心碎的感觉很痛，但破碎的地方会生出新的勇气。",
        "不必强迫自己立刻好起来，疗愈没有截止日期。",
        "你不需要完美，你的存在本身就有意义。",
        "如果今天很难，那就先过好这一分钟。",
        "我会接住你所有的情绪，它们并不可怕。",
        "你走过的路，哪怕曲折，也都算数。",
        "你没有被生活打败，你只是在蓄力。",
        "你的价值从不取决于某件事的结果。",
        "天空不会永远下雨，你也不会永远难过。",
        "有些人只是路过你的生命，不值得你掉眼泪。",
        "你害怕的未来，可能比你想象的更温柔。",
        "深呼吸，这一刻的艰难只是人生的一页。",
        "你值得被爱，尤其在你觉得自己最糟糕的时候。",
        "痛苦不是弱点，而是你曾勇敢付出的证明。",
        "我会一直在这里，无论晴天还是雨天。"
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