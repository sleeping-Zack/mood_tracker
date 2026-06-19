import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, Tuple

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer

try:
    from ml.config import (
        HF_COMPARE_PATH,
        KMEANS_CLUSTER_TERMS_PATH,
        KMEANS_COMPARE_PATH,
        KMEANS_VIS_PATH,
        LATENCY_COMPARE_PATH,
        LR_MODEL_PATH,
        RANDOM_STATE,
        TEST_SEGMENTED_PATH,
        TRAIN_SEGMENTED_PATH,
        VECTORIZER_PATH,
    )
    from ml.hf_predict import hf_predict
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import (
        HF_COMPARE_PATH,
        KMEANS_CLUSTER_TERMS_PATH,
        KMEANS_COMPARE_PATH,
        KMEANS_VIS_PATH,
        LATENCY_COMPARE_PATH,
        LR_MODEL_PATH,
        RANDOM_STATE,
        TEST_SEGMENTED_PATH,
        TRAIN_SEGMENTED_PATH,
        VECTORIZER_PATH,
    )
    from ml.hf_predict import hf_predict


def run_kmeans_on_tfidf(x, n_clusters: int = 2, random_state: int = RANDOM_STATE):
    model = KMeans(n_clusters=n_clusters, n_init=10, random_state=random_state)
    labels = model.fit_predict(x)
    return model, labels


def run_lsa_kmeans(x, n_clusters: int = 2, n_components: int = 2, random_state: int = RANDOM_STATE):
    max_components = max(1, min(n_components, x.shape[0] - 1, x.shape[1] - 1))
    lsa = make_pipeline(
        TruncatedSVD(n_components=max_components, random_state=random_state),
        Normalizer(copy=False),
    )
    x_lsa = lsa.fit_transform(x)
    model = KMeans(n_clusters=n_clusters, n_init=10, random_state=random_state)
    labels = model.fit_predict(x_lsa)
    return lsa, model, labels, x_lsa


def _map_clusters_to_labels(cluster_labels: Iterable[int], y_true: Iterable[int]) -> Dict[int, int]:
    buckets = defaultdict(list)
    for cluster_id, true_label in zip(cluster_labels, y_true):
        buckets[int(cluster_id)].append(int(true_label))
    mapping = {}
    for cluster_id, labels in buckets.items():
        counts = Counter(labels)
        mapping[cluster_id] = counts.most_common(1)[0][0]
    return mapping


def _evaluate_cluster_labels(name: str, cluster_labels, y_true) -> Dict[str, object]:
    mapping = _map_clusters_to_labels(cluster_labels, y_true)
    y_pred = [mapping[int(cluster_id)] for cluster_id in cluster_labels]
    return {
        "experiment": name,
        "cluster_to_label": json.dumps(mapping, ensure_ascii=False),
        "accuracy_after_mapping": round(accuracy_score(y_true, y_pred), 6),
        "macro_f1_after_mapping": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 6),
    }


def _top_terms_for_clusters(model: KMeans, vectorizer, top_n: int = 12) -> pd.DataFrame:
    terms = vectorizer.get_feature_names_out()
    rows = []
    for cluster_id, center in enumerate(model.cluster_centers_):
        top_indices = center.argsort()[::-1][:top_n]
        rows.append(
            {
                "experiment": "tfidf_kmeans",
                "cluster": cluster_id,
                "top_terms": " ".join(terms[index] for index in top_indices),
            }
        )
    return pd.DataFrame(rows)


def run_hf_compare(limit: int = 50) -> pd.DataFrame:
    test_df = pd.read_csv(TEST_SEGMENTED_PATH).dropna(subset=["text", "label"]).copy().head(limit)
    rows = []
    started = time.perf_counter()
    first = hf_predict(str(test_df.iloc[0]["text"])) if not test_df.empty else {"available": False}
    if not first.get("available"):
        rows.append(
            {
                "method": "huggingface_local_cache",
                "status": "skipped",
                "samples": int(test_df.shape[0]),
                "accuracy": None,
                "happy_f1": None,
                "macro_f1": None,
                "avg_ms_per_sample": None,
                "depends_on_network": "no during script run; requires local model cache",
                "error": first.get("error"),
            }
        )
        result_df = pd.DataFrame(rows)
        result_df.to_csv(HF_COMPARE_PATH, index=False, encoding="utf-8-sig")
        return result_df

    predictions = [first]
    for text in test_df["text"].astype(str).tolist()[1:]:
        predictions.append(hf_predict(text))

    elapsed = time.perf_counter() - started
    y_true = test_df["label"].astype(int).tolist()
    y_pred = [int(item["label"]) for item in predictions]
    rows.append(
        {
            "method": "huggingface_local_cache",
            "status": "ok",
            "samples": len(y_true),
            "accuracy": round(accuracy_score(y_true, y_pred), 6),
            "happy_f1": round(f1_score(y_true, y_pred, pos_label=4, zero_division=0), 6),
            "macro_f1": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 6),
            "avg_ms_per_sample": round((elapsed / len(y_true)) * 1000, 6) if y_true else 0,
            "depends_on_network": "no during script run; requires local model cache",
            "error": None,
        }
    )
    result_df = pd.DataFrame(rows)
    result_df.to_csv(HF_COMPARE_PATH, index=False, encoding="utf-8-sig")
    return result_df


def run_latency_compare(local_model_key: str = "lr") -> pd.DataFrame:
    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(LR_MODEL_PATH)
    test_df = pd.read_csv(TEST_SEGMENTED_PATH).dropna(subset=["seg_text", "label"]).copy()
    x_test = vectorizer.transform(test_df["seg_text"].fillna("").astype(str).tolist())
    started = time.perf_counter()
    model.predict(x_test)
    elapsed = time.perf_counter() - started
    rows = [
        {
            "method": f"local_{local_model_key}",
            "samples": int(test_df.shape[0]),
            "avg_ms_per_sample": round((elapsed / test_df.shape[0]) * 1000, 6) if test_df.shape[0] else 0,
            "depends_on_network": "no",
        }
    ]
    if HF_COMPARE_PATH.exists():
        hf_df = pd.read_csv(HF_COMPARE_PATH)
        if not hf_df.empty:
            rows.append(
                {
                    "method": "huggingface_local_cache",
                    "samples": int(hf_df.iloc[0].get("samples", 0) or 0),
                    "avg_ms_per_sample": hf_df.iloc[0].get("avg_ms_per_sample"),
                    "depends_on_network": hf_df.iloc[0].get("depends_on_network"),
                }
            )
    latency_df = pd.DataFrame(rows)
    latency_df.to_csv(LATENCY_COMPARE_PATH, index=False, encoding="utf-8-sig")
    return latency_df


def run_kmeans_experiments() -> Dict[str, object]:
    vectorizer = joblib.load(VECTORIZER_PATH)
    train_df = pd.read_csv(TRAIN_SEGMENTED_PATH).dropna(subset=["seg_text", "label"]).copy()
    x_train = vectorizer.transform(train_df["seg_text"].fillna("").astype(str).tolist())
    y_train = train_df["label"].astype(int).tolist()

    tfidf_model, tfidf_clusters = run_kmeans_on_tfidf(x_train)
    lsa, lsa_model, lsa_clusters, x_lsa = run_lsa_kmeans(x_train)

    compare_rows = [
        _evaluate_cluster_labels("tfidf_kmeans", tfidf_clusters, y_train),
        _evaluate_cluster_labels("lsa_kmeans", lsa_clusters, y_train),
    ]
    compare_df = pd.DataFrame(compare_rows)
    compare_df.to_csv(KMEANS_COMPARE_PATH, index=False, encoding="utf-8-sig")

    terms_df = _top_terms_for_clusters(tfidf_model, vectorizer)
    terms_df.to_csv(KMEANS_CLUSTER_TERMS_PATH, index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(6, 5))
    scatter = ax.scatter(x_lsa[:, 0], x_lsa[:, 1], c=lsa_clusters, cmap="Set1", alpha=0.8)
    ax.set_title("LSA + KMeans clusters")
    ax.set_xlabel("LSA component 1")
    ax.set_ylabel("LSA component 2")
    ax.legend(*scatter.legend_elements(), title="cluster")
    fig.tight_layout()
    fig.savefig(KMEANS_VIS_PATH, dpi=200)
    plt.close(fig)

    return {
        "compare": compare_df,
        "cluster_terms": terms_df,
        "kmeans_vis_path": str(KMEANS_VIS_PATH),
    }


def run_stage6() -> Dict[str, object]:
    hf_compare = run_hf_compare()
    latency_compare = run_latency_compare()
    kmeans_result = run_kmeans_experiments()
    return {
        "hf_compare": hf_compare,
        "latency_compare": latency_compare,
        **kmeans_result,
    }


def main() -> None:
    result = run_stage6()
    print("HF compare:")
    print(result["hf_compare"].to_string(index=False))
    print("Latency compare:")
    print(result["latency_compare"].to_string(index=False))
    print("KMeans compare:")
    print(result["compare"].to_string(index=False))
    print("Cluster terms:")
    print(result["cluster_terms"].to_string(index=False))
    print(f"kmeans_vis_path={result['kmeans_vis_path']}")


if __name__ == "__main__":
    main()
