import logging
import re
import sys
import unicodedata
from pathlib import Path
from typing import Optional, Union

import jieba
import pandas as pd

try:
    from ml.config import (
        SEGMENT_PREVIEW_PATH,
        STOPWORDS_PATH,
        TEST_DATA_PATH,
        TEST_SEGMENTED_PATH,
        TRAIN_DATA_PATH,
        TRAIN_SEGMENTED_PATH,
        USER_DICT_PATH,
        VALID_DATA_PATH,
        VALID_SEGMENTED_PATH,
    )
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import (
        SEGMENT_PREVIEW_PATH,
        STOPWORDS_PATH,
        TEST_DATA_PATH,
        TEST_SEGMENTED_PATH,
        TRAIN_DATA_PATH,
        TRAIN_SEGMENTED_PATH,
        USER_DICT_PATH,
        VALID_DATA_PATH,
        VALID_SEGMENTED_PATH,
    )


jieba.setLogLevel(logging.WARNING)
_USER_DICT_LOADED = False


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text)).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\u4e00-\u9fff，。！？、；：“”‘’（）《》【】…—-]", "", text)
    return text.strip()


def load_stopwords(path: Union[str, Path] = STOPWORDS_PATH) -> set[str]:
    path = Path(path)
    if not path.exists():
        return set()
    words = {
        line.strip()
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    return words


def load_user_dict(user_dict_path: Optional[Union[str, Path]] = USER_DICT_PATH) -> None:
    global _USER_DICT_LOADED
    if _USER_DICT_LOADED or not user_dict_path:
        return

    path = Path(user_dict_path)
    if path.exists():
        jieba.load_userdict(str(path))
    _USER_DICT_LOADED = True


def segment_text(
    text: str,
    stopwords: Optional[set[str]] = None,
    use_user_dict: bool = True,
) -> str:
    if use_user_dict:
        load_user_dict()

    text = clean_text(text)
    tokens = jieba.lcut(text, cut_all=False)
    if stopwords:
        tokens = [word for word in tokens if word.strip() and word not in stopwords]
    else:
        tokens = [word for word in tokens if word.strip()]
    return " ".join(tokens)


def preprocess_dataset(input_path: Union[str, Path], output_path: Union[str, Path]) -> pd.DataFrame:
    stopwords = load_stopwords()
    df = pd.read_csv(input_path)
    df = df.dropna(subset=["text", "label"]).copy()
    df["clean_text"] = df["text"].map(clean_text)
    df["seg_text"] = df["clean_text"].map(lambda text: segment_text(text, stopwords=stopwords))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df


def preprocess_all() -> dict[str, int]:
    outputs = {
        "train": preprocess_dataset(TRAIN_DATA_PATH, TRAIN_SEGMENTED_PATH),
        "valid": preprocess_dataset(VALID_DATA_PATH, VALID_SEGMENTED_PATH),
        "test": preprocess_dataset(TEST_DATA_PATH, TEST_SEGMENTED_PATH),
    }

    preview = outputs["train"][["text", "clean_text", "seg_text", "label"]].head(12)
    SEGMENT_PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    preview.to_csv(SEGMENT_PREVIEW_PATH, index=False, encoding="utf-8-sig")
    return {split: len(df) for split, df in outputs.items()}


def main() -> None:
    sizes = preprocess_all()
    print(f"sizes={sizes}")
    print(f"train_segmented={TRAIN_SEGMENTED_PATH}")
    print(f"valid_segmented={VALID_SEGMENTED_PATH}")
    print(f"test_segmented={TEST_SEGMENTED_PATH}")
    print(f"segment_preview={SEGMENT_PREVIEW_PATH}")


if __name__ == "__main__":
    main()
