"""Build the 5-class emotion training corpus.

Pipeline:
1. Pull `zzhdbw/Simplified_Chinese_Multi-Emotion_Dialogue_Dataset` and map its
   emotion labels into the project's 5-class schema (drop unsupported classes).
2. Generate a fresh batch of campus / student-diary anxiety samples because the
   public dataset has no anxiety class.
3. Merge in the few historical diary entries from db.sqlite3 when they already
   carry a 5-class label or 5-class emotion key.
4. Deduplicate by text and write the unified labeled corpus.
5. Add `manual_balanced_augment` rows (default 200 per class) for training diversity.

The output keeps the schema requested by the upgrade plan:
    text, label, emotion, source, split, notes
"""

from __future__ import annotations

import csv
import sqlite3
import sys
from pathlib import Path
from itertools import product
from typing import Iterable

try:
    from ml.config import (
        ALL_LABELS,
        BASE_DIR,
        EMOTION_TO_LABEL,
        LABEL_ANGRY,
        LABEL_ANXIOUS,
        LABEL_CALM,
        LABEL_HAPPY,
        LABEL_KEY_TO_LABEL,
        LABEL_NAMES,
        LABEL_SAD,
        LABELED_DATA_PATH,
        RAW_DATA_PATH,
    )
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import (
        ALL_LABELS,
        BASE_DIR,
        EMOTION_TO_LABEL,
        LABEL_ANGRY,
        LABEL_ANXIOUS,
        LABEL_CALM,
        LABEL_HAPPY,
        LABEL_KEY_TO_LABEL,
        LABEL_NAMES,
        LABEL_SAD,
        LABELED_DATA_PATH,
        RAW_DATA_PATH,
    )


HF_DATASET_NAME = "zzhdbw/Simplified_Chinese_Multi-Emotion_Dialogue_Dataset"

ORIGINAL_LABEL_TO_FIVECLASS = {
    "开心": LABEL_HAPPY,
    "伤心": LABEL_SAD,
    "生气": LABEL_ANGRY,
    "厌恶": LABEL_ANGRY,
    "平静": LABEL_CALM,
    "焦虑": LABEL_ANXIOUS,
    "恐惧": LABEL_ANXIOUS,
    "担心": LABEL_ANXIOUS,
    "害怕": LABEL_ANXIOUS,
    "紧张": LABEL_ANXIOUS,
}

DROP_ORIGINAL_LABELS = {"惊讶", "关心", "疑问"}


def load_hf_rows() -> list[dict[str, object]]:
    try:
        from datasets import load_dataset
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "缺少 datasets 依赖，请先执行: python -m pip install datasets"
        ) from exc

    dataset = load_dataset(HF_DATASET_NAME)
    rows: list[dict[str, object]] = []
    for split_name, split_data in dataset.items():
        for index, item in enumerate(split_data):
            text = str(item.get("text", "")).strip()
            raw_label = str(item.get("label", "")).strip()
            if not text or not raw_label:
                continue
            if raw_label in DROP_ORIGINAL_LABELS:
                continue
            mapped_label = ORIGINAL_LABEL_TO_FIVECLASS.get(raw_label)
            if mapped_label is None:
                continue
            rows.append(
                {
                    "text": text,
                    "label": mapped_label,
                    "emotion": LABEL_NAMES[mapped_label],
                    "source": "multi_emotion_dialogue",
                    "split": "",
                    "notes": (
                        f"{HF_DATASET_NAME}; original_label={raw_label}; "
                        f"original_split={split_name}; row={index}"
                    ),
                }
            )
    return rows


_BASE_ANXIOUS_SAMPLES = [
    "明天就要期末考试了，复习还差三章，心里特别慌。",
    "答辩 PPT 还有一半没改完，越想越焦虑。",
    "项目 DDL 在三天后，但我一行核心代码都还没动。",
    "老师下午要检查实验进度，我现在脑子一片空白。",
    "课程汇报临近，我担心自己讲得不够清楚。",
    "实习简历还没投出去，怕错过校招最佳时间。",
    "数学作业全是难题，做了两小时还是没头绪。",
    "代码报错改不出来，越改越乱，担心来不及交。",
    "保研材料缺一份证明，怕赶不上系里截止时间。",
    "明天要交课程设计文档，可我连大纲都没写好。",
    "答辩在即，PPT 动效一直崩，心里特别紧张。",
    "项目组员临时换需求，时间根本来不及调整。",
    "晚上要交实验报告，但实验数据还没整理出来。",
    "复习计划严重落后，我开始怀疑能不能及格。",
    "明天实验课要演示，演练了两次都卡壳，很慌。",
    "导师给的 deadline 要到了，我还没拿到关键结果。",
    "课程设计的核心算法还没写完，我整夜睡不好。",
    "面试题刷不完了，怕明天技术面会被问倒。",
    "PPT 改到第七稿还是不满意，时间在一分一秒过。",
    "期中考试不到一周，我连第一遍复习都没看完。",
    "组员消息回得慢，我一个人扛 PPT 心里特别着急。",
    "明天要给导师汇报进度，我现在还没把数据跑出来。",
    "保研面试只剩一周，我对自己的项目讲不清楚。",
    "课题组明天开会，我怕被问到一个我答不上的问题。",
    "数学课的习题册才写到第三章，期末却快到了。",
    "项目代码越写越乱，我开始怕重构来不及。",
    "DDL 越来越近，可我这两天状态非常差。",
    "复习时间不够用了，每翻一页都觉得心跳快。",
    "实验仪器一直故障，进度推后我已经急到失眠。",
    "毕设老师要看初稿，但我连框架都没想清楚。",
    "今天又通宵改 PPT，越熬越焦虑。",
    "明早八点交作业，我现在还差最后一题没头绪。",
    "助教要查代码风格，我担心被打回重写。",
    "明天小组答辩，我怕组员临时掉链子。",
    "课程考试改成开卷我反而更慌，因为题量很大。",
    "我盯着屏幕半小时一行字都没写出来，焦虑感越来越重。",
    "讨论班轮到我汇报，我担心讲到一半就被打断追问。",
    "考前一周我才发现重点根本没复习对，特别懊恼。",
    "PPT 字体调不好，时间在流逝，我越改越烦躁。",
    "答辩老师据说很严，我担心被现场质疑。",
    "明天要面试实习，我紧张得连昨晚都没睡好。",
    "课程设计被打回重做，我担心赶不上重交时间。",
    "项目周会前一天，我数据完全不对劲，心里很慌。",
    "代码 bug 改不动，我担心连最低分都拿不到。",
    "组员一直没回消息，我担心晚上交不出 PPT。",
    "复习清单没完成一半，我焦虑到吃不下饭。",
    "PPT 模板被推翻，我得重做，时间根本不够。",
    "明天的英语口试我一句完整的回答都说不利索。",
    "导师让我两小时内回复修改意见，但我还没看完。",
    "项目的接口又出问题，我担心赶不上集成。",
    "考研倒计时进入两位数，我每天都在追问自己来不来得及。",
    "实验报告已经超期一天，我每分钟都在焦虑。",
    "导师让我重写文献综述，我很怕通不过。",
    "代码部署失败，我害怕赶不上演示。",
    "毕业要求多了一项，我担心自己达不到。",
    "助教的批改群一直在催，我心慌到打字都打错。",
    "我担心明天上课被点名回答，怕答得很差。",
    "PPT 检查时发现一处大错，我现在不知道从哪改起。",
    "导师提的修改意见太多，我担心一晚上改不完。",
    "组长说今天要交版本，我才发现我这部分没合并好。",
    "我担心毕设答辩老师会问我没准备的问题。",
    "明天要 demo，但环境一直配不上，焦虑得手都在抖。",
    "课程作业要求改了，我担心已经写的部分要全推翻。",
    "考研真题做错一大半，我开始怀疑自己来不来得及。",
    "毕设流程图导师不满意，要我今晚重画。",
    "项目跑出来的结果完全偏离预期，我心里很慌。",
    "周会的 PPT 还没整理结论，我怕被点出来。",
    "图书馆复习一整天没进展，越坐越焦虑。",
    "项目的关键模块还没合并完，我怕明天验收。",
    "答辩前一天我反复练讲，越练越担心讲不清逻辑。",
    "课程的实验数据丢了，我担心要重新跑一周。",
    "复试名单临近公布，我每天都心神不宁。",
    "我担心今晚通宵也写不完报告。",
    "演示前 30 分钟代码崩了，我心都凉了一半。",
    "我担心组队答辩时其他人发挥得比我好。",
    "明天考试我重点都没看完，越翻越慌。",
    "项目的实验对比图一直跑不出来，我担心交不上。",
    "实习面试连续被拒，我开始焦虑找不到岗位。",
    "导师要的进展报告还没动笔，我已经心虚得不行。",
    "明天就交毕业设计，我打开文档脑子还是空的。",
    "课题进度被同组的快了一截，我有点慌。",
    "明天的展示我只练过两遍，担心讲不连贯。",
    "课程作业互评打分被扣，我担心成绩拉不上来。",
    "项目验收要交三份文档，我现在只完成了一份。",
    "周报每周都拖到最后一刻，我担心被导师注意到。",
    "明天是答辩日，今天才发现一个数据有错，整个人很慌。",
    "我担心明天试讲发挥不好，被同组看出来准备不足。",
    "课程设计代码一直跑不通，我担心赶不上提交。",
    "毕业论文外审还没回来，我每天都在等结果，很煎熬。",
    "考研倒计时三十天，我做的卷子分数还在波动，不踏实。",
    "答辩老师据说会问数据细节，我已经开始失眠。",
    "毕设演示需要现场跑代码，我担心服务器连不上。",
    "周末两天要把 PPT 全部改完，时间根本不够。",
    "答辩前我反复演练，但越练越觉得逻辑不顺。",
    "毕业设计的模型评估还没做完，我担心来不及补。",
    "数学复习卡在第六章，我担心后面追不回来。",
    "项目里的接口文档要重写，我怕周一交不出来。",
    "导师的回信说要大改，我担心剩下时间根本不够。",
    "课程报告检测重复率超标了，我担心拿不到分。",
    "实验数据量不够，我担心结论站不住脚。",
    "明天要交开题报告初稿，我现在还在改第二章。",
    "项目的关键人临时请假，我担心整个进度往后推。",
    "面试材料我准备了三天，临到投递我还是一直犹豫。",
    "实验里的关键指标没达标，我担心被导师批评。",
    "毕业论文的查重结果不理想，我担心要返工。",
    "线上答辩工具一直卡顿，我担心轮到自己时直接掉线。",
    "一想到期末周快到了，我就控制不住地担心自己会挂科。",
    "期末周已经来了，可我还有四门没开始复习，担心挂科。",
    "这门课重点全没看，我担心自己撑不过期末周。",
    "我一直担心自己会挂科，吃饭都没什么胃口。",
    "考前一周我开始失眠，怕一觉醒来已经来不及。",
    "成绩快出来了，我控制不住地担心自己挂科。",
    "我担心自己这门挂了要重修，整夜睡不安稳。",
    "期末分数线公布在即，我紧张得手心出汗。",
    "听说这门课通过率很低，我担心自己拿不到学分。",
    "想到要补考我就胸闷，担心一直担心。",
    "我担心自己绩点掉到保研线以下。",
    "期末周一到，我就开始焦虑，连去食堂都没心情。",
    "复习时间剩三天，重点书还没翻过，担心来不及。",
    "我担心自己挂科被家里知道，越想越睡不着。",
    "考研还有两个月，但我还在第一轮，担心自己赶不上。",
    "笔试成绩明天出，我控制不住地刷新页面。",
    "导师在催进度，我担心自己达不到他的要求。",
    "组会要汇报数据，我担心自己讲到一半就被打断。",
    "课程实验失败了三次，我担心今晚还是跑不出来。",
    "面试结果还没消息，我心一直悬着，担心被刷掉。",
    "中期检查在下周，我担心自己拿不出像样的成果。",
    "我控制不住地反复检查邮件，担心错过老师的通知。",
    "考试周连着五场，我担心自己撑不下来。",
    "答辩名单一公布我就开始紧张，担心被排在最后。",
    "我担心自己 GPA 掉得太厉害，前面的努力都白费了。",
    "查重率还没出，我担心自己要被打回重写。",
    "我一边复习一边担心自己看的方向不对。",
    "明天就是补考日，我担心再挂一次。",
    "心里压在那的不是某一件事，是怕全部都做不完。",
    "我控制不住地想最坏的结果，越想越睡不着。",
    "我担心自己在答辩现场说不出话。",
    "学分够不够保研线我都不敢算，越算越焦虑。",
    "周末有三个 DDL 撞在一起，我担心做不完。",
    "我担心自己说错话，整个人在汇报现场都僵住了。",
    "课程论文投稿截止前一天，我担心格式还出错。",
    "我担心自己请假被扣勤分，还得想办法补回来。",
    "导师让我重写引言，我担心还是过不了关。",
    "我担心明天早八点会迟到，整夜都在看手机。",
    "项目验收快到了，我担心自己写的模块跑不起来。",
    "最近期末任务太多，项目也没做完，心里压力很大。",
    "项目还有三个模块没做完，心里压力很大，根本睡不着。",
    "这周任务太多，每件事都还没收尾，心里一直压着块石头。",
    "项目临近交付，但我手上还有四个 bug 没解决，压力很大。",
    "这学期任务一个接一个，根本喘不过气，心里压力越积越大。",
    "课程项目任务都堆在一起，我没做完一项，新的又来了，压力很大。",
    "最近事情太多了，项目论文都没动，心里很慌。",
    "项目没做完、复习也没开始，我感觉时间根本不够用。",
    "项目代码还有一半没写，DDL 在三天后，心里特别有压力。",
    "项目延期已经第二周了，我心里一直压着事，根本静不下来。",
    "上周的任务还没收尾，这周又派下来新的，心里压力很大。",
    "课程项目没做完，老师又要进度报告，我整个人都很紧绷。",
    "最近事多得离谱，项目、论文、报告都赶不完，压力大到失眠。",
    "项目交付前夜还有一堆没完成，心里很急很慌。",
    "压力大到一闭眼就想到没做完的项目，根本睡不安稳。",
    "今天加班到十点项目还是没做完，心里压力大得头皮发麻。",
    "课程项目和实习同时进行，我怕两边都做不完。",
    "明天就要交项目方案了，关键章节还没开写，压力很大。",
    "项目接口没接通，演示就在后天，我心里很慌。",
    "最近压力大到吃不下饭，项目和论文一项都没真正完成。",
    "项目周报又要交了，我这周进度几乎为零，心里慌得不行。",
    "实验室项目堆了一堆，我连基本的复现都没跑完，压力巨大。",
    "组员都各忙各的，整个项目压在我一个人身上，心里压力很大。",
    "这次项目要交两个版本，我连第一版都没做完，心里压力很大。",
    "心里压力大到胸口发闷，项目还没出实验结果。",
    "最近什么任务都没完成，越想越焦虑，越焦虑越不想动。",
    "项目截止还有 48 小时，但我代码还在改 bug，心里压力很大。",
    "事情太多压在一起，我有点喘不过气，项目也是一直拖着。",
    "课程项目要做演示我还没准备 PPT，加上没做完心里压力很大。",
    "三个项目并行赶，我已经分不清优先级了，心里压力很大。",
]


def _generate_anxious_template_samples() -> list[str]:
    triggers = [
        "期末考试",
        "期中考试",
        "期末周",
        "课程答辩",
        "毕设答辩",
        "毕业设计",
        "项目验收",
        "课程汇报",
        "PPT",
        "实验报告",
        "课程设计",
        "实习面试",
        "考研复习",
        "代码作业",
        "数学作业",
        "组会汇报",
        "导师周报",
        "挂科补考",
    ]
    feelings = [
        "我心里特别慌，怕赶不上 DDL。",
        "我反复想都觉得时间不够。",
        "我担心做不完，整夜睡不着。",
        "我心跳快、手在抖，根本静不下来。",
        "我越想越焦虑，工作效率反而更低。",
        "我担心被老师抓出问题。",
        "我担心组员临时掉链子。",
        "我开始怀疑自己能不能撑下来。",
        "我担心拿不到合格分。",
        "我整个人都紧绷着，没法专心。",
        "我控制不住地担心自己挂科。",
        "我担心自己讲不清楚被同学笑话。",
        "我担心成绩掉得太厉害保不住绩点。",
    ]
    contexts = [
        "明天就要交了",
        "DDL 在三天后",
        "今天晚上必须交",
        "本周末要演示",
        "明早八点要提交",
        "下周一就要展示",
        "导师催了好几次",
        "期末周已经开始",
        "成绩马上要公布",
    ]

    samples: list[str] = []
    for trigger in triggers:
        for feeling in feelings:
            for context in contexts:
                samples.append(f"{trigger} {context}，但我还没准备好。{feeling}")
    return samples


def build_anxious_samples(target_count: int = 360) -> list[str]:
    seen: set[str] = set()
    samples: list[str] = []
    for text in _BASE_ANXIOUS_SAMPLES:
        text = text.strip()
        if text and text not in seen:
            samples.append(text)
            seen.add(text)

    for text in _generate_anxious_template_samples():
        if len(samples) >= target_count:
            break
        text = text.strip()
        if text and text not in seen:
            samples.append(text)
            seen.add(text)
    return samples


def load_anxious_rows(target_count: int = 360) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for text in build_anxious_samples(target_count=target_count):
        rows.append(
            {
                "text": text,
                "label": LABEL_ANXIOUS,
                "emotion": LABEL_NAMES[LABEL_ANXIOUS],
                "source": "manual_campus_anxious",
                "split": "",
                "notes": "campus diary anxiety sample (manual / template)",
            }
        )
    return rows


_BASE_SAD_SAMPLES = [
    "晚上一个人在宿舍待着，突然觉得很孤独，好像没人真正理解我。",
    "宿舍只剩我一个人，灯关了之后心里空落落的。",
    "周末室友都回家了，我一个人坐在桌前，鼻子一酸眼泪就下来了。",
    "今天又一个人吃饭，看着别人成群结队，心里特别难过。",
    "深夜了还睡不着，突然就想哭，也不知道为什么。",
    "在群里发了消息没人回，那一刻觉得自己被忽视了。",
    "认真讲完一段话，发现没人在听，心里凉了一下。",
    "一个人走回宿舍的路上，突然觉得没人真正懂我。",
    "和朋友的聚会被忘了叫上我，回到宿舍我就难过了一整晚。",
    "看到别人有人陪，自己却一个人待着，鼻子忍不住酸。",
    "晚上一个人在自习室坐到关门，心里空得发慌。",
    "回到宿舍发现没人说话，连灯都不想开。",
    "今天没人主动和我说话，我整个人都很低落。",
    "一个人在食堂吃饭，盯着窗外突然鼻子就酸了。",
    "宿舍空荡荡的，连呼吸都带着凉意，心里很难过。",
    "翻完朋友圈看到大家都在玩，只有我一个人在房间，特别孤独。",
    "想找人说话，翻遍通讯录却不知道发给谁，最后还是一个人。",
    "晚自习一个人留到最后，关灯那一刻特别想哭。",
    "今天什么都不顺，回到宿舍蒙着被子哭了很久。",
    "妈妈打电话问我吃了吗，我假装没事，挂了之后眼泪就掉了。",
    "下雨天一个人撑伞走回宿舍，鞋全湿了，心里也是潮的。",
    "今天本来约好的人临时放鸽子，我一个人坐在那里傻等了一小时。",
    "有些话憋在心里没人讲，越憋越觉得没人理解。",
    "看到别人在朋友圈晒陪伴，自己只剩屏幕的光，心里好难过。",
    "回宿舍开门的瞬间，发现一个人都没有，心一下子沉下去。",
    "今天状态不好，没人发现，一直自己消化到半夜。",
    "和家里通完电话更想他们了，挂了之后偷偷哭了一会儿。",
    "今天考砸了一门，没人可以倾诉，回到宿舍一个人默默坐着。",
    "我跟室友的话题越来越少，最近常常觉得自己是多余的。",
    "晚上失眠，听着隔壁房间的笑声，心里更难过了。",
    "今天有点累，想要个拥抱，但身边一个人都没有。",
    "翻看以前的照片看到熟悉的人，心一下子被揪起来。",
    "走在校园里看到情侣，我突然就觉得自己很孤单。",
    "回宿舍的路上看见路灯下只有自己的影子，眼眶就湿了。",
    "今天发生的事我没法和别人讲，憋了一天心很累。",
    "今天朋友圈所有人都在庆祝，只有我一个人静静地划过去。",
    "深夜突然想起以前的事，鼻子一酸眼泪就出来了。",
    "心里有很多话却没人能讲，越想越孤独。",
    "今天本来很期待的活动被取消了，一个人在宿舍坐了很久。",
    "我以为有人会主动找我，结果一整天手机都没响。",
    "回到家发现冰箱是空的，桌子也是空的，心也跟着空。",
    "电话那头没人接，挂了之后心一下子沉到底。",
    "看到别人都被关心，只有我一个人默默忍着，特别难过。",
    "和最好的朋友吵架后整个人都没了精神，觉得世界都灰了。",
    "晚上睡不着，看着天花板一点点亮起来，心里空得难受。",
    "今天得到的不是想要的结果，一个人坐在阳台哭了好久。",
    "我说了很多话，对方却像没听到一样，我突然觉得很失落。",
    "想找一个真正懂我的人聊聊，却一个名字也想不起来。",
    "周末没人约，我一个人在床上躺了一整天，没什么力气。",
    "今天又一次被忽视了，回宿舍闷头睡了两小时还是难过。",
    "答辩失利那一刻，我什么也说不出，眼泪在打转。",
    "我把手机调静音，可还是没有任何消息，心里凉透了。",
    "我尝试主动找人说话，结果换来冷淡的回应，心一下子就掉了。",
    "看到朋友们的合照里没有我，心里咯噔一下。",
    "今天有人随口说了句让我难受的话，我装作没事，回到宿舍才偷偷哭。",
    "今天本来想跟朋友讲，可话到嘴边又咽下去了，最后还是一个人撑着。",
    "天气阴沉沉的，整个人也跟着提不起精神。",
    "今天没什么事，就是莫名其妙地想哭。",
    "回到宿舍发现自己没什么期待的东西，整个人空空的。",
    "我太累了，但没人可以让我靠一会儿。",
    "走在去食堂的路上，突然觉得这一切都没什么意思。",
    "和奶奶视频时她说想我，我刚说一句就哽咽了。",
    "今天我又一次发现，自己最难的时候只能靠自己。",
    "我以为自己撑得住，结果在洗澡的时候哭出了声。",
    "晚上睡前翻聊天记录，看到熟悉的名字鼻子又酸了。",
    "今天的天空蓝得很漂亮，我却完全笑不出来。",
    "心里有一块沉甸甸的东西堵着，呼吸都带着钝痛。",
    "看着窗外发呆很久，发现自己不知道在想什么，眼泪却掉了。",
    "我一直以为我是开朗的人，今天才发现我也会这样难过。",
    "今天跟自己说了好几次没事，但其实一点都不好。",
    "看见别人的家人来送饭，我心里就一阵难过。",
    "我习惯把不开心藏起来，今天终于藏不住了。",
    "我感觉自己像被这个世界落下了，没人会注意到我离开。",
    "今天身体不舒服，但宿舍没人，自己倒水都觉得吃力。",
    "晚上一个人走回宿舍，路灯下只有自己拉得很长的影子。",
    "看到别人聊得开心，我插不进话只能笑笑，心里却是空的。",
    "宿舍楼里到处是说笑声，只有我的房间是安静的。",
    "好像很久没有人认真问过我最近怎么样了。",
    "我不想做任何事，只想一个人发呆，谁也别来找我。",
    "今天很累，想要被理解，但好像没人在意我说了什么。",
    "心累到不想说话，连吃饭的力气都没有。",
    "我把眼泪憋回去，又一个人撑过了一天。",
    "今天朋友说我变了，那一刻我突然就鼻子酸了。",
    "和喜欢的人吵架后，整个人都没了精神，做什么都没意思。",
    "我多希望有个人在我难过的时候不用我开口就知道。",
    "走在熙熙攘攘的人群里，我反而觉得更孤独了。",
    "看着室友一个个有人陪，只有我一个人在角落里，鼻子酸酸的。",
    "今天晚上我又把自己关在被子里哭了一会儿。",
    "我以为时间会让我好起来，可今天好像更难过了。",
    "我已经很努力假装没事了，可还是被一句话打回原形。",
    "我突然意识到，没有谁会一直站在我身边，那一刻心里特别难受。",
    "我尝试给自己打气，可眼泪还是不争气地掉下来。",
    "我多希望今天可以重来一次，把那些话留在心里。",
    "我做了一桌饭，没人和我一起吃，最后一个人草草扒完。",
    "今天又被排除在计划之外，我假装无所谓，心里却很难受。",
    "我太累了，可是没有一个能让我安心睡觉的怀抱。",
    "我把音乐调到最大，也压不住心里那种空空的感觉。",
    "我看着镜子里的自己，眼泪不知不觉就掉下来了。",
    "今天只想一个人静静地待着，谁都别说话。",
    "下雨天的图书馆没什么人，我坐在角落，一直没动地方。",
    "我突然觉得自己好像哪里都不属于。",
    "今天又一次没人能和我分享好消息，分享着分享着就想哭。",
    "我把电话拨给妈妈又挂了，怕一开口就忍不住哭。",
    "今晚的月亮很亮，可我看着它却觉得很冷。",
    "我从早到晚一句话都没说，回到宿舍才发现喉咙是哑的。",
    "看着空荡荡的宿舍，我突然好想家。",
    "今天没人陪我去医务室，自己一个人挂号有点想哭。",
    "我假装坚强了一整天，回到房间还是忍不住哭出来。",
    "今天没人主动找我吃饭，我对着外卖发了好久的呆。",
    "今天把心里话发给以前的朋友，对方却很久没回。",
    "我盯着对话框打了很多字又删掉，最后什么也没发出去。",
    "我承认我嫉妒那些被很多人喜欢的人，今天又因为这个难过了。",
    "今天又一次梦到很久没见的人，醒来枕头是湿的。",
    "我希望有人能看见我的努力，但好像没有。",
    "我开始怀疑我是不是真的不重要，那种感觉越想越疼。",
]


def _generate_sad_template_samples() -> list[str]:
    scenes = [
        "今晚宿舍只有我一个人",
        "晚上一个人坐在自习室",
        "下雨天一个人撑伞回宿舍",
        "周末没人约我出门",
        "图书馆关门后一个人走回去",
        "今天没人和我说一句话",
        "和家里打完电话挂掉之后",
        "看到朋友圈大家都在玩",
        "翻完聊天记录之后",
        "今天考砸了之后",
    ]
    feelings = [
        "心里空空的，眼泪不知不觉掉下来。",
        "突然就想哭，没人理解我。",
        "整个人都很低落，连吃饭都没胃口。",
        "鼻子一酸，觉得自己被忽视了。",
        "我把头埋进被子里，闷闷地哭了一会儿。",
        "我才发现自己其实没有想象中那么坚强。",
        "心里堵得难受，什么都不想做。",
        "我蜷在床上一动不动，连灯都没开。",
        "我假装没事，但心里很难过。",
        "我才意识到自己一直在硬撑。",
    ]

    samples: list[str] = []
    for scene in scenes:
        for feeling in feelings:
            samples.append(f"{scene}，{feeling}")
    return samples


def build_sad_samples(target_count: int = 180) -> list[str]:
    seen: set[str] = set()
    samples: list[str] = []
    for text in _BASE_SAD_SAMPLES:
        text = text.strip()
        if text and text not in seen:
            samples.append(text)
            seen.add(text)
    for text in _generate_sad_template_samples():
        if len(samples) >= target_count:
            break
        text = text.strip()
        if text and text not in seen:
            samples.append(text)
            seen.add(text)
    return samples


def load_sad_rows(target_count: int = 180) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for text in build_sad_samples(target_count=target_count):
        rows.append(
            {
                "text": text,
                "label": LABEL_SAD,
                "emotion": LABEL_NAMES[LABEL_SAD],
                "source": "manual_campus_sad",
                "split": "",
                "notes": "campus diary sad / lonely sample (manual / template)",
            }
        )
    return rows


_BASE_ANGRY_SAMPLES = [
    "今天代码一直报错，怎么改都不行，真的很烦。",
    "代码改了一下午还是报同样的错，真的很烦。",
    "代码报错改不动，气得想砸键盘。",
    "今天 IDE 一直闪退，重写了三遍了，真的很烦。",
    "环境配了一上午都没配好，真的烦。",
    "改了几十行代码还是跑不起来，气死了。",
    "项目 bug 修一个出三个，越改越烦。",
    "服务器又挂了，我刚跑了一半的实验全废，真烦。",
    "调了一晚上 bug 还是没解决，真的很烦。",
    "Python 报了一个奇怪的错误，怎么搜都搜不到答案，烦死了。",
    "git 又冲突了，我都不知道改的是哪一版，烦得不行。",
    "代码 commit 错了分支，回滚的时候又出问题，真的很烦。",
    "明明跑通的代码换了台电脑就报错，气炸了。",
    "改一行报一行错，真的快被这代码逼疯了。",
    "今天写代码全在和 bug 较劲，做了一天等于零进度，烦。",
    "刚才删了一段代码就再也复原不了，气得我想关电脑。",
    "实验脚本跑了三小时报了个 OOM，真的很烦。",
    "我已经看了三遍这段代码，还是找不到错在哪，真烦。",
    "项目代码乱得我都看不下去了，组员合并完更烂，气死。",
    "改 bug 改到怀疑人生，真的越改越烦。",
    "代码不行，环境也不行，今天什么都不行，真的很烦。",
    "搜了半天 stackoverflow 全是答非所问，真的烦。",
    "数据格式又变了，要重新写解析代码，真的很烦。",
    "刚搞定一个错误又冒出三个，怎么改都不行。",
    "依赖装一会儿冲突一会儿，今天就栽在配环境上，烦。",
    "我代码刚跑通老师就让重做，气得不想说话。",
    "改了一整天，提交还是报错，真的很烦。",
    "组员把代码合得乱七八糟，我光是 review 就花了两小时，烦死。",
    "刚跑出来的结果发现是错的，要从头来一遍，真的很烦。",
    "今天写的代码不能用，明天还得重写，越想越气。",
    "调试日志看到吐，问题还是没找到，真的很烦。",
    "代码报错卡了我两小时，原来是个空格，气炸。",
    "电脑卡得跑不动 IDE，今天什么都干不了，真的很烦。",
    "明明前几天还跑得好好的，今天就开始报错，烦透了。",
    "导出数据又乱码了，怎么调编码都不行，真的烦。",
    "我已经第五次跑这个脚本还是不行，真的烦死了。",
]


def load_angry_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for text in _BASE_ANGRY_SAMPLES:
        text = text.strip()
        if text and text not in seen:
            rows.append(
                {
                    "text": text,
                    "label": LABEL_ANGRY,
                    "emotion": LABEL_NAMES[LABEL_ANGRY],
                    "source": "manual_campus_angry",
                    "split": "",
                    "notes": "campus diary angry / coding-frustration sample (manual)",
                }
            )
            seen.add(text)
    return rows


def load_diary_rows() -> list[dict[str, object]]:
    db_path = BASE_DIR / "db.sqlite3"
    if not db_path.exists():
        return []

    rows: list[dict[str, object]] = []
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            try:
                records = conn.execute(
                "SELECT id, date, text, sentiment, emotion_label FROM mood_moodentry ORDER BY id"
                ).fetchall()
            except sqlite3.DatabaseError:
                return []
    except sqlite3.OperationalError:
        return []

    for record in records:
        text = str(record["text"]).strip()
        sentiment = str(record["sentiment"]).strip()
        emotion_label = record["emotion_label"]
        if not text or "奴才" in text:
            continue
        if emotion_label in ALL_LABELS:
            label = int(emotion_label)
        elif sentiment in LABEL_KEY_TO_LABEL:
            label = LABEL_KEY_TO_LABEL[sentiment]
        else:
            continue
        rows.append(
            {
                "text": text,
                "label": label,
                "emotion": LABEL_NAMES[label],
                "source": "diary",
                "split": "",
                "notes": (
                    f"mood_moodentry.id={record['id']}; "
                    f"date={record['date']}; emotion_key={sentiment}"
                ),
            }
        )
    return rows


def load_balanced_augment_rows(count_per_label: int = 200) -> list[dict[str, object]]:
    """Deterministic campus-diary style augmentation: exactly `count_per_label` per emotion."""
    if count_per_label <= 0:
        return []

    def take_pairs(prefixes: list[str], suffixes: list[str]) -> list[str]:
        pairs = list(product(prefixes, suffixes))
        texts = [f"{a}{b}" for a, b in pairs]
        return texts[:count_per_label]

    sad_prefixes = [
        "今晚宿舍很安静",
        "一个人吃完晚饭走回宿舍",
        "周末室友都不在",
        "自习室坐到关门才离开",
        "群里发的消息半天没人回",
        "认真讲完却发现没人认真听",
        "雨天一个人撑伞去食堂",
        "刷完朋友圈关了屏幕",
        "洗完澡坐在床边发呆",
        "给家里打完视频挂了电话",
        "翻开相册看到去年的合照",
        "路过操场看见很多人在跑步",
        "食堂角落一个人吃完套餐",
        "图书馆闭馆音乐响起的时候",
        "路灯下影子拉得很长",
        "今天第三次刷新邮箱还是没有回信",
        "把想说的话写进备忘录又删掉",
        "耳机里放着歌却一句也没听进去",
        "洗漱完发现室友床帘里一片安静",
        "凌晨两点还在辗转睡不着",
    ]
    sad_suffixes = [
        "，心里闷闷的，提不起劲。",
        "，突然觉得有点孤单。",
        "，鼻子一酸就又把情绪压下去了。",
        "，什么话都不想再说。",
        "，只想躲进被子里安静一会儿。",
        "，越想越想哭又不好意思出声。",
        "，好像没人注意到我今天不太好。",
        "，那种空落落的感觉一直在。",
        "，努力装作没事其实很难过。",
        "，眼泪掉下来才发现自己撑不住了。",
    ]

    anxious_prefixes = [
        "明天第一节就有测验",
        "这周有三个 DDL 连在一起",
        "导师刚才又在群里催进度",
        "毕设中期检查只剩五天",
        "项目演示定在周五下午",
        "考研真题错题还没整理完",
        "实习简历改了第八版还是不满意",
        "英语口语考核排在周三",
        "课程论文截止时间是今晚十二点",
        "实验报告格式又被助教打回",
        "组会轮到我汇报还剩两天",
        "补考名单还没公布",
        "保研材料还差一封推荐信",
        "机房排队两小时还没轮到座位",
        "代码仓库权限突然被收回",
        "选课系统崩溃我没抢到课",
        "打印店关门才发现报告没打好",
        "实验室门禁卡丢了进不去",
        "VPN 连不上没法下参考文献",
        "小组分工表还没对齐各自进度",
    ]
    anxious_suffixes = [
        "，越想越慌，手心一直在出汗。",
        "，我心跳很快，根本坐不住。",
        "，控制不住地把最坏的结果想了一遍又一遍。",
        "，怕赶不上只能今晚通宵试试。",
        "，脑子里全是还没做完的事。",
        "，担心被老师当众问到细节答不上来。",
        "，怕拖累组员又怕自己一个人扛不住。",
        "，复习半天也不知道方向对不对。",
        "，邮件草稿写了删删了写仍不敢发。",
        "，只要一安静下来就更焦虑。",
    ]

    angry_prefixes = [
        "老师临时改截止时间还不提前说明",
        "室友半夜打游戏键盘敲得震天响",
        "组长把最难的部分甩给我一句辛苦了",
        "外卖迟到了四十分钟汤全洒了",
        "打印机卡纸把我的论文撕坏了",
        "选课系统崩溃我只抢到一节硬课",
        "课上有人一直大声聊天还不听讲",
        "群里明明定了分工有人却一直消失",
        "辅导员临时开会占用整个晚自习",
        "洗衣机被别人拿走衣服揉成一团",
        "共享单车被人恶意锁在树干上",
        "浴室排队半小时还有人插队",
        "食堂阿姨算错钱还不承认",
        "室友借了数据线两周不还",
        "快递被人误拿拆开还不吱声",
        "图书馆有人占座一整天不来",
        "电梯坏了扛着主机爬七楼",
        "校园网断了一整天作业交不上",
        "演示前一天被告知需求又改了",
        "代码合并冲突全是别人的烂格式",
    ]
    angry_suffixes = [
        "，我真的特别不爽。",
        "，越想越气，胸口堵得慌。",
        "，当场就想发火又只能憋着。",
        "，这事完全不考虑别人感受。",
        "，气得我把耳机摔到桌上。",
        "，真想当面质问凭什么这样安排。",
        "，明明可以提前说清楚非要临时通知。",
        "，我已经尽力配合结果还是被拖累。",
        "，这种不负责任的做法我很反感。",
        "，今天一整天心情都被这件事毁了。",
    ]

    calm_prefixes = [
        "今天在图书馆自习两小时",
        "早上八点按时去食堂吃了豆浆油条",
        "上午四节课都坐在中间排认真听讲",
        "中午回宿舍睡了二十分钟午觉",
        "下午实验课按步骤做完提前五分钟离开",
        "傍晚去操场慢走了三圈放松腿",
        "晚饭选了清淡窗口吃完散步回宿舍",
        "晚上把明天的书包整理好放在椅子上",
        "睡前把手机调成勿扰模式放在远处",
        "周末早起把床单被套换洗晾干",
        "把桌面收纳了一遍杂物更少",
        "按课表把下周要交的作业列成清单",
        "下载了三篇论文放进阅读文件夹",
        "跟室友约好十一点关灯各自休息",
        "去打印店顺利打好装订材料",
        "雨天带了伞走到教室鞋没湿",
        "自习室空调温度刚好坐得很舒服",
        "把邮箱未读邮件清零归档",
        "泡了一杯温水慢慢喝完继续看书",
        "晚上在阳台站了一会儿吹吹风",
    ]
    calm_suffixes = [
        "，整体节奏还算平稳，没什么大起大落。",
        "，效率一般但状态比较稳定，就这样按部就班完成。",
        "，心情平平常常，也没有特别兴奋或低落。",
        "，做事不急不慢，挺踏实的。",
        "，这一天过得普普通通，还算可控。",
        "，没什么惊喜也没什么糟心事。",
        "，按计划推进就行，我也不多想。",
        "，身体不累精神也还行，挺中庸的一天。",
        "，安静地把事情做完就挺好。",
        "，算是平常校园里普通的一天。",
    ]

    happy_prefixes = [
        "早上闹钟响之前就自然醒了",
        "食堂阿姨多给了我一个包子",
        "小组讨论一次就把分工敲定",
        "代码第一次跑通日志全是绿色的",
        "助教说我报告格式这次完全过关",
        "体育课阳光很好风吹得很舒服",
        "抢到心仪的选修课名额",
        "快递拆开正好是需要的那本书",
        "傍晚云彩很好看顺手拍了照片",
        "室友带了家乡特产分给大家",
        "导师邮件里夸了我这一段进度",
        "口语考试题目刚好昨晚练过",
        "打印店老板顺手帮我装订整齐",
        "图书馆找到了最后一个靠窗座位",
        "晚饭和朋友边吃边聊到关门",
        "校园歌手彩排路过觉得旋律好听",
        "洗澡水温刚刚好也不用排队",
        "睡前刷到喜欢的乐队官宣巡演",
        "把拖延两周的任务一口气收尾",
        "明天没有早八可以睡到自然醒",
    ]
    happy_suffixes = [
        "，整个人轻松了不少，心情挺好。",
        "，忍不住嘴角上扬了一整天。",
        "，感觉今天运气站在我这边。",
        "，做完这些事特别有成就感。",
        "，和朋友分享完更开心了。",
        "，这种小确幸足够点亮一整天。",
        "，走路都不自觉地轻快起来。",
        "，晚上写日记都觉得今天的页面亮堂堂。",
        "，终于可以把心事放下好好睡一觉。",
        "，对生活的满意度悄悄往上挪了一点。",
    ]

    builders = [
        (LABEL_SAD, sad_prefixes, sad_suffixes),
        (LABEL_ANXIOUS, anxious_prefixes, anxious_suffixes),
        (LABEL_ANGRY, angry_prefixes, angry_suffixes),
        (LABEL_CALM, calm_prefixes, calm_suffixes),
        (LABEL_HAPPY, happy_prefixes, happy_suffixes),
    ]

    rows: list[dict[str, object]] = []
    for label, prefixes, suffixes in builders:
        for text in take_pairs(prefixes, suffixes):
            rows.append(
                {
                    "text": text,
                    "label": label,
                    "emotion": LABEL_NAMES[label],
                    "source": "manual_balanced_augment",
                    "split": "",
                    "notes": (
                        f"balanced augment {count_per_label}/class; "
                        f"deterministic template combo"
                    ),
                }
            )
    return rows


def deduplicate(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[str] = set()
    unique_rows: list[dict[str, object]] = []
    for row in rows:
        text = str(row["text"]).strip()
        if not text or text in seen:
            continue
        if int(row["label"]) not in ALL_LABELS:
            continue
        seen.add(text)
        unique_rows.append(row)
    return unique_rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> None:
    hf_rows = load_hf_rows()
    anxious_rows = load_anxious_rows()
    sad_rows = load_sad_rows()
    angry_rows = load_angry_rows()
    diary_rows = load_diary_rows()

    augment_rows = load_balanced_augment_rows(200)
    labeled_rows = deduplicate(
        hf_rows + anxious_rows + sad_rows + angry_rows + diary_rows + augment_rows
    )

    write_csv(
        LABELED_DATA_PATH,
        labeled_rows,
        fieldnames=["text", "label", "emotion", "source", "split", "notes"],
    )

    raw_rows = []
    for row in labeled_rows:
        raw_rows.append(
            {
                "text": row["text"],
                "source": row["source"],
                "original_label": row["emotion"],
                "notes": row["notes"],
            }
        )
    write_csv(
        RAW_DATA_PATH,
        raw_rows,
        fieldnames=["text", "source", "original_label", "notes"],
    )

    counter: dict[int, int] = {label: 0 for label in ALL_LABELS}
    for row in labeled_rows:
        counter[int(row["label"])] += 1

    print(f"hf_rows={len(hf_rows)}")
    print(f"anxious_rows={len(anxious_rows)}")
    print(f"sad_rows={len(sad_rows)}")
    print(f"angry_rows={len(angry_rows)}")
    print(f"diary_rows={len(diary_rows)}")
    print(f"augment_rows={len(augment_rows)}")
    print(f"labeled_rows={len(labeled_rows)}")
    for label in ALL_LABELS:
        print(f"label={label} ({LABEL_NAMES[label]}): {counter[label]}")
    print(f"raw_path={RAW_DATA_PATH}")
    print(f"labeled_path={LABELED_DATA_PATH}")


if __name__ == "__main__":
    main()
