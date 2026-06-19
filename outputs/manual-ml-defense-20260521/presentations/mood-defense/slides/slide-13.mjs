import { C, bg, footer, image, img, kicker, panel, title } from "./common.mjs";

export async function slide13(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "interpretability", "13");
  title(slide, ctx, "Top TF-IDF 词项提供了可解释证据：模型捕捉的是情绪表达线索，而不是纯粹记忆样本。", 82, 74, 29, 1080);
  await image(slide, ctx, img.topTerms, 64, 160, 610, 450, "contain", "top tfidf terms");
  panel(slide, ctx, 720, 165, 390, 95, "焦虑信号", "“还没、担心、准备、没准备、准备好”集中指向未完成任务和时间压力。", C.teal, C.teal2, { bodySize: 12.5, bodyBold: true });
  panel(slide, ctx, 720, 282, 390, 95, "开心信号", "“开心、终于、太高兴、太好了”直接表达正向情绪或压力解除。", C.coral, C.coral2, { bodySize: 12.5, bodyBold: true });
  panel(slide, ctx, 720, 399, 390, 95, "生气信号", "“真的、这样、怎么、不、这种”更多对应抱怨、反问和被冒犯语气。", C.gold, C.gold2, { bodySize: 12.5, bodyBold: true });
  panel(slide, ctx, 720, 516, 390, 85, "答辩口径", "可解释性不是只看一个词，而是结合类别词项、混淆矩阵和误分类案例判断模型是否学到合理规律。", C.navy, C.white, { bodySize: 11.5 });
  footer(slide, ctx, 13, "证据：top_tfidf_terms_by_label.csv / top_tfidf_terms_by_label.png");
  return slide;
}
