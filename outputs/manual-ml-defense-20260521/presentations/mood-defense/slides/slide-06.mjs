import { C, bg, bulletList, flowStep, footer, kicker, panel, rect, text, title } from "./common.mjs";

export async function slide06(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  kicker(slide, ctx, "preprocessing", "06");
  title(slide, ctx, "中文短文本预处理的关键不是复杂，而是训练阶段与预测阶段完全一致。", 82, 74, 31, 1040);
  flowStep(slide, ctx, 1, "清洗文本", "去空白、统一格式、清理极端噪声符号", 78, 170, 190, C.teal);
  flowStep(slide, ctx, 2, "jieba 分词", "精确模式；加载校园场景用户词典", 300, 170, 190, C.coral);
  flowStep(slide, ctx, 3, "停用词过滤", "去除虚词、标点和低信息 token", 522, 170, 190, C.gold);
  flowStep(slide, ctx, 4, "空格拼接", "输出 seg_text，供 TfidfVectorizer 直接读取", 744, 170, 210, C.navy);
  flowStep(slide, ctx, 5, "预测复用", "segment_for_prediction 与训练逻辑一致", 984, 170, 190, C.teal);
  rect(slide, ctx, 78, 312, 500, 188, C.white, C.line, 1);
  text(slide, ctx, "分词示例", 100, 332, 120, 24, { size: 16, bold: true });
  text(slide, ctx, "原文：明天就要答辩了，PPT 还没完全准备好，心里很紧张。", 100, 372, 440, 30, { size: 12.5, bold: true });
  text(slide, ctx, "清洗+分词：明天 答辩 PPT 还没 完全 准备 好 心里 紧张", 100, 420, 440, 30, { size: 12.5, color: C.teal, bold: true });
  text(slide, ctx, "意义：保留“还没、准备、紧张、答辩”等能区分焦虑的词项，同时避免页面预测时与训练分词不一致。", 100, 462, 430, 30, { size: 11.2, color: C.mute });
  panel(slide, ctx, 640, 312, 500, 188, "实现位置", "`ml/preprocess.py` 负责训练数据清洗与分词；`ml/predict.py::segment_for_prediction` 在 Django 预测时复用同一逻辑；用户词典与停用词集中放在 `ml/dicts/`。", C.teal, C.white, { bodySize: 12 });
  bulletList(slide, ctx, [
    { text: "避免数据泄漏：向量器只在训练集 fit，验证/测试集只 transform。", color: C.coral, bold: true },
    { text: "避免线上线下割裂：Django 提交文本时走同一套分词与向量化入口。", color: C.teal, bold: true },
    { text: "避免不可复现：每个阶段输出 CSV/JSON/PNG 证据文件，便于复查。", color: C.gold, bold: true },
  ], 110, 540, 980, 34, { size: 13 });
  footer(slide, ctx, 6, "证据：ml/preprocess.py / ml/predict.py / ml/dicts/user_dict.txt / segment_preview.csv");
  return slide;
}
