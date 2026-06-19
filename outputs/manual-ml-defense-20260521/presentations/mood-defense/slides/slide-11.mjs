import { C, bg, footer, image, img, kicker, metric, table, title } from "./common.mjs";

export async function slide11(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "test result", "11");
  title(slide, ctx, "最终测试集确认：LinearSVC 不只在验证集领先，在保留测试集上也取得最优综合指标。", 82, 74, 30, 1060);
  await image(slide, ctx, img.test, 58, 158, 560, 300, "contain", "test metrics");
  await image(slide, ctx, img.f1, 650, 170, 445, 260, "contain", "f1 comparison");
  table(slide, ctx, [
    { label: "类别", w: 110 },
    { label: "Precision", w: 105, align: "center" },
    { label: "Recall", w: 105, align: "center" },
    { label: "F1", w: 105, align: "center" },
    { label: "Support", w: 105, align: "center" },
  ], [
    ["难过", "0.9390", "0.8851", "0.9112", "87"],
    ["焦虑", "0.9483", "0.9821", "0.9649", "56"],
    ["生气", "0.9237", "0.9316", "0.9277", "117"],
    ["平静", "0.8763", "0.9341", "0.9043", "91"],
    ["开心", "0.9200", "0.8734", "0.8961", "79"],
  ], 685, 444, 530, 28, { bodySize: 9.5, boldFirstCol: true });
  metric(slide, ctx, "0.9186", "Accuracy", 85, 514, C.teal, "测试集 430 条");
  metric(slide, ctx, "0.9208", "Macro F1", 305, 514, C.coral, "类别均衡指标");
  metric(slide, ctx, "0.9184", "Weighted F1", 525, 514, C.gold, "样本加权指标");
  metric(slide, ctx, "0.000368", "ms / sample", 745, 602, C.navy, "本地预测耗时", { valueW: 210, valueSize: 23 });
  footer(slide, ctx, 11, "证据：evaluation_log.json / test_model_compare.csv / test_metrics_compare.png / f1_bar.png");
  return slide;
}
