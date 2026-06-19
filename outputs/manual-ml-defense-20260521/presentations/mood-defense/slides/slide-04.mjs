import { C, bg, bulletList, footer, image, img, kicker, metric, panel, title } from "./common.mjs";

export async function slide04(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "data construction", "04");
  title(slide, ctx, "数据集不是简单下载：公开多情绪语料提供底座，\n校园焦虑样本补齐应用场景。", 82, 82, 29, 1080);
  await image(slide, ctx, img.source, 66, 174, 515, 295, "contain", "data source distribution");
  await image(slide, ctx, img.split, 640, 158, 430, 335, "contain", "stratified split");
  bulletList(slide, ctx, [
    { text: "公开数据：multi_emotion_dialogue 贡献 2710 条，是主体语义来源。", color: C.teal },
    { text: "人工增强：manual_balanced_augment 贡献 1000 条，用于缓解类别分布偏移。", color: C.coral },
    { text: "校园焦虑：manual_campus_anxious 贡献 360 条，覆盖期末、答辩、DDL、导师、代码未完成等高频场景。", color: C.gold },
  ], 82, 500, 620, 33, { size: 12.5 });
  panel(slide, ctx, 750, 520, 360, 72, "切分策略", "使用分层切分保证训练、验证、测试集中五类都保留样本；测试集仅用于最终报告，不参与模型选择。", C.navy, C.white, { bodySize: 11.5 });
  metric(slide, ctx, "3436", "训练集", 92, 610, C.teal, "80%");
  metric(slide, ctx, "429", "验证集", 310, 610, C.coral, "10%");
  metric(slide, ctx, "430", "测试集", 528, 610, C.gold, "10%");
  footer(slide, ctx, 4, "证据：emotion_labeled.csv / label_distribution.csv / data_source_distribution.png / split_label_heatmap.png");
  return slide;
}
