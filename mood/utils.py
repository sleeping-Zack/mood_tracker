import json, os
from datetime import date

# 定义记录文件路径（这里放在应用目录下，实际可根据需要调整路径）
DATA_FILE = os.path.join(os.path.dirname(__file__), 'mood_history.json')

def load_records():
    """读取历史记录并返回列表；如果文件不存在或无效，则返回空列表。"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_record(text, sentiment):
    """将一条新的记录追加到 JSON 文件。记录包含当前日期、心情文字和情绪。"""
    records = load_records()
    record = {
        'date': date.today().strftime('%Y-%m-%d'),
        'text': text,
        'sentiment': sentiment
    }
    records.append(record)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)
