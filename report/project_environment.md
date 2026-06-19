# 立项与环境定版

## 技术路线

按照 PDF，本项目不重写网站，而是保留现有 Django 交互层与 SQLite 数据库层，后续只替换情绪识别内核：`jieba` 分词、`TfidfVectorizer` 特征提取、`MultinomialNB` / `LogisticRegression` / `LinearSVC` 分类、`joblib` 持久化，并在后续阶段由 `views.py` 调用 `predict_emotion()`。

## 环境版本

PDF 推荐统一到 Python 3.11，依赖锁定为：

| 依赖 | 版本 |
| --- | --- |
| Django | `5.2.*` |
| scikit-learn | `1.8.0` |
| jieba | `0.42.1` |
| joblib | `1.5.3` |
| pandas | `3.0.2` |
| numpy | `2.4.4` |
| matplotlib | `3.10.9` |
| datasets | `4.5.0` |

本仓库已新增 `requirements.txt` 固定上述版本。当前机器扫描结果：全局 `python` 为 3.9.13，现有 `.venv` 为 Python 3.8.10 + Django 4.2.30；未检测到可直接创建 3.11 环境的 `py -3.11`。因此本阶段先完成依赖锁定与目录规范，实际安装需在本机具备 Python 3.11 后执行。

建议命令：

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\python.exe -m pip install -r requirements.txt
```

## 目录结构

| 路径 | 作用 |
| --- | --- |
| `requirements.txt` | 固定依赖版本 |
| `ml/data/raw/emotion_raw.csv` | 原始文本数据 |
| `ml/data/processed/emotion_labeled.csv` | 清洗与人工规则标注后的训练数据 |
| `ml/data/processed/train.csv` | 训练集 |
| `ml/data/processed/valid.csv` | 验证集 |
| `ml/data/processed/test.csv` | 测试集 |
| `ml/dicts/user_dict.txt` | 自定义词典 |
| `ml/dicts/stopwords.txt` | 停用词表 |
| `ml/artifacts/tfidf_vectorizer.joblib` | 后续阶段保存 TF-IDF 向量器 |
| `ml/artifacts/nb_model.joblib` | 后续阶段保存 NB 模型 |
| `ml/artifacts/lr_model.joblib` | 后续阶段保存 LR 模型 |
| `ml/artifacts/svm_model.joblib` | 后续阶段保存 SVM 模型 |
| `ml/reports/model_compare.csv` | 后续阶段保存模型对比结果 |
| `ml/reports/label_distribution.png` | 标签分布图 |
| `ml/config.py` | 统一路径、标签与随机种子配置 |
| `ml/prepare_data.py` | 读取 Hugging Face `dirtycomputer/ChnSentiCorp_htl_all`，并合并本地日记与人工样本 |
| `ml/split_dataset.py` | 按 8:1:1 分层切分数据 |
| `report/label_guide.md` | 标注规范 |

## 标签规范

训练标签只使用二分类：

| 标签 | 含义 |
| --- | --- |
| `1` | 积极 |
| `0` | 消极 |

页面趋势分值与训练标签分开处理：后续页面趋势可将 `1` 映射为 `+1`，将 `0` 映射为 `-1`。中性、客观陈述、信息不足、强反讽文本暂不进入训练集。

## 脚本接口规范

| 脚本 | 函数名 | 参数 | 返回值 | 说明 |
| --- | --- | --- | --- | --- |
| `ml/prepare_data.py` | `read_hotel_review_rows` | 无 | `list[dict]` | 从 Hugging Face 加载酒店评论情感数据 |
| `ml/prepare_data.py` | `build_raw_rows` | 无 | `list[dict]` | 汇总酒店评论数据、原日记文本与公开短文本原始数据 |
| `ml/prepare_data.py` | `build_labeled_rows` | 无 | `list[dict]` | 生成酒店评论主数据 + 本地补充的二分类标注数据 |
| `ml/split_dataset.py` | `split_dataset` | `input_path, train_path, valid_path, test_path` | `dict` | 去空值、去重、按标签分层切分 |
| `ml/split_dataset.py` | `save_label_distribution` | `input_path, csv_path, figure_path` | `DataFrame` | 输出每个 split 的标签分布与柱状图 |

后续阶段再补充 PDF 中的 `clean_text()`、`segment_text()`、`build_vectorizer()`、`train_nb()`、`train_lr()`、`train_svm()`、`evaluate_classifier()`、`predict_emotion()` 等接口。
