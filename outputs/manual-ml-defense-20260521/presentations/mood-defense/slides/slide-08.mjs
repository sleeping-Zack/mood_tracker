import { C, bg, footer, kicker, panel, table, title } from "./common.mjs";

export async function slide08(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "model design", "08");
  title(slide, ctx, "模型选择遵循“先可解释、再比较、最后落地”的原则，\n而不是盲目追求复杂度。", 82, 82, 29, 1080);
  table(slide, ctx, [
    { label: "模型", w: 160 },
    { label: "核心假设", w: 365 },
    { label: "优点", w: 295 },
    { label: "风险", w: 270 },
  ], [
    ["MultinomialNB", "词项条件独立，适合计数/概率式文本分类", "训练极快、基线清晰", "无法充分利用复杂边界"],
    ["LogisticRegression", "线性可分概率模型，权重可解释", "稳定、可输出概率", "训练时间略高"],
    ["LinearSVC", "在高维稀疏空间寻找最大间隔超平面", "适合 TF-IDF 稀疏文本，泛化强", "置信度需额外校准"],
  ], 70, 174, 1090, 42, { bodySize: 10.5, boldFirstCol: true });
  panel(slide, ctx, 78, 370, 340, 130, "为什么不是深度模型", "样本量、课堂复现、离线演示和依赖安装都要求方案轻量。深度模型可以作为未来方向，但不应成为当前系统的最小可靠方案。", C.coral, C.white, { bodySize: 12 });
  panel(slide, ctx, 470, 370, 340, 130, "为什么强调 Macro F1", "五分类中每类支持数不同；只看 Accuracy 可能掩盖焦虑、开心等较小类别的错误，因此主排序使用 Macro F1。", C.teal, C.white, { bodySize: 12 });
  panel(slide, ctx, 862, 370, 300, 130, "模型选择规则", "验证集 Macro F1 优先；若差距在 ±0.005 内，再比较 weighted F1、accuracy 和模型偏好。测试集只做最终确认。", C.gold, C.white, { bodySize: 12 });
  panel(slide, ctx, 78, 535, 1084, 64, "答辩口径", "本项目的模型选择不是“哪个库更高级”，而是在高维稀疏文本、可复现课堂环境和 Django 集成成本之间取得工程上可解释的平衡。", C.navy, C.navy2, { bodySize: 13, bodyBold: true });
  footer(slide, ctx, 8, "证据：ml/train_model.py / best_model_info.json / train_log.json");
  return slide;
}
