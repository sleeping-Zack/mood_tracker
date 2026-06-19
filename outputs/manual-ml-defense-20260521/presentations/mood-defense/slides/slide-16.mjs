import { C, bg, footer, image, img, kicker, metric, panel, table, title } from "./common.mjs";

export async function slide16(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "contrast and extension", "16");
  title(slide, ctx, "对照实验说明：无监督聚类能展示结构，但不能替代监督模型作为主系统。", 82, 74, 30, 1060);
  await image(slide, ctx, img.kmeans, 68, 160, 450, 335, "contain", "kmeans visualization");
  table(slide, ctx, [
    { label: "方案", w: 180 },
    { label: "Accuracy", w: 120, align: "center" },
    { label: "Macro F1", w: 120, align: "center" },
    { label: "定位", w: 390 },
  ], [
    ["TF-IDF KMeans", "0.6834", "0.6130", "无监督拓展，需后验映射 cluster id"],
    ["LSA + KMeans", "0.6994", "0.6876", "可视化更稳定，但仍低于监督模型"],
    ["LinearSVC", "0.9186", "0.9208", "最终接入 Django 的主监督模型"],
  ], 580, 180, 810, 38, { bodySize: 10.5, boldFirstCol: true });
  panel(slide, ctx, 580, 345, 500, 90, "Hugging Face 对照", "项目保留 hf_predict.py 作为旧方案对照入口；当前机器 transformers 导入因 urllib3 依赖冲突被记录为 skipped，不影响本地主模型评估。", C.coral, C.white, { bodySize: 11.5 });
  panel(slide, ctx, 580, 460, 500, 90, "为什么不把 KMeans 当主模型", "聚类标签本身没有情绪语义，必须根据簇内多数标签后验解释；它适合课程拓展，不适合直接给用户返回情绪。", C.gold, C.white, { bodySize: 11.5 });
  metric(slide, ctx, "0.6994", "最佳无监督 Accuracy", 100, 530, C.teal, "LSA+KMeans");
  metric(slide, ctx, "0.9208", "监督 Macro F1", 360, 530, C.coral, "LinearSVC");
  footer(slide, ctx, 16, "证据：kmeans_compare.csv / hf_compare.csv / kmeans_vis.png");
  return slide;
}
