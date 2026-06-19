# 预处理与特征工程阶段摘要

## 阶段目标

按照 PDF 第三阶段要求，将中文情绪日记文本转成传统机器学习可用的数值特征：先做文本清洗，再用 `jieba.lcut()` 精确模式分词，去除停用词，最后用 `TfidfVectorizer` 生成 TF-IDF 特征。

## 已实现脚本

| 脚本 | 函数 | 说明 |
| --- | --- | --- |
| `ml/preprocess.py` | `clean_text(text)` | 去空白、统一全角半角、清理极端噪声符号 |
| `ml/preprocess.py` | `load_stopwords(path)` | 读取停用词表 |
| `ml/preprocess.py` | `load_user_dict(path)` | 加载校园场景自定义词典 |
| `ml/preprocess.py` | `segment_text(text, stopwords, use_user_dict=True)` | jieba 精确模式分词并返回空格拼接 token |
| `ml/preprocess.py` | `preprocess_all()` | 生成 train/valid/test 三份分词数据 |
| `ml/feature_engineering.py` | `build_vectorizer(...)` | 构建 TF-IDF 向量器 |
| `ml/feature_engineering.py` | `fit_feature_configs(...)` | 评估 unigram 与 unigram+bigram 两套特征配置，并保存主向量器 |

## 预处理产物

| 产物 | 说明 |
| --- | --- |
| `ml/data/processed/train_segmented.csv` | 训练集清洗与分词结果 |
| `ml/data/processed/valid_segmented.csv` | 验证集清洗与分词结果 |
| `ml/data/processed/test_segmented.csv` | 测试集清洗与分词结果 |
| `ml/reports/segment_preview.csv` | 原始文本、清洗后文本、分词结果三列表预览 |
| `ml/dicts/user_dict.txt` | 校园场景自定义词典 |
| `ml/dicts/stopwords.txt` | 停用词表，包含常见虚词和标点 |

## TF-IDF 配置

两套配置均使用：

```python
TfidfVectorizer(
    tokenizer=str.split,
    preprocessor=None,
    token_pattern=None,
    lowercase=False,
    max_features=8000,
    min_df=2,
    max_df=0.9,
)
```

差异只在 `ngram_range`：

| config_name | ngram_range | vocab_size | train_features | train_sparsity | valid_sparsity | test_sparsity |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `tfidf_unigram` | `[1, 1]` | 8000 | 8000 | 0.994746 | 0.995151 | 0.994827 |
| `tfidf_unigram_bigram` | `[1, 2]` | 8000 | 8000 | 0.993549 | 0.994076 | 0.993691 |

## 保存的向量器

主向量器已保存到：

```text
ml/artifacts/tfidf_vectorizer.joblib
```

保存的是 `ngram_range=(1, 2)` 的 TF-IDF 向量器，供后续监督模型训练阶段复用。当前阶段只保存向量器，不训练 NB/LR/SVM。

## 环境说明

PDF 推荐 Python 3.11 + scikit-learn 1.8.0。当前机器用于生成本阶段产物的全局环境为 scikit-learn 1.0.2、joblib 1.1.0、pandas 2.2.3、jieba 0.42.1；后续在正式 Python 3.11 环境安装 `requirements.txt` 后，建议重新运行：

```powershell
python ml\preprocess.py
python ml\feature_engineering.py
```
