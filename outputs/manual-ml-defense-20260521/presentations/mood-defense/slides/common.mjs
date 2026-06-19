export const A = {
  root: "D:/py/mydjango/mood_tracker",
  evidence: "D:/py/mydjango/mood_tracker/.codex_work/report_evidence",
  assets: "D:/py/mydjango/mood_tracker/outputs/manual-ml-defense-20260521/presentations/mood-defense/assets",
};

export const img = {
  cover: `${A.assets}/cover_ml_emotion_image2.png`,
  source: `${A.evidence}/data_source_distribution.png`,
  split: `${A.evidence}/split_label_heatmap.png`,
  labelDist: `${A.root}/ml/reports/label_distribution.png`,
  sparse: `${A.evidence}/tfidf_sparse_matrix_spy.png`,
  nonzero: `${A.evidence}/nonzero_feature_distribution.png`,
  topTerms: `${A.evidence}/top_tfidf_terms_by_label.png`,
  valid: `${A.evidence}/validation_metrics_compare.png`,
  trainTime: `${A.evidence}/training_time_compare.png`,
  test: `${A.evidence}/test_metrics_compare.png`,
  f1: `${A.root}/ml/reports/f1_bar.png`,
  cmSvm: `${A.root}/ml/reports/confusion_matrix_svm.png`,
  errorPairs: `${A.evidence}/svm_error_pair_heatmap.png`,
  kmeans: `${A.root}/ml/reports/kmeans_vis.png`,
  moodTrend: `${A.root}/static/mood_trend.png`,
};

export const C = {
  paper: "#F7F2EA",
  paper2: "#FFFDF8",
  ink: "#172331",
  mute: "#6B7280",
  line: "#D7D2C8",
  teal: "#2F7D7A",
  teal2: "#DCEEEA",
  coral: "#E76F51",
  coral2: "#F8DFD4",
  gold: "#C9A15B",
  gold2: "#EFE6D2",
  navy: "#16324F",
  navy2: "#E8F0F4",
  green: "#6A994E",
  red: "#C94C4C",
  white: "#FFFFFF",
};

export function rect(slide, ctx, x, y, w, h, fill = C.paper2, lineFill = "#00000000", lineWidth = 0, name) {
  return ctx.addShape(slide, {
    x,
    y,
    w,
    h,
    fill,
    line: { fill: lineFill, width: lineWidth, style: "solid" },
    name,
  });
}

export function rule(slide, ctx, x, y, w, color = C.line, h = 1) {
  return rect(slide, ctx, x, y, w, h, color);
}

export function text(slide, ctx, value, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: String(value ?? ""),
    x,
    y,
    w,
    h,
    fontSize: opts.size ?? 20,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    typeface: opts.face ?? "Microsoft YaHei",
    align: opts.align ?? "left",
    valign: opts.valign ?? "top",
    fill: opts.fill ?? "#00000000",
    line: { fill: opts.line ?? "#00000000", width: opts.lineWidth ?? 0, style: "solid" },
    insets: opts.insets ?? { left: 0, right: 0, top: 0, bottom: 0 },
    name: opts.name,
  });
}

export function bg(slide, ctx) {
  rect(slide, ctx, 0, 0, ctx.W, ctx.H, C.paper);
  rect(slide, ctx, 0, 0, ctx.W, 12, C.navy);
  rect(slide, ctx, 0, 708, ctx.W, 12, C.teal);
}

export function kicker(slide, ctx, label, n = "") {
  rect(slide, ctx, 62, 45, 7, 24, C.coral, "#00000000", 0, `kicker-${n}-marker`);
  text(slide, ctx, label.toUpperCase(), 78, 45, 520, 24, {
    size: 11,
    color: C.mute,
    bold: true,
    valign: "middle",
    name: `kicker-${n}-label`,
  });
}

export function title(slide, ctx, value, y = 82, h = 76, size = 31, w = 1050) {
  text(slide, ctx, value, 60, y, w, h, {
    size,
    bold: true,
    color: C.ink,
    face: "Microsoft YaHei",
  });
}

export function footer(slide, ctx, page, note = "机器学习与实践 · 情绪日记五分类系统") {
  rule(slide, ctx, 60, 682, 1020, C.line, 1);
  text(slide, ctx, note, 60, 690, 820, 18, { size: 8.5, color: C.mute });
  text(slide, ctx, String(page).padStart(2, "0"), 1180, 684, 42, 22, {
    size: 13,
    color: C.ink,
    bold: true,
    align: "right",
  });
}

export function metric(slide, ctx, value, label, x, y, accent = C.teal, note = "", opts = {}) {
  rule(slide, ctx, x, y, 4, accent, opts.barH ?? 58);
  text(slide, ctx, value, x + 14, y - 3, opts.valueW ?? 160, 34, {
    size: opts.valueSize ?? 27,
    bold: true,
    color: C.ink,
  });
  text(slide, ctx, label, x + 14, y + 32, opts.labelW ?? 190, 17, { size: 10, bold: true, color: C.mute });
  if (note) text(slide, ctx, note, x + 14, y + 49, opts.noteW ?? 190, 17, { size: 8.5, color: C.mute });
}

export function chip(slide, ctx, value, x, y, w, fill = C.navy2, color = C.ink) {
  rect(slide, ctx, x, y, w, 32, fill, "#00000000", 0);
  text(slide, ctx, value, x + 12, y + 6, w - 24, 20, { size: 10.5, color, bold: true, valign: "middle" });
}

export function panel(slide, ctx, x, y, w, h, heading, body, accent = C.teal, fill = C.white, opts = {}) {
  rect(slide, ctx, x, y, w, h, fill, opts.line ?? C.line, opts.lineWidth ?? 1);
  rect(slide, ctx, x, y, 5, h, accent);
  if (heading && body && h <= 72) {
    text(slide, ctx, heading, x + 18, y + 12, opts.compactHeadingW ?? 130, h - 20, {
      size: opts.headingSize ?? 14,
      bold: true,
      color: C.ink,
    });
    text(slide, ctx, body, x + (opts.compactHeadingW ?? 130) + 36, y + 12, w - (opts.compactHeadingW ?? 130) - 54, h - 18, {
      size: opts.bodySize ?? 11.5,
      color: opts.bodyColor ?? C.ink,
      bold: opts.bodyBold ?? false,
    });
    return;
  }
  if (heading) text(slide, ctx, heading, x + 18, y + 16, w - 36, 24, { size: opts.headingSize ?? 15, bold: true, color: C.ink });
  if (body) text(slide, ctx, body, x + 18, y + (heading ? 46 : 18), w - 36, h - (heading ? 58 : 32), {
    size: opts.bodySize ?? 12,
    color: opts.bodyColor ?? C.ink,
    bold: opts.bodyBold ?? false,
  });
}

export function bulletList(slide, ctx, items, x, y, w, rowH = 38, opts = {}) {
  items.forEach((item, i) => {
    const yy = y + i * rowH;
    rect(slide, ctx, x, yy + 4, 7, 7, item.color ?? opts.color ?? C.teal);
    text(slide, ctx, item.text ?? item, x + 18, yy, w - 18, rowH, {
      size: item.size ?? opts.size ?? 12.5,
      color: item.textColor ?? opts.textColor ?? C.ink,
      bold: item.bold ?? false,
    });
  });
}

export function table(slide, ctx, columns, rows, x, y, w, rowH = 30, opts = {}) {
  const colW = columns.map((c) => c.w ?? w / columns.length);
  rect(slide, ctx, x, y, w, rowH, opts.headerFill ?? C.navy, "#00000000", 0);
  let xx = x;
  columns.forEach((c, i) => {
    text(slide, ctx, c.label, xx + 8, y + 7, colW[i] - 16, rowH - 10, { size: opts.headerSize ?? 10.5, color: C.white, bold: true, align: c.align ?? "left" });
    xx += colW[i];
  });
  rows.forEach((row, r) => {
    const yy = y + rowH * (r + 1);
    rect(slide, ctx, x, yy, w, rowH, r % 2 === 0 ? C.white : "#FAF7EF", C.line, 0.5);
    let cx = x;
    row.forEach((cell, i) => {
      text(slide, ctx, cell, cx + 8, yy + 7, colW[i] - 16, rowH - 10, {
        size: opts.bodySize ?? 10,
        color: C.ink,
        bold: opts.boldFirstCol && i === 0,
        align: columns[i].align ?? "left",
      });
      cx += colW[i];
    });
  });
}

export function flowStep(slide, ctx, n, label, sub, x, y, w, color = C.teal) {
  rect(slide, ctx, x, y, w, 86, "#FDFBF6", color, 2);
  text(slide, ctx, String(n).padStart(2, "0"), x + 14, y + 14, 42, 24, { size: 19, color, bold: true });
  text(slide, ctx, label, x + 58, y + 16, w - 70, 22, { size: 14, bold: true, color: C.ink });
  text(slide, ctx, sub, x + 16, y + 48, w - 32, 30, { size: 9.5, color: C.mute, align: "center" });
}

export function claimBar(slide, ctx, value, x, y, w, color = C.teal) {
  rect(slide, ctx, x, y, w, 44, C.teal2, color, 1);
  text(slide, ctx, value, x + 16, y + 11, w - 32, 24, { size: 13, color: C.ink, bold: true });
}

export async function image(slide, ctx, path, x, y, w, h, fit = "contain", alt = "") {
  return ctx.addImage(slide, { path, x, y, w, h, fit, alt });
}

export function hbar(slide, ctx, rows, x, y, w, h, maxValue, color = C.teal) {
  const rowH = h / rows.length;
  rows.forEach((row, i) => {
    const yy = y + i * rowH;
    text(slide, ctx, row.label, x, yy + 3, 120, 20, { size: 10.5, color: C.ink, bold: i === 0 });
    rect(slide, ctx, x + 130, yy + 7, w - 190, 10, "#E5E1D8");
    rect(slide, ctx, x + 130, yy + 7, (w - 190) * row.value / maxValue, 10, row.color || color);
    text(slide, ctx, row.valueText ?? row.value, x + w - 52, yy, 52, 20, {
      size: 10,
      color: C.mute,
      align: "right",
    });
  });
}
