import { C, chip, footer, image, img, metric, panel, rect, text } from "./common.mjs";

export async function slide01(presentation, ctx) {
  const slide = presentation.slides.add();
  rect(slide, ctx, 0, 0, ctx.W, ctx.H, C.paper);
  await image(slide, ctx, img.cover, 505, 0, 775, 720, "cover", "image2 style cover");
  rect(slide, ctx, 0, 0, 590, 720, "#F7F2EAEE");
  rect(slide, ctx, 0, 0, 14, 720, C.navy);
  text(slide, ctx, "机器学习与实践 · 课程大作业答辩", 62, 54, 420, 24, { size: 11, color: C.mute, bold: true });
  text(slide, ctx, "基于传统机器学习的\n情绪日记五分类系统", 62, 130, 495, 112, { size: 34, bold: true, color: C.ink });
  text(slide, ctx, "研究目标：在保留 Django 情绪日记应用的前提下，构建可离线复现、可解释、可落地的中文日记情绪识别内核。", 64, 262, 452, 54, { size: 14.5, color: C.ink, bold: true });
  chip(slide, ctx, "jieba 分词", 64, 338, 112, C.navy2, C.navy);
  chip(slide, ctx, "TF-IDF 稀疏特征", 190, 338, 150, C.teal2, C.teal);
  chip(slide, ctx, "LinearSVC", 354, 338, 112, C.coral2, C.coral);
  panel(slide, ctx, 64, 392, 430, 94, "答辩主线", "为什么要从外部在线模型迁移到本地五分类？如何证明数据、特征、模型、系统四个环节是闭环而不是孤立实验？", C.teal, C.white, { bodySize: 12.5 });
  metric(slide, ctx, "4295", "五分类标注样本", 72, 526, C.teal, "train/valid/test");
  metric(slide, ctx, "3439", "TF-IDF 特征维度", 235, 526, C.coral, "unigram+bigram");
  metric(slide, ctx, "0.9208", "测试 Macro F1", 398, 526, C.gold, "LinearSVC");
  footer(slide, ctx, 1, "封面视觉：image generation / image 2.0 路线；图表证据均来自本项目实验产物");
  return slide;
}
