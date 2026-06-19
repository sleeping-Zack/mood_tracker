import { C, bg, footer, kicker, panel, table, title } from "./common.mjs";

export async function slide15(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "reproducibility", "15");
  title(slide, ctx, "可复现不是口头承诺：从数据构建到网页运行都有明确命令、产物和检查点。", 82, 74, 30, 1060);
  table(slide, ctx, [
    { label: "步骤", w: 170 },
    { label: "命令", w: 520 },
    { label: "验证产物", w: 390 },
  ], [
    ["数据构建", "python ml\\build_5class_dataset.py && python ml\\split_dataset.py", "emotion_labeled.csv / label_distribution.png"],
    ["预处理与特征", "python ml\\preprocess.py && python ml\\feature_engineering.py", "train_segmented.csv / tfidf_vectorizer.joblib"],
    ["监督训练", "python ml\\train_model.py", "nb/lr/svm_model.joblib / train_log.json"],
    ["测试评估", "python ml\\evaluate_model.py", "test_model_compare.csv / confusion_matrix_svm.png"],
    ["网页演示", "python manage.py migrate && python manage.py runserver", "MoodEntry 记录 / mood_trend.png"],
  ], 70, 170, 1080, 42, { bodySize: 10, boldFirstCol: true });
  panel(slide, ctx, 80, 435, 330, 120, "环境说明", "当前训练环境为 Python 3.9.13、scikit-learn 1.0.2、joblib 1.1.0；正式演示若切换 Python 3.11，应重新训练并保存 joblib。", C.coral, C.white, { bodySize: 11.3 });
  panel(slide, ctx, 455, 435, 330, 120, "版本风险控制", "scikit-learn 不保证 joblib 跨版本加载完全兼容，因此报告中记录环境版本和模型路径，避免“能跑但不可解释”。", C.gold, C.white, { bodySize: 11.3 });
  panel(slide, ctx, 830, 435, 310, 120, "答辩检查点", "现场可展示：CSV、JSON 训练日志、混淆矩阵、稀疏矩阵、Django 首页提交和数据库记录。", C.teal, C.white, { bodySize: 11.3 });
  panel(slide, ctx, 80, 585, 1060, 48, "结论", "这套流程可以从零重新生成数据、训练模型、评估结果并接入网站，因此不是一次性截图工程。", C.navy, C.navy2, { bodySize: 13, bodyBold: true });
  footer(slide, ctx, 15, "证据：README.md / requirements.txt / ml/reports/train_log.json / evaluation_log.json");
  return slide;
}
