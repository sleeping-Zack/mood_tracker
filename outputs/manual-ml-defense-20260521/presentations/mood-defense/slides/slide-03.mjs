import { C, bg, footer, kicker, panel, rect, text, title } from "./common.mjs";

export async function slide03(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "contribution spine", "03");
  title(slide, ctx, "本项目的贡献不是“调库跑模型”，而是把五分类任务做成可证明、可解释、可集成的工程闭环。", 82, 74, 29, 1080);
  panel(slide, ctx, 70, 172, 250, 155, "贡献 1：任务升级", "从原有粗粒度情感倾向升级为五分类情绪识别，单独补齐校园日记中高频但公开数据不足的“焦虑”类别。", C.teal, C.white, { bodySize: 12.2 });
  panel(slide, ctx, 350, 172, 250, 155, "贡献 2：可复现实验", "明确数据来源、标签映射、分层切分、特征配置、模型选择规则，所有关键产物保存到 reports/artifacts。", C.coral, C.white, { bodySize: 12.2 });
  panel(slide, ctx, 630, 172, 250, 155, "贡献 3：可解释证据", "展示标签分布、稀疏矩阵、Top TF-IDF 词、混淆矩阵和误分类对，证明模型行为可追溯。", C.gold, C.white, { bodySize: 12.2 });
  panel(slide, ctx, 910, 172, 250, 155, "贡献 4：系统落地", "通过 ml/predict.py 接入 Django；预测结果写入 MoodEntry，并参与趋势图和页面建议展示。", C.navy, C.white, { bodySize: 12.2 });
  rect(slide, ctx, 90, 395, 1030, 98, C.white, C.line, 1);
  text(slide, ctx, "答辩逻辑链", 112, 414, 130, 22, { size: 16, bold: true });
  text(slide, ctx, "问题约束 → 数据构建 → 预处理与特征 → 三模型验证 → 测试集确认 → 误差解释 → Django 集成 → 不足与改进", 245, 414, 820, 24, { size: 15, bold: true, color: C.teal });
  text(slide, ctx, "每个环节都对应一个可检查产物：CSV 数据、joblib 模型、PNG 图表、JSON 日志、Django 字段迁移和页面结果。", 112, 452, 945, 26, { size: 13, color: C.ink });
  panel(slide, ctx, 90, 535, 1030, 76, "最终主张", "在当前样本规模和课程复现约束下，TF-IDF + LinearSVC 是一个比外部在线模型更稳定、比复杂深度模型更可控、比无监督聚类更适合上线的方案。", C.teal, C.teal2, { bodySize: 13.5, bodyBold: true });
  footer(slide, ctx, 3, "证据链：README.md / report/*.md / ml/reports/*.csv,json,png / ml/artifacts/*.joblib");
  return slide;
}
