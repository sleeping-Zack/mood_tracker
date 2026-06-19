import { C, bg, flowStep, footer, image, img, kicker, panel, rect, text, title } from "./common.mjs";

export async function slide14(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "django integration", "14");
  title(slide, ctx, "模型已进入 Django 日记流程：用户输入、模型预测、数据库记录和趋势展示形成闭环。", 82, 74, 30, 1060);
  flowStep(slide, ctx, 1, "用户输入", "mood_note 文本", 72, 160, 185, C.teal);
  flowStep(slide, ctx, 2, "预测入口", "mood/views.py 调用 predict_emotion(text)", 295, 160, 215, C.coral);
  flowStep(slide, ctx, 3, "本地模型", "TF-IDF vectorizer + LinearSVC joblib", 548, 160, 220, C.gold);
  flowStep(slide, ctx, 4, "数据库", "MoodEntry 保存 label/score/model_name", 806, 160, 220, C.navy);
  flowStep(slide, ctx, 5, "页面展示", "情绪、建议语、历史记录和趋势图", 1060, 160, 150, C.teal);
  await image(slide, ctx, img.moodTrend, 676, 300, 455, 250, "contain", "mood trend");
  rect(slide, ctx, 78, 300, 535, 255, C.white, C.line, 1);
  text(slide, ctx, "数据库字段同步", 102, 322, 180, 24, { size: 16, bold: true });
  text(slide, ctx, "emotion_label：0/1/2/3/4 五分类标签\nsentiment：sad/anxious/angry/calm/happy\nscore：-2/-1/0/+2 趋势分值\nmodel_name：TF-IDF + LinearSVC\nanalysis_message：对应情绪建议语\nanalyzed_at：预测时间", 102, 365, 470, 132, { size: 12.5, color: C.ink });
  panel(slide, ctx, 78, 580, 1050, 52, "工程结论", "本项目没有重写网站，而是把识别内核替换为本地传统机器学习模型；这使实验产物可以被页面真实调用，满足“机器学习与实践”的实践要求。", C.teal, C.teal2, { bodySize: 12.5, bodyBold: true });
  footer(slide, ctx, 14, "证据：mood/views.py / mood/models.py / ml/predict.py / static/mood_trend.png");
  return slide;
}
