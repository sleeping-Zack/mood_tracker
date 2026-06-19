import { C, bg, bulletList, footer, image, img, kicker, metric, panel, title } from "./common.mjs";

export async function slide10(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "validation result", "10");
  title(slide, ctx, "验证集结果显示 LinearSVC 在宏平均 F1 上领先，且训练成本仍保持轻量。", 82, 74, 30, 1060);
  await image(slide, ctx, img.valid, 60, 160, 585, 320, "contain", "validation metrics");
  await image(slide, ctx, img.trainTime, 685, 158, 455, 320, "contain", "training time");
  metric(slide, ctx, "0.9142", "LinearSVC 验证 Macro F1", 95, 515, C.teal, "验证集 429 条", { valueW: 210, valueSize: 25 });
  metric(slide, ctx, "0.9032", "LR Macro F1", 380, 515, C.gold, "次优模型");
  metric(slide, ctx, "0.0178s", "SVM 训练耗时", 650, 515, C.coral, "当前数据规模");
  panel(slide, ctx, 905, 500, 250, 86, "结论", "LinearSVC 同时满足：验证指标最高、训练耗时可接受、预测速度接近实时。", C.teal, C.white, { bodySize: 11.5, bodyBold: true });
  bulletList(slide, ctx, [
    { text: "NB 速度最快，但验证 Macro F1 低于线性判别模型。", color: C.coral },
    { text: "LR 具有概率解释优势，但当前验证集指标略低。", color: C.gold },
    { text: "LinearSVC 与 TF-IDF 稀疏空间匹配，作为主模型更稳。", color: C.teal, bold: true },
  ], 90, 602, 1030, 24, { size: 11.5 });
  footer(slide, ctx, 10, "证据：train_log.json / validation_metrics_compare.png / training_time_compare.png");
  return slide;
}
