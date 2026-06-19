# 数据准备阶段摘要

## 数据来源

| 文件 | 行数 | 说明 |
| --- | ---: | --- |
| `ml/data/raw/emotion_raw.csv` | 7860 | 原始文本数据：Hugging Face `dirtycomputer/ChnSentiCorp_htl_all` 酒店评论 7766 条 + Django 历史日记 + 项目已有公开短文本 |
| `ml/data/processed/emotion_labeled.csv` | 7885 | 二分类标注数据，主来源为酒店评论数据，并补充少量日记与校园场景样本 |

酒店评论数据字段映射为 `review -> text`、`label -> 0/1`。公开短文本当前只作为原始补充材料保留；中性文本、信息不足文本和强反讽文本不进入训练集。

## 标签分布

| label | 含义 | 数量 |
| --- | --- | ---: |
| `1` | 积极 | 5378 |
| `0` | 消极 | 2507 |

## 切分结果

| split | label=0 消极 | label=1 积极 | 总数 |
| --- | ---: | ---: | ---: |
| train | 2005 | 4302 | 6307 |
| valid | 250 | 538 | 788 |
| test | 251 | 538 | 789 |

切分方式为 `train_test_split(..., stratify=y)`，比例 8:1:1，随机种子为 42。

## 生成产物

| 产物 | 说明 |
| --- | --- |
| `ml/data/raw/emotion_raw.csv` | 原始文本汇总 |
| `ml/data/processed/emotion_labeled.csv` | 干净标注数据 |
| `ml/data/processed/train.csv` | 训练集 |
| `ml/data/processed/valid.csv` | 验证集 |
| `ml/data/processed/test.csv` | 测试集 |
| `ml/reports/label_distribution.csv` | 标签分布统计 |
| `ml/reports/label_distribution.png` | 标签分布柱状图 |
| `report/label_guide.md` | 标注规范 |
