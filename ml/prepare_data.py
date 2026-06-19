import csv
import re
import sqlite3
import sys
from pathlib import Path

try:
    from ml.config import BASE_DIR, LABEL_HAPPY, LABEL_SAD, LABELED_DATA_PATH, RAW_DATA_PATH
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import BASE_DIR, LABEL_HAPPY, LABEL_SAD, LABELED_DATA_PATH, RAW_DATA_PATH


_CHNSENTICORP_ROWS = None


MANUAL_POSITIVE_SAMPLES = [
    "今天早八没有迟到，还顺利买到了早餐，心情很轻松。",
    "小组展示顺利结束，老师也肯定了我们的准备。",
    "复习计划按时完成，我对期末考试更有信心了。",
    "宿舍今晚很安静，我终于能好好看完一章书。",
    "跑步之后整个人清醒了很多，压力也散掉了一些。",
    "论文开题被导师夸思路清楚，我特别有动力。",
    "今天和朋友一起吃饭聊天，感觉被认真理解了。",
    "实验数据终于跑通了，之前的努力没有白费。",
    "社团活动办得很顺利，大家配合得很好。",
    "收到实习面试通知，感觉未来又亮了一点。",
    "图书馆的位置很舒服，下午学习效率特别高。",
    "今天完成了英语打卡，连续坚持让我很有成就感。",
    "和室友把矛盾说开了，心里一下子轻松很多。",
    "老师课后耐心解答了我的问题，我突然没那么慌了。",
    "答辩 PPT 改完以后，整个人都踏实了。",
    "今天的天气很好，走在校园里觉得很放松。",
    "收到家人的鼓励，感觉自己还能继续坚持。",
    "编程作业终于通过测试，我开心得想多学一会儿。",
    "早起背单词成功，感觉一天都有了好的开头。",
    "和同学一起复盘错题，很多知识点终于明白了。",
    "今天没有被 DDL 追着跑，节奏很稳定。",
    "篮球赛赢了，班里的气氛特别热闹。",
    "保研材料整理得差不多了，我心里更有底了。",
    "晚上散步时听到喜欢的歌，疲惫感少了很多。",
    "第一次主动提问被认真回应，我觉得自己更勇敢了。",
    "今天把拖了很久的报告写完了，特别畅快。",
    "导师说我的实验方向可以继续推进，我很受鼓舞。",
    "食堂新菜很好吃，普通的一天也有小惊喜。",
    "课上终于跟上老师的推导，心里很有成就感。",
    "今天复盘计划没有崩，感觉自己在慢慢变好。",
    "收到朋友送的小卡片，心里暖暖的。",
    "面试准备比昨天顺利，我对自己多了一点信任。",
    "晚自习效率不错，回宿舍时心情很平稳。",
    "今天把房间收拾干净，整个人都清爽了。",
    "实验室师兄帮我看代码，问题很快解决了。",
    "期中成绩比预想好，我觉得努力被看见了。",
    "参加讲座收获很大，突然对专业有了新的兴趣。",
    "今天按时睡觉按时起床，状态比前几天好多了。",
    "和朋友约好周末去看展，我开始期待休息日。",
    "运动会报名成功，感觉校园生活又丰富了一点。",
    "今天没有内耗，做完任务后安心休息了。",
    "老师表扬我的课堂分享，我开心了一整天。",
    "把错题整理完之后，焦虑明显少了。",
    "今天的咖啡很好喝，学习也变得没那么难熬。",
    "终于抢到想选的课，感觉运气站在我这边。",
    "组员主动分担任务，我觉得合作很舒服。",
    "晚上的校园风很温柔，心情也跟着变好了。",
    "收到奖学金通知，我觉得这学期的努力值得。",
    "今天把简历改到满意版本，心里很踏实。",
    "课程设计展示顺利通过，我终于可以松一口气。",
    "和家里视频后心情很好，感觉自己不是一个人在努力。",
    "今天读完一本书，内心很安静也很满足。",
    "实验报告提前提交，我第一次没有卡在截止前。",
    "晨跑时看到日出，觉得新的一天很值得期待。",
]

MANUAL_NEGATIVE_SAMPLES = [
    "今天早八迟到了，进教室时特别尴尬。",
    "小组作业没人回复消息，我一个人扛着很累。",
    "复习了一整晚还是不会做题，心里很挫败。",
    "宿舍太吵了，我根本没办法集中注意力。",
    "跑步时膝盖又疼了，计划被打断很烦。",
    "论文开题被指出很多问题，我一下子没了底气。",
    "今天和朋友聊天不太顺利，感觉自己被误解了。",
    "实验数据又失败了，我真的有点崩溃。",
    "社团活动临时出状况，我一直在补救。",
    "实习投了很多简历都没有回应，心里很失落。",
    "图书馆一直找不到座位，学习计划全乱了。",
    "英语打卡断掉了，觉得自己太没有毅力。",
    "和室友又因为卫生问题吵起来，心情很差。",
    "老师讲得太快，我整节课都跟不上。",
    "答辩 PPT 还没改完，想到明天就很焦虑。",
    "今天一直下雨，鞋子湿了，心情也很低落。",
    "家里催我做决定，我压力特别大。",
    "编程作业一直报错，我卡到想放弃。",
    "早上起不来，错过了原本安排好的复习时间。",
    "错题越整理越多，我开始怀疑自己学不会。",
    "DDL 堆在一起，我感觉快喘不过气。",
    "篮球赛输了，自己还失误很多，特别难受。",
    "保研材料还缺东西，我越整理越慌。",
    "晚上一个人回宿舍，突然觉得很孤单。",
    "课堂上不敢提问，怕自己问得太简单。",
    "报告拖到现在还没写完，我对自己很失望。",
    "导师否定了我的实验设计，我不知道怎么改。",
    "食堂排队太久，下午的安排全被打乱。",
    "课上公式完全没听懂，脑子一片空白。",
    "计划又崩了，我觉得自己一直在原地打转。",
    "朋友忘记了我们的约定，我有点难过。",
    "面试准备越看越焦虑，感觉自己什么都不会。",
    "晚自习效率很低，坐了三小时几乎没进展。",
    "房间很乱，我看着就更烦躁。",
    "代码问题找不到原因，整个人很无力。",
    "期中成绩比预想差，我心里很沉。",
    "讲座听不进去，觉得自己状态很糟糕。",
    "昨晚失眠，今天上课一直犯困。",
    "周末计划被临时取消，我很失望。",
    "运动会训练太累了，身体和情绪都撑不住。",
    "今天一直在内耗，什么都没做好。",
    "课堂分享讲砸了，我回想起来还是很难受。",
    "错题越改越烦，感觉压力没有减少。",
    "咖啡也救不了困意，我整天都很疲惫。",
    "没抢到想选的课，心情一下子跌下去。",
    "组员临时退出任务，我不知道该怎么补上。",
    "晚上的校园很冷，我一个人走得很压抑。",
    "奖学金没评上，虽然知道差距，但还是难过。",
    "简历改了很多遍还是不满意，越看越没信心。",
    "课程设计演示出了问题，我当场很慌。",
    "和家里视频后反而更想家，心里空落落的。",
    "书读不进去，注意力一直飘走。",
    "实验报告还没写完，截止时间越来越近。",
    "早上醒来就很疲惫，完全不想面对今天。",
    "今天被临时加任务，原来的安排全部乱掉。",
    "排练时被指出很多不足，我有点受打击。",
    "考试临近却复习不完，焦虑一直压在心口。",
]


def clean_line(text: str) -> str:
    text = re.sub(r"^\s*\d+[.、]\s*", "", str(text)).strip()
    text = text.strip("“”\"' ")
    return re.sub(r"\s+", " ", text)


def read_public_texts(limit: int = 80) -> list[str]:
    merged_path = BASE_DIR / "小红书" / "文案2" / "merged.txt"
    if not merged_path.exists():
        return []

    texts: list[str] = []
    for line in merged_path.read_text(encoding="utf-8-sig").splitlines():
        text = clean_line(line)
        if 4 <= len(text) <= 120 and text not in texts:
            texts.append(text)
        if len(texts) >= limit:
            break
    return texts


def read_hotel_review_rows() -> list[dict[str, object]]:
    global _CHNSENTICORP_ROWS
    if _CHNSENTICORP_ROWS is not None:
        return _CHNSENTICORP_ROWS

    try:
        from datasets import load_dataset
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "缺少 datasets 依赖，请先执行: python -m pip install datasets"
        ) from exc

    dataset = load_dataset("dirtycomputer/ChnSentiCorp_htl_all")
    rows: list[dict[str, object]] = []
    for split_name, split_data in dataset.items():
        for index, item in enumerate(split_data):
            text = str(item.get("review", "")).strip()
            if not text:
                continue
            source_label = int(item["label"])
            if source_label == 0:
                label = LABEL_SAD
            elif source_label == 1:
                label = LABEL_HAPPY
            else:
                continue
            rows.append(
                {
                    "text": text,
                    "label": label,
                    "source": "chnsenticorp_htl_all",
                    "split": "",
                    "notes": f"dirtycomputer/ChnSentiCorp_htl_all; original_split={split_name}; row={index}",
                }
            )
    _CHNSENTICORP_ROWS = rows
    return rows


def read_diary_rows() -> list[dict[str, str]]:
    db_path = BASE_DIR / "db.sqlite3"
    if not db_path.exists():
        return []

    rows: list[dict[str, str]] = []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        try:
            records = conn.execute(
                "SELECT id, date, text, sentiment FROM mood_moodentry ORDER BY id"
            ).fetchall()
        except sqlite3.DatabaseError:
            return []

    for row in records:
        rows.append(
            {
                "text": str(row["text"]).strip(),
                "source": "diary",
                "original_label": str(row["sentiment"]).strip(),
                "notes": f"mood_moodentry.id={row['id']}; date={row['date']}",
            }
        )
    return rows


def build_raw_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_hotel_review_rows():
        rows.append(
            {
                "text": row["text"],
                "source": row["source"],
                "original_label": str(row["label"]),
                "notes": row["notes"],
            }
        )

    rows.extend(read_diary_rows())
    for text in read_public_texts():
        rows.append(
            {
                "text": text,
                "source": "public",
                "original_label": "",
                "notes": "public short text supplement; requires manual review before training",
            }
        )
    return rows


def build_labeled_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()

    for row in read_hotel_review_rows():
        text = str(row["text"]).strip()
        if not text or text in seen:
            continue
        rows.append(row)
        seen.add(text)

    for row in read_diary_rows():
        text = row["text"]
        sentiment = row["original_label"]
        if not text or text in seen:
            continue
        if sentiment == "happy" and "奴才" not in text:
            label = LABEL_HAPPY
        elif sentiment == "sad":
            label = LABEL_SAD
        else:
            continue
        rows.append(
            {
                "text": text,
                "label": label,
                "source": "diary",
                "split": "",
                "notes": row["notes"],
            }
        )
        seen.add(text)

    for text in MANUAL_POSITIVE_SAMPLES:
        if text not in seen:
            rows.append(
                {
                    "text": text,
                    "label": LABEL_HAPPY,
                    "source": "manual",
                    "split": "",
                    "notes": "campus diary expression; rule-labeled happy",
                }
            )
            seen.add(text)

    for text in MANUAL_NEGATIVE_SAMPLES:
        if text not in seen:
            rows.append(
                {
                    "text": text,
                    "label": LABEL_SAD,
                    "source": "manual",
                    "split": "",
                    "notes": "campus diary expression; rule-labeled sad",
                }
            )
            seen.add(text)

    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    raw_rows = build_raw_rows()
    labeled_rows = build_labeled_rows()

    write_csv(
        RAW_DATA_PATH,
        raw_rows,
        fieldnames=["text", "source", "original_label", "notes"],
    )
    write_csv(
        LABELED_DATA_PATH,
        labeled_rows,
        fieldnames=["text", "label", "source", "split", "notes"],
    )

    happy_count = sum(1 for row in labeled_rows if row["label"] == LABEL_HAPPY)
    sad_count = sum(1 for row in labeled_rows if row["label"] == LABEL_SAD)
    print(f"raw_rows={len(raw_rows)}")
    print(f"labeled_rows={len(labeled_rows)}")
    print(f"happy={happy_count}")
    print(f"sad={sad_count}")
    print(f"raw_path={RAW_DATA_PATH}")
    print(f"labeled_path={LABELED_DATA_PATH}")


if __name__ == "__main__":
    main()
