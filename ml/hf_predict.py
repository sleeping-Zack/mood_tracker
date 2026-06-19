import sys
from pathlib import Path


_CLASSIFIER = None
_INIT_ERROR = None


def _get_classifier(model_name: str = "uer/roberta-base-finetuned-jd-binary-chinese"):
    global _CLASSIFIER, _INIT_ERROR
    if _CLASSIFIER is not None or _INIT_ERROR is not None:
        return _CLASSIFIER

    try:
        from transformers import pipeline
    except Exception as exc:
        _INIT_ERROR = exc
        return None

    try:
        _CLASSIFIER = pipeline(
            "text-classification",
            model=model_name,
            tokenizer=model_name,
            model_kwargs={"local_files_only": True},
            tokenizer_kwargs={"local_files_only": True},
        )
    except Exception:
        try:
            _CLASSIFIER = pipeline(
                "text-classification",
                model=model_name,
                tokenizer=model_name,
            )
        except Exception as exc:
            _INIT_ERROR = exc
    return _CLASSIFIER


def map_hf_label(raw_label: str) -> int:
    label = str(raw_label).upper()
    if "POS" in label or label in {"LABEL_1", "1"}:
        return 1
    if "NEG" in label or label in {"LABEL_0", "0"}:
        return 0
    return 1 if "1" in label else 0


def hf_predict(text: str, model_name: str = "uer/roberta-base-finetuned-jd-binary-chinese") -> dict:
    classifier = _get_classifier(model_name=model_name)
    if classifier is None:
        return {
            "available": False,
            "label": None,
            "emotion": "不可用",
            "raw_label": None,
            "score": None,
            "error": str(_INIT_ERROR),
        }

    result = classifier(text)[0]
    raw_label = result["label"]
    mapped = map_hf_label(raw_label)
    return {
        "available": True,
        "label": mapped,
        "emotion": "积极" if mapped == 1 else "消极",
        "raw_label": raw_label,
        "score": float(result["score"]),
        "error": None,
    }


def main() -> None:
    text = "今天答辩很顺利，我很开心。"
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    print(hf_predict(text))


if __name__ == "__main__":
    main()
