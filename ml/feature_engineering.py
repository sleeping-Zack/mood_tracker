import json
import sys
from pathlib import Path
from typing import Tuple, Union

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from ml.config import (
        TEST_SEGMENTED_PATH,
        TRAIN_SEGMENTED_PATH,
        VALID_SEGMENTED_PATH,
        VECTORIZER_PATH,
        VOCAB_STATS_PATH,
    )
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import (
        TEST_SEGMENTED_PATH,
        TRAIN_SEGMENTED_PATH,
        VALID_SEGMENTED_PATH,
        VECTORIZER_PATH,
        VOCAB_STATS_PATH,
    )


def build_vectorizer(
    max_features: int = 8000,
    ngram_range: Tuple[int, int] = (1, 2),
    min_df: Union[int, float] = 3,
    max_df: Union[int, float] = 0.9,
) -> TfidfVectorizer:
    return TfidfVectorizer(
        tokenizer=str.split,
        preprocessor=None,
        token_pattern=None,
        lowercase=False,
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
    )


def _matrix_stats(matrix) -> tuple[int, int, float]:
    rows, cols = matrix.shape
    total = rows * cols
    density = matrix.nnz / total if total else 0
    sparsity = 1 - density
    return matrix.nnz, total, round(sparsity, 6)


def evaluate_vectorizer_config(
    name: str,
    train_texts: list[str],
    valid_texts: list[str],
    test_texts: list[str],
    ngram_range: Tuple[int, int],
    max_features: int = 8000,
    min_df: Union[int, float] = 2,
    max_df: Union[int, float] = 0.9,
) -> Tuple[TfidfVectorizer, dict[str, object]]:
    vectorizer = build_vectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
    )
    x_train = vectorizer.fit_transform(train_texts)
    x_valid = vectorizer.transform(valid_texts)
    x_test = vectorizer.transform(test_texts)

    train_nnz, train_total, train_sparsity = _matrix_stats(x_train)
    valid_nnz, valid_total, valid_sparsity = _matrix_stats(x_valid)
    test_nnz, test_total, test_sparsity = _matrix_stats(x_test)

    stats = {
        "config_name": name,
        "ngram_range": json.dumps(list(ngram_range)),
        "max_features": max_features,
        "min_df": min_df,
        "max_df": max_df,
        "vocab_size": len(vectorizer.vocabulary_),
        "train_rows": x_train.shape[0],
        "train_features": x_train.shape[1],
        "train_non_zero": train_nnz,
        "train_total_values": train_total,
        "train_sparsity": train_sparsity,
        "valid_non_zero": valid_nnz,
        "valid_sparsity": valid_sparsity,
        "test_non_zero": test_nnz,
        "test_sparsity": test_sparsity,
    }
    return vectorizer, stats


def fit_feature_configs(
    train_csv: Union[str, Path] = TRAIN_SEGMENTED_PATH,
    valid_csv: Union[str, Path] = VALID_SEGMENTED_PATH,
    test_csv: Union[str, Path] = TEST_SEGMENTED_PATH,
    vectorizer_path: Union[str, Path] = VECTORIZER_PATH,
    vocab_stats_path: Union[str, Path] = VOCAB_STATS_PATH,
) -> pd.DataFrame:
    train_df = pd.read_csv(train_csv)
    valid_df = pd.read_csv(valid_csv)
    test_df = pd.read_csv(test_csv)

    train_texts = train_df["seg_text"].fillna("").astype(str).tolist()
    valid_texts = valid_df["seg_text"].fillna("").astype(str).tolist()
    test_texts = test_df["seg_text"].fillna("").astype(str).tolist()

    configs = [
        ("tfidf_unigram", (1, 1)),
        ("tfidf_unigram_bigram", (1, 2)),
    ]

    rows = []
    selected_vectorizer = None
    for name, ngram_range in configs:
        vectorizer, stats = evaluate_vectorizer_config(
            name=name,
            train_texts=train_texts,
            valid_texts=valid_texts,
            test_texts=test_texts,
            ngram_range=ngram_range,
        )
        rows.append(stats)
        if name == "tfidf_unigram_bigram":
            selected_vectorizer = vectorizer

    vectorizer_path = Path(vectorizer_path)
    vectorizer_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_vectorizer, vectorizer_path)

    vocab_stats = pd.DataFrame(rows)
    vocab_stats_path = Path(vocab_stats_path)
    vocab_stats_path.parent.mkdir(parents=True, exist_ok=True)
    vocab_stats.to_csv(vocab_stats_path, index=False, encoding="utf-8-sig")
    return vocab_stats


def main() -> None:
    stats = fit_feature_configs()
    print(stats.to_string(index=False))
    print(f"vectorizer_path={VECTORIZER_PATH}")
    print(f"vocab_stats_path={VOCAB_STATS_PATH}")


if __name__ == "__main__":
    main()
