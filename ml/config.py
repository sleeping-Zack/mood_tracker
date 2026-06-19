from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "ml" / "data" / "raw" / "emotion_raw.csv"
LABELED_DATA_PATH = BASE_DIR / "ml" / "data" / "processed" / "emotion_labeled.csv"
TRAIN_DATA_PATH = BASE_DIR / "ml" / "data" / "processed" / "train.csv"
VALID_DATA_PATH = BASE_DIR / "ml" / "data" / "processed" / "valid.csv"
TEST_DATA_PATH = BASE_DIR / "ml" / "data" / "processed" / "test.csv"
TRAIN_SEGMENTED_PATH = BASE_DIR / "ml" / "data" / "processed" / "train_segmented.csv"
VALID_SEGMENTED_PATH = BASE_DIR / "ml" / "data" / "processed" / "valid_segmented.csv"
TEST_SEGMENTED_PATH = BASE_DIR / "ml" / "data" / "processed" / "test_segmented.csv"

USER_DICT_PATH = BASE_DIR / "ml" / "dicts" / "user_dict.txt"
STOPWORDS_PATH = BASE_DIR / "ml" / "dicts" / "stopwords.txt"

VECTORIZER_PATH = BASE_DIR / "ml" / "artifacts" / "tfidf_vectorizer.joblib"
NB_MODEL_PATH = BASE_DIR / "ml" / "artifacts" / "nb_model.joblib"
LR_MODEL_PATH = BASE_DIR / "ml" / "artifacts" / "lr_model.joblib"
SVM_MODEL_PATH = BASE_DIR / "ml" / "artifacts" / "svm_model.joblib"

MODEL_COMPARE_PATH = BASE_DIR / "ml" / "reports" / "model_compare.csv"
TEST_MODEL_COMPARE_PATH = BASE_DIR / "ml" / "reports" / "test_model_compare.csv"
EVALUATION_LOG_PATH = BASE_DIR / "ml" / "reports" / "evaluation_log.json"
F1_BAR_PATH = BASE_DIR / "ml" / "reports" / "f1_bar.png"
ERROR_CASES_CSV_PATH = BASE_DIR / "ml" / "reports" / "error_cases.csv"
ERROR_CASES_XLSX_PATH = BASE_DIR / "ml" / "reports" / "error_cases.xlsx"
CONFUSION_MATRIX_NB_PATH = BASE_DIR / "ml" / "reports" / "confusion_matrix_nb.png"
CONFUSION_MATRIX_LR_PATH = BASE_DIR / "ml" / "reports" / "confusion_matrix_lr.png"
CONFUSION_MATRIX_SVM_PATH = BASE_DIR / "ml" / "reports" / "confusion_matrix_svm.png"
TRAIN_LOG_PATH = BASE_DIR / "ml" / "reports" / "train_log.json"
BEST_MODEL_INFO_PATH = BASE_DIR / "ml" / "reports" / "best_model_info.json"
HF_COMPARE_PATH = BASE_DIR / "ml" / "reports" / "hf_compare.csv"
LATENCY_COMPARE_PATH = BASE_DIR / "ml" / "reports" / "latency_compare.csv"
KMEANS_CLUSTER_TERMS_PATH = BASE_DIR / "ml" / "reports" / "kmeans_cluster_terms.csv"
KMEANS_COMPARE_PATH = BASE_DIR / "ml" / "reports" / "kmeans_compare.csv"
KMEANS_VIS_PATH = BASE_DIR / "ml" / "reports" / "kmeans_vis.png"
LABEL_DISTRIBUTION_PATH = BASE_DIR / "ml" / "reports" / "label_distribution.png"
LABEL_DISTRIBUTION_CSV_PATH = BASE_DIR / "ml" / "reports" / "label_distribution.csv"
VOCAB_STATS_PATH = BASE_DIR / "ml" / "reports" / "vocab_stats.csv"
SEGMENT_PREVIEW_PATH = BASE_DIR / "ml" / "reports" / "segment_preview.csv"

LABEL_SAD = 0
LABEL_ANXIOUS = 1
LABEL_ANGRY = 2
LABEL_CALM = 3
LABEL_HAPPY = 4

ALL_LABELS = [LABEL_SAD, LABEL_ANXIOUS, LABEL_ANGRY, LABEL_CALM, LABEL_HAPPY]

LABEL_NAMES = {
    LABEL_SAD: "难过",
    LABEL_ANXIOUS: "焦虑",
    LABEL_ANGRY: "生气",
    LABEL_CALM: "平静",
    LABEL_HAPPY: "开心",
}

EMOTION_TO_LABEL = {emotion: label for label, emotion in LABEL_NAMES.items()}

LABEL_KEYS = {
    LABEL_SAD: "sad",
    LABEL_ANXIOUS: "anxious",
    LABEL_ANGRY: "angry",
    LABEL_CALM: "calm",
    LABEL_HAPPY: "happy",
}

LABEL_KEY_TO_LABEL = {emotion_key: label for label, emotion_key in LABEL_KEYS.items()}

TREND_SCORE = {
    LABEL_SAD: -2,
    LABEL_ANXIOUS: -1,
    LABEL_ANGRY: -2,
    LABEL_CALM: 0,
    LABEL_HAPPY: 2,
}

EMOTION_MESSAGES = {
    LABEL_SAD: "情绪偏难过，允许自己慢下来，给自己一点温柔的时间。",
    LABEL_ANXIOUS: "感觉到比较明显的焦虑，建议先把任务拆小，再优先处理一件最紧迫的事。",
    LABEL_ANGRY: "情绪偏生气，先深呼吸几次，避免立即做重要决定。",
    LABEL_CALM: "情绪整体平静，可以利用这段稳定状态做一些需要专注的事。",
    LABEL_HAPPY: "情绪明显积极，继续保持当前节奏，并把这份能量留给重要的事情。",
}

RANDOM_STATE = 42
TRAIN_RATIO = 0.8
VALID_RATIO = 0.1
TEST_RATIO = 0.1
