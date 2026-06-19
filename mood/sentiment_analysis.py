import random
import time

try:
    from ml.config import LABEL_KEYS, LABEL_KEY_TO_LABEL, LABEL_NAMES
except Exception:
    LABEL_KEYS = {0: "sad", 1: "anxious", 2: "angry", 3: "calm", 4: "happy"}
    LABEL_KEY_TO_LABEL = {emotion_key: label for label, emotion_key in LABEL_KEYS.items()}
    LABEL_NAMES = {0: "难过", 1: "焦虑", 2: "生气", 3: "平静", 4: "开心"}


_QUOTES = {
    "sad": [
        "难过的时候，先允许自己慢一点。",
        "今天不必急着振作，照顾好自己也很重要。",
        "情绪低落不是失败，只是在提醒你需要休息。",
        "请对现在的自己温柔一点。",
    ],
    "anxious": [
        "先把事情拆成一小步，完成眼前这一件就好。",
        "焦虑常常来自事情太大，先抓住最紧迫的一项。",
        "深呼吸一下，任务可以排队，不必一起压过来。",
        "你不用一次解决全部问题，先处理可执行的第一步。",
    ],
    "angry": [
        "先暂停几分钟，等情绪降下来再决定怎么回应。",
        "烦躁的时候，离开现场一下也算是在保护自己。",
        "把火气写下来，再决定哪些真的需要处理。",
        "今天先稳住节奏，不让坏情绪替你做决定。",
    ],
    "calm": [
        "平稳也是一种好状态，可以慢慢把事情往前推。",
        "普通的一天也有价值，按自己的节奏来。",
        "情绪稳定时，适合做一点需要专注的小事。",
        "今天不用追求很特别，平平稳稳就很好。",
    ],
    "happy": [
        "把这份好状态记下来，它会成为之后的能量。",
        "今天的顺利值得被认真看见。",
        "继续保持这个节奏，把开心留给重要的事。",
        "有成就感的时候，也别忘了肯定自己。",
    ],
}


def _normalize_emotion_key(emotion) -> str:
    if isinstance(emotion, int):
        return LABEL_KEYS.get(emotion, "calm")
    emotion = str(emotion or "").strip()
    if emotion in LABEL_KEY_TO_LABEL:
        return emotion
    for label, name in LABEL_NAMES.items():
        if emotion == name:
            return LABEL_KEYS[label]
    return "calm"


def generate_motivational_quote(emotion) -> str:
    random.seed(time.time())
    emotion_key = _normalize_emotion_key(emotion)
    return random.choice(_QUOTES[emotion_key])
