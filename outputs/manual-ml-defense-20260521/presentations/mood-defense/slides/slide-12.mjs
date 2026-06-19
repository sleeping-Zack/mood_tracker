import { C, bg, bulletList, footer, image, img, kicker, panel, title } from "./common.mjs";

export async function slide12(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "error analysis", "12");
  title(slide, ctx, "误差不是随机崩溃，主要集中在情绪边界相近的类别之间。", 82, 74, 32, 1040);
  await image(slide, ctx, img.cmSvm, 62, 158, 455, 405, "contain", "svm confusion matrix");
  await image(slide, ctx, img.errorPairs, 555, 164, 410, 370, "contain", "error pair heatmap");
  panel(slide, ctx, 1000, 170, 185, 132, "主要边界", "难过 ↔ 平静\n生气 ↔ 焦虑\n开心 ↔ 平静", C.coral, C.white, { bodySize: 13, bodyBold: true });
  panel(slide, ctx, 1000, 330, 185, 150, "原因解释", "短日记常省略上下文；同一句可能同时包含压力、失落或平静叙述。词面信号不足时，线性模型会靠近相邻类别。", C.gold, C.white, { bodySize: 10.5 });
  bulletList(slide, ctx, [
    { text: "焦虑类别 Recall 达 0.9821，说明校园焦虑样本补充有效。", color: C.teal, bold: true },
    { text: "开心与平静、难过与平静容易混淆，反映“情绪强度”比“情绪方向”更难区分。", color: C.coral },
    { text: "下一步应补充真实日记长文本、加入置信度阈值和人工复核机制。", color: C.gold },
  ], 85, 590, 1030, 26, { size: 12 });
  footer(slide, ctx, 12, "证据：confusion_matrix_svm.png / svm_error_pair_heatmap.png / error_cases.csv");
  return slide;
}
