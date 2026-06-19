# 监督模型训练阶段摘要

## 阶段目标

按照 PDF 第四阶段要求，基于第三阶段生成的 `seg_text` 与 TF-IDF 特征，训练三个传统监督分类模型：

| 模型 | 配置 |
| --- | --- |
| NB | `MultinomialNB(alpha=1.0)` |
| LR | `LogisticRegression(max_iter=1000, random_state=42)` |
| SVM | `LinearSVC(random_state=42)` |

本阶段只使用训练集训练、验证集对比，不使用测试集做最终评价；混淆矩阵、测试集指标和误分类分析留到下一阶段。

## 输入数据

| 输入 | 数量 | 说明 |
| --- | ---: | --- |
| `ml/data/processed/train_segmented.csv` | 6307 | 训练集分词文本 |
| `ml/data/processed/valid_segmented.csv` | 788 | 验证集分词文本 |

TF-IDF 配置沿用第三阶段主配置：`ngram_range=(1, 2)`、`max_features=8000`、`min_df=2`、`max_df=0.9`。训练阶段重新 `fit` 向量器，并与模型一起保存，避免模型和向量器不匹配。

## 验证集结果

| rank | model | Accuracy | Positive Precision | Positive Recall | Positive F1 | Macro F1 | Weighted F1 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | LinearSVC | 0.885787 | 0.910256 | 0.923792 | 0.916974 | 0.867024 | 0.885280 |
| 2 | LogisticRegression | 0.883249 | 0.891228 | 0.944238 | 0.916968 | 0.860193 | 0.880943 |
| 3 | MultinomialNB | 0.860406 | 0.861486 | 0.947955 | 0.902655 | 0.828009 | 0.855291 |

LinearSVC 在验证集上 Macro F1 最高，因此第四阶段主模型选择为 LinearSVC。

## 生成产物

| 产物 | 说明 |
| --- | --- |
| `ml/artifacts/tfidf_vectorizer.joblib` | 训练阶段重新 fit 后保存的 TF-IDF 向量器 |
| `ml/artifacts/nb_model.joblib` | NB 模型 |
| `ml/artifacts/lr_model.joblib` | LR 模型 |
| `ml/artifacts/svm_model.joblib` | SVM 模型 |
| `ml/reports/train_log.json` | 训练参数、环境版本、训练耗时与验证指标 |
| `ml/reports/model_compare.csv` | 三个模型的验证集对比表 |
| `ml/reports/best_model_info.json` | 当前阶段主模型选择记录 |

## 环境说明

PDF 推荐 Python 3.11 + scikit-learn 1.8.0。当前机器实际用于训练的全局环境为 Python 3.9.13、scikit-learn 1.0.2、joblib 1.1.0。由于 scikit-learn 官方不保证 joblib 模型跨版本加载，后续切换到正式 Python 3.11 环境后，建议重新运行：

```powershell
python ml\preprocess.py
python ml\feature_engineering.py
python ml\train_model.py
```
