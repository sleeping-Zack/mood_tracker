# mood_tracker · 情绪日记本地传统机器学习五分类版

本仓库在保留原 Django 情绪日记网页交互层与 SQLite 数据库的前提下，把"情绪识别内核"从原先依赖 Hugging Face API 的在线推理升级为完全本地的**传统机器学习五分类系统**：`jieba` 分词 + `TfidfVectorizer` 特征 + `MultinomialNB / LogisticRegression / LinearSVC` 分类器 + `joblib` 持久化 + `views.py` 调用 `predict_emotion()`。原 Hugging Face 流程仍保留为对照基线，K-Means 作为无监督拓展实验。

> 当前推理、入库和展示都以五分类为准：难过、焦虑、生气、平静、开心。

## 一、技术路线

```
现有 Django 项目
    └── 文本提交 (mood/views.py)
            └── ml.predict.predict_emotion(text)
                    ├── ml.preprocess.segment_text   # jieba + 停用词 + 自定义词典
                    ├── joblib.load(tfidf_vectorizer.joblib)
                    └── joblib.load(lr_model.joblib)  # 默认主模型 LinearSVC/LogisticRegression 二选一
            └── MoodEntry.objects.create(...)         # emotion_label / score / model_name
            └── 渲染 templates/mood/index.html        # 文本/情绪/模型/分析时间/趋势分值/建议
对照实验:
    ml/hf_predict.py          # 复用原 Hugging Face 接口
    ml/kmeans_experiment.py   # K-Means / LSA+K-Means 拓展
```

## 二、环境版本

按方案统一到 **Python 3.11**，依赖锁定见 `requirements.txt`：

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
| transformers (对照实验，可选) | `5.6.2` |
| torch (对照实验，可选) | `2.11.0` |

> 当前本机为 Python 3.9.13 + Django 4.2.20 + sklearn 1.0.2，已能完整跑通全流程。`scikit-learn` 官方不保证 joblib 模型跨版本加载，正式演示前请按本节版本重新训练并保存模型。

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\python.exe -m pip install -r requirements.txt
```

## 三、目录结构（与方案一致）

```
mood_tracker/
├── manage.py
├── requirements.txt
├── README.md
├── mood_tracker/                  # Django 项目配置
│   └── settings.py / urls.py / ...
├── mood/                          # Django 应用
│   ├── models.py                  # MoodEntry: emotion_label / score / model_name / analyzed_at
│   ├── views.py                   # POST 调 predict_emotion 并写库
│   ├── admin.py / urls.py
│   ├── sentiment_analysis.py      # 五分类提示语
│   ├── migrations/0004_...py      # 新字段迁移
│   └── templates/mood/index.html  # 输入框 + 本次分析结果 + 趋势图 + 历史记录
├── static/                        # 静态资源 + mood_trend.png
├── ml/
│   ├── config.py                  # 路径、标签、随机种子
│   ├── prepare_data.py            # Hugging Face 酒店评论数据 + 本地补充数据汇总
│   ├── split_dataset.py           # train/valid/test 8:1:1 分层切分
│   ├── preprocess.py              # clean_text / segment_text / load_user_dict / load_stopwords
│   ├── feature_engineering.py     # build_vectorizer / TF-IDF 配置对比
│   ├── train_model.py             # train_nb / train_lr / train_svm
│   ├── evaluate_model.py          # 测试集指标 + 混淆矩阵 + 误分类
│   ├── predict.py                 # load_artifacts + predict_emotion (Django 入口)
│   ├── hf_predict.py              # Hugging Face 对照实验
│   ├── kmeans_experiment.py       # K-Means / LSA+KMeans 拓展
│   ├── data/raw/emotion_raw.csv
│   ├── data/processed/{emotion_labeled,train,valid,test,*_segmented}.csv
│   ├── dicts/{user_dict,stopwords}.txt
│   ├── artifacts/{tfidf_vectorizer,nb_model,lr_model,svm_model}.joblib
│   └── reports/                   # 训练日志 / 模型对比 / 混淆矩阵 / 误分类 / KMeans / HF 对照
└── report/                        # 课程报告 markdown 摘要
    ├── project_environment.md
    ├── label_guide.md
    ├── data_preparation_summary.md
    ├── preprocessing_feature_summary.md
    ├── supervised_training_summary.md
    ├── test_evaluation_summary.md
    ├── contrast_unsupervised_summary.md
    └── django_integration_summary.md
```

## 四、五分类标签规范

| `label` | 中文情绪 | emotion key | `score` |
| --- | --- | --- | --- |
| `0` | 难过 | sad | -2 |
| `1` | 焦虑 | anxious | -1 |
| `2` | 生气 | angry | -2 |
| `3` | 平静 | calm |  0 |
| `4` | 开心 | happy | +2 |

所有这些常量都集中定义在 `ml/config.py`：`ALL_LABELS`、`LABEL_NAMES`、`LABEL_KEYS`、`LABEL_KEY_TO_LABEL`、`TREND_SCORE`、`EMOTION_MESSAGES`。其余脚本通过 `from ml.config import ...` 读取，避免在多个文件里重复硬编码。

主训练数据来自 Hugging Face `zzhdbw/Simplified_Chinese_Multi-Emotion_Dialogue_Dataset`：

- `开心 → 4`、`伤心 → 0`、`生气 → 2`、`厌恶 → 2`、`平静 → 3`
- `恐惧 / 担心 / 害怕 / 紧张` 若出现则映射为 `1` 焦虑
- `惊讶 / 关心 / 疑问` 直接丢弃，不进训练集

公开数据集里没有焦虑类，所以 `ml/build_5class_dataset.py` 里另外手工补了 ~260 条**大学生日记焦虑样本**（围绕期末/答辩/PPT/项目/DDL/老师检查/代码没完成…）。详见 `report/label_guide.md`。

## 五、如何重新训练（端到端）

```powershell
# 1. 数据准备 (五分类语料 + 焦虑样本补全)
python ml\build_5class_dataset.py
python ml\split_dataset.py

# 2. 预处理 + 特征工程
python ml\preprocess.py
python ml\feature_engineering.py

# 3. 监督模型训练 (NB / LR / SVM, 多分类, class_weight=balanced)
python ml\train_model.py

# 4. 测试集评估 + 五分类混淆矩阵 + 误分类
python ml\evaluate_model.py

# 5. 对照实验与无监督拓展 (可选)
python ml\kmeans_experiment.py
```

> 旧的 `python ml\prepare_data.py` 是二分类的数据准备脚本，目前仍保留作为历史对照入口；五分类训练请改用 `python ml\build_5class_dataset.py`。

输出位置：

| 产物 | 路径 |
| --- | --- |
| TF-IDF 向量器 | `ml/artifacts/tfidf_vectorizer.joblib` |
| NB / LR / SVM 模型 | `ml/artifacts/{nb,lr,svm}_model.joblib` |
| 训练日志 | `ml/reports/train_log.json` |
| 模型对比 | `ml/reports/model_compare.csv`、`test_model_compare.csv` |
| 混淆矩阵 | `ml/reports/confusion_matrix_{nb,lr,svm}.png` |
| F1 对比图 | `ml/reports/f1_bar.png` |
| 误分类案例 | `ml/reports/error_cases.csv` / `.xlsx` |
| HF / 延迟对照 | `ml/reports/hf_compare.csv`、`latency_compare.csv` |
| K-Means 结果 | `ml/reports/kmeans_compare.csv`、`kmeans_cluster_terms.csv`、`kmeans_vis.png` |

## 六、如何加载主模型并做单条预测

`ml/predict.py` 提供给 Django 调用的统一接口，模型与向量器在进程内懒加载并复用，避免每次请求都 `joblib.load()`：

```python
from ml.predict import predict_emotion

result = predict_emotion("今天答辩非常顺利，我很开心。")
# {
#   "label": 4,
#   "sentiment": "happy",
#   "emotion_key": "happy",
#   "emotion": "开心",
#   "score": 2,
#   "message": "情绪明显积极，继续保持当前节奏，并把这份能量留给重要的事情。",
#   "model_name": "TF-IDF + LogisticRegression",
#   "confidence": 0.6577,
#   "seg_text": "答辩 顺利 开心",
#   "predict_ms": 12.3,
#   "error": null
# }
```

命令行直接试：

```powershell
python ml\predict.py "今天答辩非常顺利，我很开心。"
python ml\predict.py "明天就要答辩了，PPT 还没完全准备好，心里很紧张。"
python ml\predict.py "今天代码一直报错，怎么改都不行，真的很烦。"
python ml\predict.py "今天正常上课，晚上简单复习了一会儿，整体还算平稳。"
```

主模型选择规则（与训练阶段一致）：先用验证集 `macro_f1`，再 `weighted_f1`、`accuracy`，平局时优先 LR，再 SVM，最后 NB。`best_model_info.json` 保存当前主模型路径。`positive_f1` 在五分类下不再适用，已从训练 / 评估指标中移除。

## 七、如何启动 Django 网页

```powershell
python manage.py migrate         # 首次或字段变更时
python manage.py check           # 系统自检
python manage.py runserver       # 默认 http://127.0.0.1:8000/
```

页面行为：

1. 用户在文本框写入心情。
2. POST 提交 → `mood/views.py::index` → `predict_emotion(text)` → 写入 `MoodEntry`。
3. 重定向回首页后展示：
   - 本次分析结果：文本、五分类中文情绪、所用模型、分析时间、趋势分值、建议语句。
   - 心情趋势图：基于 `display_score` 字段绘制，y 轴范围 `-2 ~ +2`，标题为 `Mood Score (-2=sad/angry, -1=anxious, 0=calm, 2=happy)`。
   - 历史记录列表：所有 `MoodEntry` 按时间倒序。

> 数据库迁移会把旧的 `positive / negative / neutral` 记录转换为五分类 key：`happy / sad|anxious|angry / calm`，之后页面和模型都不再使用旧三分类。

## 八、对照实验与无监督拓展

- `ml/hf_predict.py` 提供 `hf_predict(text)` 接口，优先使用本地缓存的 Hugging Face 模型（`uer/roberta-base-finetuned-jd-binary-chinese`），失败时回落到无 `local_files_only` 模式自动下载。结果记录在 `ml/reports/hf_compare.csv`。
- `ml/kmeans_experiment.py` 在同一 TF-IDF 特征上跑 `KMeans(n_clusters=2)`，并对比 `TruncatedSVD + Normalizer + KMeans` 的 LSA 流程，最终通过簇内多数标签做后验解释（不是把 cluster id 当真实标签）。

> 当前 Anaconda 全局环境的 `urllib3` 缺少 `DEFAULT_CIPHERS`，`transformers` 导入会失败，`hf_compare.csv` 会被记录为 `skipped`。切换到方案推荐的 Python 3.11 + transformers 5.6.2 + torch 2.11.0 后，对照实验数据会自动补齐。

## 九、部署提示（仅本地课堂演示）

```python
# mood_tracker/settings.py
DEBUG = True                                 # 课堂演示保持
ALLOWED_HOSTS = []                           # 仅本机回环；如需远端访问改成 ["你的IP", "localhost"]
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

正式部署时按 Django 部署清单：

```powershell
python manage.py check --deploy
```

并设置 `DEBUG=False`、合理的 `ALLOWED_HOSTS`、用 `gunicorn` / `uvicorn` 等替代 `runserver`。

## 十、报告与图表导引

| 文件 | 阶段 |
| --- | --- |
| `report/project_environment.md` | 立项与环境定版 |
| `report/label_guide.md`、`report/data_preparation_summary.md` | 数据准备 |
| `report/preprocessing_feature_summary.md` | 预处理与特征工程 |
| `report/supervised_training_summary.md` | 监督模型训练 |
| `report/test_evaluation_summary.md` | 评估与误差分析 |
| `report/contrast_unsupervised_summary.md` | 对照实验与 K-Means |
| `report/django_integration_summary.md` | Django 集成 |

## 十一、迁移自旧版本的关键变更

| 旧实现 (二分类) | 新实现 (五分类) |
| --- | --- |
| `LABEL_NEGATIVE / LABEL_POSITIVE` 写在多处 | 统一改为 `LABEL_SAD / LABEL_ANXIOUS / LABEL_ANGRY / LABEL_CALM / LABEL_HAPPY`，所有映射集中到 `ml/config.py` |
| `predict_emotion` 只返回 `1 / 0` | 返回 `0–4` 的 `label`，并附带 `emotion`、`emotion_key`、`score`、`message`、`confidence` |
| `MoodEntry` `EMOTION_LABEL_CHOICES` 只有 0/1 | 升级为五分类，`save()` 按五分类同步 `score / sentiment`，其中 `sentiment` 存储 `sad/anxious/angry/calm/happy` |
| 趋势图基于 `+1 / 0 / -1` | 趋势图基于 `display_score`，y 轴 `-2 ~ +2`，按五分类绘制 |
| 模型选择主指标是 `positive_f1` | 改为 `macro_f1 → weighted_f1 → accuracy`，`positive_f1` 从训练 / 评估流程中移除 |
| 混淆矩阵 / 误分类表用 `false_positive / false_negative` 二分类术语 | 混淆矩阵显示难过/焦虑/生气/平静/开心五个中文标签，误分类表统一输出 `true_label / pred_label / true_emotion / pred_emotion / text / model_key` |
| 数据来自 ChnSentiCorp 酒店评论 | 改为 `zzhdbw/Simplified_Chinese_Multi-Emotion_Dialogue_Dataset` 多情绪对话数据 + 手工补充的大学生焦虑样本 |
| 推理依赖网络 | 全离线，joblib 加载 |

旧三分类推理逻辑已经从默认 Django 流程中移除，默认推理路径是 `predict_emotion` 五分类。
