import { C, bg, footer, kicker, panel, table, title } from "./common.mjs";

export async function slide05(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "label system", "05");
  title(slide, ctx, "标签体系必须先定义清楚，否则模型指标再高也无法解释业务含义。", 82, 74, 31, 1040);
  table(slide, ctx, [
    { label: "label", w: 70, align: "center" },
    { label: "中文情绪", w: 105 },
    { label: "emotion key", w: 130 },
    { label: "score", w: 80, align: "center" },
    { label: "标注标准", w: 570 },
  ], [
    ["0", "难过", "sad", "-2", "失落、伤心、孤独、低落、被拒绝、被忽视"],
    ["1", "焦虑", "anxious", "-1", "担心来不及、心慌、紧张、害怕考砸、对未发生的事过度担忧"],
    ["2", "生气", "angry", "-2", "愤怒、不耐烦、被冒犯、烦躁、抱怨、厌恶"],
    ["3", "平静", "calm", "0", "平静叙事、日常陈述、中性提问、节奏平稳"],
    ["4", "开心", "happy", "+2", "喜悦、成就感、放松、被支持、压力缓解、期待"],
  ], 80, 170, 955, 36, { bodySize: 10.5, boldFirstCol: true });
  panel(slide, ctx, 80, 420, 340, 120, "映射原则", "公开语料中的“开心、伤心、生气、厌恶、平静”进入五分类；惊讶、关心、疑问等非目标情绪删除；恐惧/担心/紧张若出现则归入焦虑。", C.teal, C.white, { bodySize: 11.5 });
  panel(slide, ctx, 470, 420, 340, 120, "为什么保留“焦虑”", "课程与校园日记场景中，焦虑不是普通负面情绪：它常与未完成任务、临近截止、考试答辩和项目压力相关，具有单独识别价值。", C.coral, C.white, { bodySize: 11.5 });
  panel(slide, ctx, 860, 420, 300, 120, "质量控制", "过滤信息量极低文本、强反讽样本和重复改写；用分层切分减少类别缺失；后续用混淆矩阵检查边界。", C.gold, C.white, { bodySize: 11.5 });
  panel(slide, ctx, 80, 570, 1080, 48, "答辩口径", "本项目不是把五个名字硬塞给模型，而是先定义可解释标签空间，再让数据、模型、数据库字段和趋势分值保持一致。", C.navy, C.navy2, { bodySize: 13, bodyBold: true });
  footer(slide, ctx, 5, "证据：report/label_guide.md / ml/config.py / mood/models.py");
  return slide;
}
