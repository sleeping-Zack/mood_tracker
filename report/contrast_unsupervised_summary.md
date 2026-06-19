# 对照实验与无监督拓展阶段摘要

## 阶段目标

按照 PDF 第六阶段要求，保留旧 Hugging Face 方案作为对照实验接口，同时使用 KMeans 做无监督拓展实验。需要强调：Hugging Face 是对照基线，KMeans 是课程拓展，真正准备接入 Django 的仍然是监督学习主模型。

## Hugging Face 对照实验

已新增 `ml/hf_predict.py` 和 `run_hf_compare()`。`_get_classifier()` 采用两段式加载：先尝试 `local_files_only=True` 复用本机已有 Hugging Face 缓存；缓存不存在时再回落到无 `local_files_only` 模式自动下载，与原项目 `mood/sentiment_analysis.py` 行为对齐。

本机运行结果：

| method | status | samples | 说明 |
| --- | --- | ---: | --- |
| `huggingface_local_cache` | `skipped` | 12 | 当前 Anaconda 全局环境 `transformers` 导入失败，未能完成 HF 指标计算 |

失败原因记录在 `ml/reports/hf_compare.csv`：`transformers` 导入链路中无法从当前 `urllib3.util.ssl_` 导入 `DEFAULT_CIPHERS`。这属于当前 Python 环境依赖冲突，不影响本地传统机器学习模型已经完成的训练与评估。切换到方案推荐的 Python 3.11 + `transformers==5.6.2` + `torch==2.11.0` 后，再次运行 `python ml\kmeans_experiment.py` 即可补齐 HF 对照数据。

## 延迟对比

| method | samples | avg_ms_per_sample | 是否依赖网络 |
| --- | ---: | ---: | --- |
| `local_lr` | 789 | 0.000167 | 否 |
| `huggingface_local_cache` | 50 | 空 | 当前不可用；脚本运行不联网，但需要本地模型缓存 |

## KMeans 拓展实验

| experiment | cluster_to_label | Accuracy after mapping | Macro F1 after mapping |
| --- | --- | ---: | ---: |
| `tfidf_kmeans` | `{"0": 1, "1": 0}` | 0.683368 | 0.612961 |
| `lsa_kmeans` | `{"1": 0, "0": 1}` | 0.699382 | 0.687596 |

这里的类别映射是后验解释：先聚类，再根据簇内多数真实标签把 cluster id 映射为“偏积极/偏消极”。不能把 `cluster=0` 直接等同于消极，也不能把 `cluster=1` 直接等同于积极。

## 高频词结果

| experiment | cluster | top_terms |
| --- | ---: | --- |
| `tfidf_kmeans` | 0 | 酒店 不错 房间 好 还 比较 服务 住 可以 不 早餐 方便 |
| `tfidf_kmeans` | 1 | 酒店 我们 房间 说 月 不 入住 日 年 到 给 您 |

## 生成产物

| 产物 | 说明 |
| --- | --- |
| `ml/hf_predict.py` | Hugging Face 对照接口 |
| `ml/kmeans_experiment.py` | HF 对照、延迟对比、KMeans 拓展实验脚本 |
| `ml/reports/hf_compare.csv` | HF 对照结果或 skipped 记录 |
| `ml/reports/latency_compare.csv` | 本地模型与 HF 对照延迟表 |
| `ml/reports/kmeans_cluster_terms.csv` | KMeans 每簇高频词 |
| `ml/reports/kmeans_compare.csv` | TF-IDF KMeans 与 LSA+KMeans 对比 |
| `ml/reports/kmeans_vis.png` | LSA 后二维聚类可视化 |

## 结论

当前数据规模较小，KMeans 只能作为课程拓展展示，不适合替代监督模型做情绪判别。后续 Django 接入阶段应继续使用监督学习主模型 LogisticRegression。
