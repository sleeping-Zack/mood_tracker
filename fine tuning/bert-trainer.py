from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import re
import numpy as np
from sklearn.metrics import accuracy_score

# 加载模型和分词器
tokenizer = AutoTokenizer.from_pretrained("uer/roberta-base-finetuned-jd-binary-chinese")
model = AutoModelForSequenceClassification.from_pretrained("uer/roberta-base-finetuned-jd-binary-chinese")

# 加载数据集
dataset = load_dataset('lansinuote/ChnSentiCorp')

# 文本清洗函数
def clean_text(example):
    example['text'] = re.sub(r'[^\w\s]', '', example['text']).strip()
    return example

dataset = dataset.map(clean_text)

# 分词函数
def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=128)

encoded_dataset = dataset.map(tokenize_function, batched=True)

# 设置训练参数
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=1,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    evaluation_strategy="epoch",
    logging_dir='./logs',
)

# 定义评估指标
def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    return {"accuracy": accuracy_score(p.label_ids, preds)}
# # 只取训练集前300条数据
# small_train_dataset = encoded_dataset['train'].select(range(300))
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=small_train_dataset,  # 使用300条数据训练
#     eval_dataset=encoded_dataset['validation'],
#     compute_metrics=compute_metrics,
# )

# 创建 Trainer 实例
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset['train'],
    eval_dataset=encoded_dataset['validation'],
    compute_metrics=compute_metrics,
)

# 训练模型
trainer.train()

# 评估模型
trainer.evaluate(encoded_dataset['test'])

# 保存模型和分词器
model.save_pretrained('./sentiment_model')
tokenizer.save_pretrained('./sentiment_model')