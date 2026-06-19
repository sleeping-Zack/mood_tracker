import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

try:
    from ml.config import (
        ALL_LABELS,
        LABEL_DISTRIBUTION_CSV_PATH,
        LABEL_DISTRIBUTION_PATH,
        LABEL_NAMES,
        LABELED_DATA_PATH,
        RANDOM_STATE,
        TEST_DATA_PATH,
        TRAIN_DATA_PATH,
        VALID_DATA_PATH,
    )
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import (
        ALL_LABELS,
        LABEL_DISTRIBUTION_CSV_PATH,
        LABEL_DISTRIBUTION_PATH,
        LABEL_NAMES,
        LABELED_DATA_PATH,
        RANDOM_STATE,
        TEST_DATA_PATH,
        TRAIN_DATA_PATH,
        VALID_DATA_PATH,
    )


_PLOT_COLORS = ["#4c78a8", "#f58518", "#e45756", "#54a24b", "#b279a2"]

_LABEL_EN = {
    0: "sad",
    1: "anxious",
    2: "angry",
    3: "calm",
    4: "happy",
}


def split_dataset(input_path: str, train_path: str, valid_path: str, test_path: str):
    df = pd.read_csv(input_path).dropna(subset=["text", "label"]).drop_duplicates(subset=["text"])
    df["label"] = df["label"].astype(int)

    train_df, temp_df = train_test_split(
        df,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=df["label"],
    )
    valid_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        random_state=RANDOM_STATE,
        stratify=temp_df["label"],
    )

    train_df = train_df.copy()
    valid_df = valid_df.copy()
    test_df = test_df.copy()
    train_df["split"] = "train"
    valid_df["split"] = "valid"
    test_df["split"] = "test"

    train_df.to_csv(train_path, index=False, encoding="utf-8-sig")
    valid_df.to_csv(valid_path, index=False, encoding="utf-8-sig")
    test_df.to_csv(test_path, index=False, encoding="utf-8-sig")

    combined_df = pd.concat([train_df, valid_df, test_df], ignore_index=True)
    combined_df.to_csv(input_path, index=False, encoding="utf-8-sig")

    return {
        "train": train_df.shape[0],
        "valid": valid_df.shape[0],
        "test": test_df.shape[0],
    }


def save_label_distribution(input_path: str, csv_path: str, figure_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    distribution = (
        df.groupby(["split", "label"])
        .size()
        .reset_index(name="count")
        .sort_values(["split", "label"])
    )
    distribution.to_csv(csv_path, index=False, encoding="utf-8-sig")

    pivot = distribution.pivot(index="split", columns="label", values="count").fillna(0)
    pivot = pivot.reindex(["train", "valid", "test"])

    columns_order = [label for label in ALL_LABELS if label in pivot.columns]
    if columns_order:
        pivot = pivot[columns_order]
    colors = _PLOT_COLORS[: len(pivot.columns)]
    legend_labels = [f"{int(label)} {_LABEL_EN.get(int(label), str(label))}" for label in pivot.columns]

    ax = pivot.plot(kind="bar", figsize=(8, 4.5), color=colors)
    ax.set_xlabel("split")
    ax.set_ylabel("count")
    ax.set_title("Label distribution by split (5-class)")
    ax.legend(legend_labels, title="label", loc="best")
    ax.figure.tight_layout()
    ax.figure.savefig(figure_path, dpi=200)
    plt.close(ax.figure)
    return distribution


def main() -> None:
    sizes = split_dataset(
        str(LABELED_DATA_PATH),
        str(TRAIN_DATA_PATH),
        str(VALID_DATA_PATH),
        str(TEST_DATA_PATH),
    )
    distribution = save_label_distribution(
        str(LABELED_DATA_PATH),
        str(LABEL_DISTRIBUTION_CSV_PATH),
        str(LABEL_DISTRIBUTION_PATH),
    )
    print(f"sizes={sizes}")
    print(distribution.to_string(index=False))
    print(f"figure_path={LABEL_DISTRIBUTION_PATH}")


if __name__ == "__main__":
    main()
