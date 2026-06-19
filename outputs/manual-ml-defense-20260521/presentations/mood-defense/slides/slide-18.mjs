import { C, bg, footer, kicker, metric, panel, title } from "./common.mjs";

export async function slide18(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "conclusion", "18");
  title(slide, ctx, "结论：轻量传统机器学习足以支撑课堂级情绪日记五分类系统，并且证据链完整。", 82, 74, 31, 1060);
  panel(slide, ctx, 78, 175, 330, 150, "问题回答 1", "能否离线复现？可以。数据构建、分词、TF-IDF、训练、评估和 Django 接入都有脚本与产物，核心推理不依赖网络。", C.teal, C.white, { bodySize: 12.2, bodyBold: true });
  panel(slide, ctx, 455, 175, 330, 150, "问题回答 2", "能否稳定识别五类？可以。LinearSVC 在测试集上 Accuracy 0.9186、Macro F1 0.9208，焦虑类 F1 0.9649。", C.coral, C.white, { bodySize: 12.2, bodyBold: true });
  panel(slide, ctx, 832, 175, 330, 150, "问题回答 3", "能否服务系统？可以。predict_emotion 已接入 Django，预测结果写入 MoodEntry，并驱动趋势图和页面建议。", C.gold, C.white, { bodySize: 12.2, bodyBold: true });
  metric(slide, ctx, "4295", "标注样本", 110, 390, C.teal, "五分类");
  metric(slide, ctx, "3439", "特征维度", 360, 390, C.coral, "TF-IDF");
  metric(slide, ctx, "0.9208", "测试 Macro F1", 610, 390, C.gold, "LinearSVC");
  metric(slide, ctx, "闭环", "最终交付", 860, 390, C.navy, "数据+模型+系统");
  panel(slide, ctx, 112, 535, 960, 82, "答辩结束语", "本项目的价值不在于堆叠复杂模型，而在于在明确约束下完成一套可验证的机器学习工程：标签定义清楚，特征证据可见，模型选择有指标，误差分析有解释，系统落地有入口。", C.navy, C.navy2, { bodySize: 13.5, bodyBold: true });
  footer(slide, ctx, 18, "结论：TF-IDF + LinearSVC 是当前数据规模与课程场景下的主模型；后续重点是扩充真实日记样本和置信度校准");
  return slide;
}
