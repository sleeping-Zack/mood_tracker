import json
import platform
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Tuple

import joblib
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

try:
    from ml.config import (
        BEST_MODEL_INFO_PATH,
        LR_MODEL_PATH,
        MODEL_COMPARE_PATH,
        NB_MODEL_PATH,
        RANDOM_STATE,
        SVM_MODEL_PATH,
        TRAIN_LOG_PATH,
        TRAIN_SEGMENTED_PATH,
        VALID_SEGMENTED_PATH,
        VECTORIZER_PATH,
    )
    from ml.feature_engineering import build_vectorizer
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import (
        BEST_MODEL_INFO_PATH,
        LR_MODEL_PATH,
        MODEL_COMPARE_PATH,
        NB_MODEL_PATH,
        RANDOM_STATE,
        SVM_MODEL_PATH,
        TRAIN_LOG_PATH,
        TRAIN_SEGMENTED_PATH,
        VALID_SEGMENTED_PATH,
        VECTORIZER_PATH,
    )
    from ml.feature_engineering import build_vectorizer


def train_nb(x_train, y_train) -> MultinomialNB:
    model = MultinomialNB(alpha=1.0)
    model.fit(x_train, y_train)
    return model


def train_lr(x_train, y_train) -> LogisticRegression:
    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    model.fit(x_train, y_train)
    return model


def train_svm(x_train, y_train) -> LinearSVC:
    model = LinearSVC(
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    model.fit(x_train, y_train)
    return model


def evaluate_on_valid(model, x_valid, y_valid) -> Dict[str, float]:
    started = time.perf_counter()
    y_pred = model.predict(x_valid)
    predict_seconds = time.perf_counter() - started
    sample_count = len(y_valid)
    return {
        "accuracy": round(accuracy_score(y_valid, y_pred), 6),
        "macro_f1": round(f1_score(y_valid, y_pred, average="macro", zero_division=0), 6),
        "weighted_f1": round(f1_score(y_valid, y_pred, average="weighted", zero_division=0), 6),
        "macro_precision": round(precision_score(y_valid, y_pred, average="macro", zero_division=0), 6),
        "macro_recall": round(recall_score(y_valid, y_pred, average="macro", zero_division=0), 6),
        "predict_ms_per_sample": round((predict_seconds / sample_count) * 1000, 6) if sample_count else 0,
    }


def _load_segmented_data(train_csv: Path, valid_csv: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    train_df = pd.read_csv(train_csv).dropna(subset=["seg_text", "label"])
    valid_df = pd.read_csv(valid_csv).dropna(subset=["seg_text", "label"])
    train_df["label"] = train_df["label"].astype(int)
    valid_df["label"] = valid_df["label"].astype(int)
    return train_df, valid_df


def train_all(
    train_csv: Path = TRAIN_SEGMENTED_PATH,
    valid_csv: Path = VALID_SEGMENTED_PATH,
    vectorizer_path: Path = VECTORIZER_PATH,
    model_paths: Dict[str, Path] = None,
) -> Dict[str, object]:
    if model_paths is None:
        model_paths = {
            "nb": NB_MODEL_PATH,
            "lr": LR_MODEL_PATH,
            "svm": SVM_MODEL_PATH,
        }

    train_df, valid_df = _load_segmented_data(Path(train_csv), Path(valid_csv))
    x_train_text = train_df["seg_text"].fillna("").astype(str).tolist()
    y_train = train_df["label"].astype(int).tolist()
    x_valid_text = valid_df["seg_text"].fillna("").astype(str).tolist()
    y_valid = valid_df["label"].astype(int).tolist()

    vectorizer = build_vectorizer(max_features=8000, ngram_range=(1, 2), min_df=3, max_df=0.9)
    x_train = vectorizer.fit_transform(x_train_text)
    x_valid = vectorizer.transform(x_valid_text)

    Path(vectorizer_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, vectorizer_path)

    trainers: Dict[str, Tuple[str, Callable]] = {
        "nb": ("MultinomialNB", train_nb),
        "lr": ("LogisticRegression", train_lr),
        "svm": ("LinearSVC", train_svm),
    }
    preference_rank = {
        "lr": 1,
        "svm": 2,
        "nb": 3,
    }

    compare_rows = []
    train_log_models = {}
    for model_key, (model_name, trainer) in trainers.items():
        started = time.perf_counter()
        model = trainer(x_train, y_train)
        train_seconds = round(time.perf_counter() - started, 6)

        model_path = Path(model_paths[model_key])
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)

        metrics = evaluate_on_valid(model, x_valid, y_valid)
        row = {
            "model_key": model_key,
            "model_name": model_name,
            "feature_config": "TF-IDF unigram+bigram",
            "train_samples": x_train.shape[0],
            "valid_samples": x_valid.shape[0],
            "feature_count": x_train.shape[1],
            "train_seconds": train_seconds,
            "model_preference_rank": preference_rank[model_key],
            **metrics,
            "model_path": str(model_path),
        }
        compare_rows.append(row)
        train_log_models[model_key] = row

    compare_df = pd.DataFrame(compare_rows)
    compare_df = compare_df.sort_values(
        by=["macro_f1", "weighted_f1", "accuracy", "model_preference_rank", "train_seconds"],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)
    compare_df["rank"] = compare_df.index + 1
    compare_df.to_csv(MODEL_COMPARE_PATH, index=False, encoding="utf-8-sig")

    # Best-model selection with a small tolerance band:
    # If two models' validation macro_f1 differ by less than ~1 sample worth
    # (~1/|valid|), treat them as tied and prefer LR > SVM > NB. This stops
    # MultinomialNB from "winning" by 0.001 of pure sampling noise on the
    # validation set, which we observed causes the served model to flip
    # between NB and LR/SVM on otherwise identical data.
    tie_tolerance = 0.005
    top_macro_f1 = float(compare_df["macro_f1"].max())
    near_top = compare_df[compare_df["macro_f1"] >= top_macro_f1 - tie_tolerance]
    best_row = (
        near_top.sort_values(
            by=["model_preference_rank", "weighted_f1", "accuracy"],
            ascending=[True, False, False],
        )
        .iloc[0]
        .to_dict()
    )
    best_model_info = {
        "best_model_key": best_row["model_key"],
        "best_model_name": best_row["model_name"],
        "selection_metric": (
            "validation macro_f1 with ±{tol} tolerance; "
            "ties broken by preference LR > SVM > NB, then weighted_f1, accuracy"
        ).format(tol=tie_tolerance),
        "tie_tolerance": tie_tolerance,
        "top_macro_f1": top_macro_f1,
        "model_path": best_row["model_path"],
        "vectorizer_path": str(vectorizer_path),
    }
    BEST_MODEL_INFO_PATH.write_text(
        json.dumps(best_model_info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    train_log = {
        "stage": "supervised_model_training",
        "python_version": platform.python_version(),
        "sklearn_version": sklearn.__version__,
        "train_csv": str(train_csv),
        "valid_csv": str(valid_csv),
        "vectorizer_path": str(vectorizer_path),
        "vectorizer_params": {
            "max_features": 8000,
            "ngram_range": [1, 2],
            "min_df": 3,
            "max_df": 0.9,
        },
        "x_train_shape": list(x_train.shape),
        "x_valid_shape": list(x_valid.shape),
        "models": train_log_models,
        "best_model": best_model_info,
    }
    TRAIN_LOG_PATH.write_text(json.dumps(train_log, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "compare": compare_df,
        "best_model": best_model_info,
        "train_log_path": str(TRAIN_LOG_PATH),
        "model_compare_path": str(MODEL_COMPARE_PATH),
    }


def main() -> None:
    result = train_all()
    print(result["compare"].to_string(index=False))
    print(f"best_model={result['best_model']}")
    print(f"train_log_path={result['train_log_path']}")
    print(f"model_compare_path={result['model_compare_path']}")


if __name__ == "__main__":
    main()
