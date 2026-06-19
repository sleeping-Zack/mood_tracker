# Django 集成与模型持久化阶段摘要

## 阶段目标

按照 PDF 的 Django 集成阶段要求，将训练好的本地传统机器学习模型接入现有情绪日记项目：页面提交文本后，`views.py` 调用 `predict_emotion()`，预测结果写入数据库，并在页面展示文本内容、预测情绪、所用模型、分析时间和建议语句。

## 已实现内容

| 文件 | 说明 |
| --- | --- |
| `ml/predict.py` | 本地预测接口，懒加载 `tfidf_vectorizer.joblib` 与主模型 |
| `mood/models.py` | 增加模型预测结果字段与趋势分值映射 |
| `mood/views.py` | 表单 POST 后调用 `predict_emotion()` 并写库 |
| `mood/templates/mood/index.html` | 展示本次分析结果、趋势图和历史记录 |
| `mood/admin.py` | 后台展示情绪标签、分值、模型名和分析时间 |
| `mood/migrations/0004_moodentry_analysis_message_moodentry_analyzed_at_and_more.py` | 数据库字段迁移 |

## 预测接口

`ml/predict.py` 提供：

| 函数 | 说明 |
| --- | --- |
| `load_artifacts(vectorizer_path, model_path)` | 加载并缓存向量器与模型 |
| `segment_for_prediction(text)` | 使用与训练阶段一致的 jieba 分词、用户词典和停用词 |
| `predict_emotion(text)` | 返回标签、中文情绪、趋势分值、建议语句、模型名、置信度和分词文本 |

模型加载采用懒加载：Django 启动时不会立即加载 joblib 文件，首次预测时才加载，并在进程内复用，避免每次请求都重复 `joblib.load()`。

## 数据库字段

| 字段 | 说明 |
| --- | --- |
| `emotion_label` | 五分类训练标签：`0=难过`、`1=焦虑`、`2=生气`、`3=平静`、`4=开心` |
| `sentiment` | 五分类 emotion key：`sad/anxious/angry/calm/happy` |
| `score` | 页面趋势分值：`-2/-1/0/+2` |
| `model_name` | 例如 `TF-IDF + LogisticRegression` |
| `analysis_message` | 预测后的建议语句 |
| `analyzed_at` | 分析时间 |

`sentiment` 字段不再使用 `positive / negative / neutral`，新记录会根据 `emotion_label` 自动同步为五分类 emotion key。

## 页面展示

首页现在展示：

| 区域 | 内容 |
| --- | --- |
| 本次分析结果 | 文本、预测情绪、所用模型、分析时间、趋势分值、建议语句 |
| 心情趋势 | `score` 趋势图，范围为 `-2 ~ +2` |
| 历史记录 | 每条文本的情绪、分值和模型名 |

## 验证结果

已执行：

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations mood
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
python manage.py check
python ml\predict.py "今天答辩很顺利，我很开心"
```

还用 Django test client 做了首页 GET 和临时 POST 集成测试，POST 能调用本地模型并写入预测字段，测试记录已删除。

## 环境注意事项

当前 `.venv` 只有 Django，没有 sklearn/joblib/jieba，因此它能启动和渲染页面，但实际 POST 预测会返回“本地模型不可用”。当前全局 Python 环境具备 ML 依赖，已验证可加载 joblib 模型。正式演示建议使用 PDF 推荐环境安装：

```powershell
python -m pip install -r requirements.txt
python ml\preprocess.py
python ml\train_model.py
python manage.py runserver
```

由于 joblib 模型不建议跨 scikit-learn 版本复用，切换到 Python 3.11 + scikit-learn 1.8.0 后，应重新训练并保存模型。
