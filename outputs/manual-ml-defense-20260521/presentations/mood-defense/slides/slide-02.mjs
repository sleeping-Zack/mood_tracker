import { C, bg, bulletList, footer, kicker, metric, panel, title } from "./common.mjs";

export async function slide02(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "problem definition", "02");
  title(slide, ctx, "答辩的核心问题：不是“能不能分类”，而是能否在课堂环境中稳定复现并服务真实日记流程。", 82, 74, 29, 1080);
  panel(slide, ctx, 66, 178, 350, 150, "现实约束", "原项目已有 Django 页面与趋势记录，但情绪识别依赖外部接口；课堂演示时网络、模型缓存、版本兼容都会影响结果。", C.coral, C.white, { bodySize: 13 });
  panel(slide, ctx, 466, 178, 350, 150, "任务重定义", "将用户输入的中文日记文本划分为：难过、焦虑、生气、平静、开心五类，并同步生成趋势分值与建议语句。", C.teal, C.white, { bodySize: 13 });
  panel(slide, ctx, 866, 178, 350, 150, "评价标准", "既看整体准确率，也看 Macro F1，避免多数类别掩盖少数类别；同时检查误差边界和 Django 集成可用性。", C.gold, C.white, { bodySize: 13 });
  bulletList(slide, ctx, [
    { text: "研究假设 H1：短文本情绪表达具有可由词项和词组捕捉的稳定信号。", color: C.teal, bold: true },
    { text: "研究假设 H2：TF-IDF 高维稀疏特征与线性分类器匹配，能在小样本课程项目中取得足够可靠的效果。", color: C.coral, bold: true },
    { text: "研究假设 H3：模型必须进入 Web 业务链路，才算完成“实践”，不能停留在离线 notebook。", color: C.gold, bold: true },
  ], 90, 385, 1040, 40, { size: 14 });
  metric(slide, ctx, "5", "目标类别", 120, 548, C.teal, "sad/anxious/angry/calm/happy");
  metric(slide, ctx, "0", "在线推理依赖", 390, 548, C.coral, "joblib 本地加载");
  metric(slide, ctx, "1", "统一预测入口", 660, 548, C.gold, "predict_emotion(text)");
  metric(slide, ctx, "闭环", "最终交付标准", 930, 548, C.navy, "数据→模型→Django");
  footer(slide, ctx, 2, "答辩口径：先定义评价问题，再解释为什么传统机器学习方案适合该约束");
  return slide;
}
