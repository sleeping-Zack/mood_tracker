# 测试集评估阶段摘要

## 阶段目标

按照 PDF 第五阶段要求，在测试集上对 NB、LR、SVM 三个监督模型进行最终评估，输出 Accuracy、积极类 Precision/Recall/F1、Macro F1、Weighted F1、混淆矩阵、F1 柱状图和误分类案例。

## 输入

| 输入 | 说明 |
| --- | --- |
| `ml/data/processed/test_segmented.csv` | 测试集分词文本，789 条 |
| `ml/artifacts/tfidf_vectorizer.joblib` | 训练阶段保存的 TF-IDF 向量器 |
| `ml/artifacts/nb_model.joblib` | NB 模型 |
| `ml/artifacts/lr_model.joblib` | LR 模型 |
| `ml/artifacts/svm_model.joblib` | SVM 模型 |

## 测试集结果

| rank | model | Accuracy | Positive Precision | Positive Recall | Positive F1 | Macro F1 | Weighted F1 | 混淆矩阵 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | LogisticRegression | 0.885932 | 0.891608 | 0.947955 | 0.918919 | 0.863306 | 0.883535 | `[[189, 62], [28, 510]]` |
| 2 | LinearSVC | 0.880862 | 0.906593 | 0.920074 | 0.913284 | 0.861500 | 0.880337 | `[[200, 51], [43, 495]]` |
| 3 | MultinomialNB | 0.842839 | 0.846154 | 0.940520 | 0.890845 | 0.805151 | 0.836322 | `[[159, 92], [32, 506]]` |

混淆矩阵行列顺序均为 `[0=消极, 1=积极]`，含义是：第 `i,j` 项表示真实类别为 `i`、预测类别为 `j` 的样本数。

## 误分类情况

| model | false_positive | false_negative |
| --- | ---: | ---: |
| LogisticRegression | 62 | 28 |
| LinearSVC | 51 | 43 |
| MultinomialNB | 92 | 32 |

`error_cases.csv` 中共 308 行，是按模型展开后的误分类记录。

## 生成产物

| 产物 | 说明 |
| --- | --- |
| `ml/reports/model_compare.csv` | 测试集模型总表，按 PDF 文件名输出 |
| `ml/reports/test_model_compare.csv` | 测试集模型总表副本 |
| `ml/reports/confusion_matrix_nb.png` | NB 混淆矩阵 |
| `ml/reports/confusion_matrix_lr.png` | LR 混淆矩阵 |
| `ml/reports/confusion_matrix_svm.png` | SVM 混淆矩阵 |
| `ml/reports/f1_bar.png` | F1 柱状图 |
| `ml/reports/error_cases.csv` | 误分类案例 |
| `ml/reports/error_cases.xlsx` | 误分类案例表格 |
| `ml/reports/evaluation_log.json` | 评估日志与 classification_report |

## 当前主模型

测试集上 LogisticRegression 略高，但系统当前沿用训练阶段的主模型选择规则：以验证集 Macro F1 选择主模型，因此 Django 默认加载 LinearSVC。
