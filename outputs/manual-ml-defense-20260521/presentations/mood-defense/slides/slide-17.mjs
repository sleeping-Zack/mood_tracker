import { C, bg, footer, kicker, panel, title } from "./common.mjs";

export async function slide17(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "limitations and future work", "17");
  title(slide, ctx, "不足与改进路径必须讲清楚：当前系统可靠，但还不是面向真实大规模用户的最终模型。", 82, 74, 30, 1060);
  panel(slide, ctx, 78, 170, 330, 150, "局限 1：数据来源仍偏小", "公开多情绪语料与人工校园样本能支撑课程验证，但真实日记表达更私密、长短不一、情绪混合更明显。", C.coral, C.white, { bodySize: 12.2 });
  panel(slide, ctx, 455, 170, 330, 150, "局限 2：边界情绪仍会混淆", "开心/平静、难过/平静、生气/焦虑在短句中常共享词面信号，需要更多上下文和强度建模。", C.gold, C.white, { bodySize: 12.2 });
  panel(slide, ctx, 832, 170, 330, 150, "局限 3：置信度解释有限", "LinearSVC 决策函数可排序，但不是天然概率；若用于真实用户建议，需要阈值、校准和人工兜底。", C.teal, C.white, { bodySize: 12.2 });
  panel(slide, ctx, 78, 370, 330, 150, "改进 1：数据层", "收集匿名真实日记，扩展焦虑/平静/开心边界样本；建立主动学习流程，让误分类样本反哺训练集。", C.teal, C.teal2, { bodySize: 12.2 });
  panel(slide, ctx, 455, 370, 330, 150, "改进 2：模型层", "在传统模型上加入概率校准和阈值拒识；进一步比较 LinearSVC、LR、轻量中文预训练模型的成本收益。", C.coral, C.coral2, { bodySize: 12.2 });
  panel(slide, ctx, 832, 370, 330, 150, "改进 3：系统层", "为 Django 增加模型版本字段、预测日志、用户反馈入口和可视化误差面板，形成长期迭代闭环。", C.gold, C.gold2, { bodySize: 12.2 });
  panel(slide, ctx, 78, 575, 1084, 50, "答辩口径", "承认局限不是削弱项目，而是说明当前结论的适用边界：课堂级、离线、可复现、可解释的五分类情绪日记系统已经成立。", C.navy, C.navy2, { bodySize: 12.5, bodyBold: true });
  footer(slide, ctx, 17, "证据：error_cases.csv / svm_error_pair_heatmap.png / django_integration_summary.md");
  return slide;
}
