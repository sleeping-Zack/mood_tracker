import { C, bg, bulletList, footer, kicker, metric, panel, table, title } from "./common.mjs";

export async function slide09(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "experimental protocol", "09");
  title(slide, ctx, "实验设计的重点是防止“看过测试集再调参”，因此验证集和测试集承担不同角色。", 82, 74, 30, 1060);
  table(slide, ctx, [
    { label: "阶段", w: 140 },
    { label: "输入", w: 310 },
    { label: "操作", w: 360 },
    { label: "输出证据", w: 290 },
  ], [
    ["数据切分", "emotion_labeled.csv", "按 label 分层切分 8:1:1", "label_distribution.csv"],
    ["特征工程", "train/valid/test_segmented.csv", "fit 训练集向量器，valid/test 只 transform", "tfidf_vectorizer.joblib"],
    ["模型训练", "训练集 TF-IDF", "训练 NB、LR、LinearSVC 三个模型", "train_log.json"],
    ["模型选择", "验证集指标", "以 Macro F1 为主，记录 tie-break 规则", "best_model_info.json"],
    ["最终评估", "测试集 430 条", "只评估一次，输出混淆矩阵和误分类表", "evaluation_log.json"],
  ], 70, 174, 1100, 36, { bodySize: 10.2, boldFirstCol: true });
  bulletList(slide, ctx, [
    { text: "评估指标：Accuracy、Macro F1、Weighted F1、Macro Precision、Macro Recall、predict_ms_per_sample。", color: C.teal },
    { text: "公平性控制：三个模型使用同一套 TF-IDF 特征，避免模型差异被特征差异污染。", color: C.coral },
    { text: "复现控制：关键参数、环境版本、模型路径、向量器路径均写入 JSON 日志。", color: C.gold },
  ], 90, 432, 1040, 34, { size: 12.8 });
  metric(slide, ctx, "3", "监督模型", 120, 560, C.teal, "NB / LR / SVM");
  metric(slide, ctx, "1", "主模型规则", 365, 560, C.coral, "validation Macro F1");
  metric(slide, ctx, "430", "最终测试样本", 610, 560, C.gold, "只用于最终报告");
  metric(slide, ctx, "可复查", "实验产物", 855, 560, C.navy, "csv/json/png/joblib");
  footer(slide, ctx, 9, "证据：split_dataset.py / feature_engineering.py / train_model.py / evaluate_model.py");
  return slide;
}
