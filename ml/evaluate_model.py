import json
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, Tuple

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

try:
    from ml.config import (
        ALL_LABELS,
        CONFUSION_MATRIX_LR_PATH,
        CONFUSION_MATRIX_NB_PATH,
        CONFUSION_MATRIX_SVM_PATH,
        ERROR_CASES_CSV_PATH,
        ERROR_CASES_XLSX_PATH,
        EVALUATION_LOG_PATH,
        F1_BAR_PATH,
        LABEL_NAMES,
        LR_MODEL_PATH,
        MODEL_COMPARE_PATH,
        NB_MODEL_PATH,
        SVM_MODEL_PATH,
        TEST_MODEL_COMPARE_PATH,
        TEST_SEGMENTED_PATH,
        VECTORIZER_PATH,
    )
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import (
        ALL_LABELS,
        CONFUSION_MATRIX_LR_PATH,
        CONFUSION_MATRIX_NB_PATH,
        CONFUSION_MATRIX_SVM_PATH,
        ERROR_CASES_CSV_PATH,
        ERROR_CASES_XLSX_PATH,
        EVALUATION_LOG_PATH,
        F1_BAR_PATH,
        LABEL_NAMES,
        LR_MODEL_PATH,
        MODEL_COMPARE_PATH,
        NB_MODEL_PATH,
        SVM_MODEL_PATH,
        TEST_MODEL_COMPARE_PATH,
        TEST_SEGMENTED_PATH,
        VECTORIZER_PATH,
    )


def _configure_chinese_font() -> None:
    """Try to register a Chinese-capable font so confusion matrices render Chinese cleanly."""
    candidates = [
        "Microsoft YaHei",
        "SimHei",
        "Source Han Sans CN",
        "Noto Sans CJK SC",
        "PingFang SC",
        "WenQuanYi Zen Hei",
        "Arial Unicode MS",
    ]
    available = {font.name for font in matplotlib.font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            matplotlib.rcParams["font.sans-serif"] = [name]
            matplotlib.rcParams["axes.unicode_minus"] = False
            return
    matplotlib.rcParams["axes.unicode_minus"] = False


_configure_chinese_font()


MODEL_SPECS = {
    "nb": ("MultinomialNB", NB_MODEL_PATH, CONFUSION_MATRIX_NB_PATH),
    "lr": ("LogisticRegression", LR_MODEL_PATH, CONFUSION_MATRIX_LR_PATH),
    "svm": ("LinearSVC", SVM_MODEL_PATH, CONFUSION_MATRIX_SVM_PATH),
}
MODEL_PREFERENCE_RANK = {
    "lr": 1,
    "svm": 2,
    "nb": 3,
}

DISPLAY_LABELS = [LABEL_NAMES[label] for label in ALL_LABELS]


def evaluate_classifier(model, x_test, y_test, labels: Iterable[int] = tuple(ALL_LABELS)) -> Dict[str, object]:
    started = time.perf_counter()
    y_pred = model.predict(x_test)
    predict_seconds = time.perf_counter() - started
    sample_count = len(y_test)
    label_list = list(labels)

    return {
        "accuracy": round(accuracy_score(y_test, y_pred), 6),
        "macro_f1": round(f1_score(y_test, y_pred, average="macro", labels=label_list, zero_division=0), 6),
        "weighted_f1": round(f1_score(y_test, y_pred, average="weighted", labels=label_list, zero_division=0), 6),
        "macro_precision": round(precision_score(y_test, y_pred, average="macro", labels=label_list, zero_division=0), 6),
        "macro_recall": round(recall_score(y_test, y_pred, average="macro", labels=label_list, zero_division=0), 6),
        "predict_ms_per_sample": round((predict_seconds / sample_count) * 1000, 6) if sample_count else 0,
        "report": classification_report(
            y_test,
            y_pred,
            labels=label_list,
            target_names=[LABEL_NAMES[label] for label in label_list],
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=label_list).tolist(),
        "y_pred": y_pred,
    }


def plot_confusion_matrix_figure(
    y_true,
    y_pred,
    save_path: Path,
    labels: Iterable[int] = tuple(ALL_LABELS),
    display_labels: Iterable[str] = None,
) -> str:
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    label_list = list(labels)
    if display_labels is None:
        display_labels = [LABEL_NAMES[label] for label in label_list]
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        labels=label_list,
        display_labels=list(display_labels),
        ax=ax,
        colorbar=False,
        xticks_rotation=30,
    )
    ax.set_title(save_path.stem)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
    return str(save_path)


def plot_f1_bar(compare_df: pd.DataFrame, save_path: Path = F1_BAR_PATH) -> str:
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(compare_df))
    ax.bar(x, compare_df["macro_f1"], width=0.35, label="macro F1", color="#4c78a8")
    ax.bar([i + 0.35 for i in x], compare_df["weighted_f1"], width=0.35, label="weighted F1", color="#f58518")
    ax.set_xticks([i + 0.175 for i in x])
    ax.set_xticklabels(compare_df["model_key"].tolist())
    ax.set_ylim(0, 1)
    ax.set_ylabel("F1")
    ax.set_title("Test-set F1 comparison (5-class)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
    return str(save_path)


def _save_error_cases(test_df: pd.DataFrame, predictions: Dict[str, Iterable[int]]) -> pd.DataFrame:
    rows = []
    for model_key, y_pred in predictions.items():
        for idx, pred in enumerate(y_pred):
            true_label = int(test_df.iloc[idx]["label"])
            pred_label = int(pred)
            if true_label == pred_label:
                continue
            rows.append(
                {
                    "model_key": model_key,
                    "true_label": true_label,
                    "pred_label": pred_label,
                    "true_emotion": LABEL_NAMES.get(true_label, str(true_label)),
                    "pred_emotion": LABEL_NAMES.get(pred_label, str(pred_label)),
                    "text": test_df.iloc[idx]["text"],
                    "seg_text": test_df.iloc[idx]["seg_text"],
                    "possible_reason": "",
                    "need_dict_or_sample_update": "",
                }
            )
    error_df = pd.DataFrame(
        rows,
        columns=[
            "model_key",
            "true_label",
            "pred_label",
            "true_emotion",
            "pred_emotion",
            "text",
            "seg_text",
            "possible_reason",
            "need_dict_or_sample_update",
        ],
    )
    ERROR_CASES_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    error_df.to_csv(ERROR_CASES_CSV_PATH, index=False, encoding="utf-8-sig")
    try:
        error_df.to_excel(ERROR_CASES_XLSX_PATH, index=False, engine="openpyxl")
    except Exception:
        pass
    return error_df


def evaluate_all() -> Dict[str, object]:
    vectorizer = joblib.load(VECTORIZER_PATH)
    test_df = pd.read_csv(TEST_SEGMENTED_PATH).dropna(subset=["seg_text", "label"]).copy()
    y_test = test_df["label"].astype(int).tolist()
    x_test = vectorizer.transform(test_df["seg_text"].fillna("").astype(str).tolist())

    compare_rows = []
    predictions = {}
    log = {
        "stage": "test_set_evaluation",
        "test_csv": str(TEST_SEGMENTED_PATH),
        "vectorizer_path": str(VECTORIZER_PATH),
        "x_test_shape": list(x_test.shape),
        "models": {},
    }

    for model_key, (model_name, model_path, confusion_path) in MODEL_SPECS.items():
        model = joblib.load(model_path)
        metrics = evaluate_classifier(model, x_test, y_test)
        y_pred = metrics.pop("y_pred")
        predictions[model_key] = y_pred
        confusion_image = plot_confusion_matrix_figure(y_test, y_pred, confusion_path)

        report = metrics.pop("report")
        row = {
            "model_key": model_key,
            "model_name": model_name,
            "feature_config": "TF-IDF unigram+bigram",
            "test_samples": len(y_test),
            "feature_count": x_test.shape[1],
            "model_preference_rank": MODEL_PREFERENCE_RANK[model_key],
            **metrics,
            "model_path": str(model_path),
            "confusion_matrix_path": confusion_image,
        }
        compare_rows.append(row)
        log["models"][model_key] = {
            **row,
            "classification_report": report,
        }

    compare_df = pd.DataFrame(compare_rows).sort_values(
        by=["macro_f1", "weighted_f1", "accuracy", "model_preference_rank"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    compare_df["rank"] = compare_df.index + 1
    TEST_MODEL_COMPARE_PATH.parent.mkdir(parents=True, exist_ok=True)
    compare_df.to_csv(TEST_MODEL_COMPARE_PATH, index=False, encoding="utf-8-sig")
    compare_df.to_csv(MODEL_COMPARE_PATH, index=False, encoding="utf-8-sig")
    plot_f1_bar(compare_df)

    error_df = _save_error_cases(test_df, predictions)
    log["test_model_compare_path"] = str(TEST_MODEL_COMPARE_PATH)
    log["model_compare_path"] = str(MODEL_COMPARE_PATH)
    log["f1_bar_path"] = str(F1_BAR_PATH)
    log["error_cases_csv_path"] = str(ERROR_CASES_CSV_PATH)
    log["error_case_count"] = int(error_df.shape[0])
    EVALUATION_LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "compare": compare_df,
        "error_cases": error_df,
        "evaluation_log_path": str(EVALUATION_LOG_PATH),
    }


def main() -> None:
    result = evaluate_all()
    print(result["compare"].to_string(index=False))
    print(f"error_cases={len(result['error_cases'])}")
    print(f"evaluation_log_path={result['evaluation_log_path']}")


if __name__ == "__main__":
    main()
