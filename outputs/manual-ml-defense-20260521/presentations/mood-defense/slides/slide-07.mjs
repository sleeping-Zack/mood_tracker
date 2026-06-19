import { C, bg, footer, image, img, kicker, metric, panel, title } from "./common.mjs";

export async function slide07(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "feature engineering", "07");
  title(slide, ctx, "TF-IDF 不是装饰性步骤：它把中文日记转成可解释、可复现、可稀疏计算的特征空间。", 82, 74, 29, 1060);
  await image(slide, ctx, img.sparse, 58, 168, 690, 215, "contain", "sparse matrix");
  await image(slide, ctx, img.nonzero, 778, 160, 390, 255, "contain", "nonzero distribution");
  panel(slide, ctx, 78, 424, 1090, 80, "参数设置", "TfidfVectorizer(tokenizer=str.split, lowercase=False, ngram_range=(1,2), max_features=8000, min_df=3, max_df=0.9)。训练阶段重新 fit 向量器，并与模型一起保存，避免向量器和模型不匹配。", C.teal, C.white, { bodySize: 12.4, bodyBold: true });
  metric(slide, ctx, "3436×3439", "训练矩阵形状", 96, 540, C.teal, "样本 × 特征", { valueW: 220, valueSize: 24, labelW: 210, noteW: 210 });
  metric(slide, ctx, "46989", "非零元素", 352, 540, C.coral, "总元素 > 1181 万");
  metric(slide, ctx, "99.60%", "训练稀疏率", 594, 540, C.gold, "sparsity");
  metric(slide, ctx, "13.68", "平均非零特征", 836, 540, C.navy, "per sample");
  footer(slide, ctx, 7, "证据：tfidf_sparse_matrix_spy.png / nonzero_feature_distribution.png / sparse_matrix_stats.csv");
  return slide;
}
