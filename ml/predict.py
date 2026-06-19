import json
import logging
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Optional, Tuple

try:
    from ml.config import (
        ALL_LABELS,
        BEST_MODEL_INFO_PATH,
        EMOTION_MESSAGES,
        LABEL_KEYS,
        LABEL_NAMES,
        LR_MODEL_PATH,
        STOPWORDS_PATH,
        TREND_SCORE,
        USER_DICT_PATH,
        VECTORIZER_PATH,
    )
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from ml.config import (
        ALL_LABELS,
        BEST_MODEL_INFO_PATH,
        EMOTION_MESSAGES,
        LABEL_KEYS,
        LABEL_NAMES,
        LR_MODEL_PATH,
        STOPWORDS_PATH,
        TREND_SCORE,
        USER_DICT_PATH,
        VECTORIZER_PATH,
    )


_VECTORIZER = None
_MODEL = None
_MODEL_NAME = ""
_LOAD_ERROR = None
_USER_DICT_LOADED = False
_LOADED_VECTORIZER_MTIME = 0.0
_LOADED_MODEL_MTIME = 0.0


def _read_best_model_info() -> Tuple[Path, str]:
    if BEST_MODEL_INFO_PATH.exists():
        try:
            info = json.loads(BEST_MODEL_INFO_PATH.read_text(encoding="utf-8"))
            model_path = Path(info.get("model_path") or LR_MODEL_PATH)
            model_name = info.get("best_model_name") or model_path.stem
            return model_path, model_name
        except Exception:
            pass
    return LR_MODEL_PATH, "LogisticRegression"


def _safe_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def load_artifacts(
    vectorizer_path: Path = VECTORIZER_PATH,
    model_path: Optional[Path] = None,
):
    """Lazy-load TF-IDF vectorizer + best model, with disk-mtime-driven refresh.

    Behaviour:
    - First call performs the full joblib.load of vectorizer + model.
    - Subsequent calls compare the on-disk mtime of vectorizer / model against
      the snapshot we cached. If either file has been overwritten (e.g. after
      `python ml/train_model.py` finishes), we re-load both atomically.
    - This way `runserver` does not need to be restarted after retraining.
    """
    global _VECTORIZER, _MODEL, _MODEL_NAME, _LOAD_ERROR
    global _LOADED_VECTORIZER_MTIME, _LOADED_MODEL_MTIME

    if model_path is None:
        resolved_model_path, model_name = _read_best_model_info()
    else:
        resolved_model_path = Path(model_path)
        model_name = resolved_model_path.stem

    vectorizer_mtime = _safe_mtime(Path(vectorizer_path))
    model_mtime = _safe_mtime(resolved_model_path)

    cache_valid = (
        _VECTORIZER is not None
        and _MODEL is not None
        and vectorizer_mtime
        and model_mtime
        and vectorizer_mtime == _LOADED_VECTORIZER_MTIME
        and model_mtime == _LOADED_MODEL_MTIME
    )
    if cache_valid:
        return _VECTORIZER, _MODEL, _MODEL_NAME

    try:
        import joblib

        new_vectorizer = joblib.load(vectorizer_path)
        new_model = joblib.load(resolved_model_path)
    except Exception as exc:
        if _VECTORIZER is None or _MODEL is None:
            _LOAD_ERROR = exc
            return None, None, ""
        # Reload failed but we still have a working cached pair: keep serving
        # with the previous artifacts instead of degrading the live page.
        return _VECTORIZER, _MODEL, _MODEL_NAME

    _VECTORIZER = new_vectorizer
    _MODEL = new_model
    _MODEL_NAME = model_name
    _LOADED_VECTORIZER_MTIME = vectorizer_mtime
    _LOADED_MODEL_MTIME = model_mtime
    _LOAD_ERROR = None
    return _VECTORIZER, _MODEL, _MODEL_NAME


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text)).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\u4e00-\u9fff，。！？、；：“”‘’（）《》【】…—-]", "", text)
    return text.strip()


def load_stopwords(path: Path = STOPWORDS_PATH) -> set:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def segment_for_prediction(text: str) -> str:
    global _USER_DICT_LOADED
    import jieba

    jieba.setLogLevel(logging.WARNING)
    if not _USER_DICT_LOADED and USER_DICT_PATH.exists():
        jieba.load_userdict(str(USER_DICT_PATH))
        _USER_DICT_LOADED = True

    stopwords = load_stopwords()
    tokens = jieba.lcut(clean_text(text), cut_all=False)
    tokens = [word for word in tokens if word.strip() and word not in stopwords]
    return " ".join(tokens)


def _confidence(model, x_vector, pred: int) -> Optional[float]:
    classes = list(getattr(model, "classes_", []))
    if hasattr(model, "predict_proba"):
        try:
            probabilities = model.predict_proba(x_vector)[0]
            if pred in classes:
                return round(float(probabilities[classes.index(pred)]), 6)
            return round(float(max(probabilities)), 6)
        except Exception:
            pass
    if hasattr(model, "decision_function"):
        try:
            decision = model.decision_function(x_vector)
            scores = decision[0] if hasattr(decision, "shape") and len(decision.shape) > 1 else decision
            try:
                length = len(scores)
            except TypeError:
                return round(float(abs(scores)), 6)
            if length == 0:
                return None
            if pred in classes:
                return round(float(scores[classes.index(pred)]), 6)
            return round(float(max(scores)), 6)
        except Exception:
            return None
    return None


def _unknown_result(message: str) -> dict:
    return {
        "label": None,
        "sentiment": "unknown",
        "emotion_key": "unknown",
        "emotion": "未知",
        "score": 0,
        "message": message,
        "model_name": "local-model-unavailable",
        "confidence": None,
        "seg_text": "",
        "predict_ms": None,
        "error": str(_LOAD_ERROR) if _LOAD_ERROR else None,
    }


def predict_emotion(text: str) -> dict:
    if not text or not str(text).strip():
        return _unknown_result("输入为空，无法分析。")

    started = time.perf_counter()
    vectorizer, model, model_name = load_artifacts()
    if vectorizer is None or model is None:
        return _unknown_result("本地模型文件或依赖暂不可用，请先确认已安装 requirements.txt 并完成训练。")

    try:
        seg_text = segment_for_prediction(text)
        x_vector = vectorizer.transform([seg_text])
        pred = int(model.predict(x_vector)[0])
        confidence = _confidence(model, x_vector, pred)
    except Exception as exc:
        return {
            **_unknown_result("本地模型预测失败，请检查分词、向量器与模型版本是否一致。"),
            "error": str(exc),
        }

    predict_ms = round((time.perf_counter() - started) * 1000, 6)
    if pred not in ALL_LABELS:
        return _unknown_result(f"模型返回了未知标签：{pred}。")

    return {
        "label": pred,
        "sentiment": LABEL_KEYS[pred],
        "emotion_key": LABEL_KEYS[pred],
        "emotion": LABEL_NAMES[pred],
        "score": TREND_SCORE[pred],
        "message": EMOTION_MESSAGES[pred],
        "model_name": f"TF-IDF + {model_name}",
        "confidence": confidence,
        "seg_text": seg_text,
        "predict_ms": predict_ms,
        "error": None,
    }


if __name__ == "__main__":
    sample = "今天答辩非常顺利，我很开心。"
    if len(sys.argv) > 1:
        sample = " ".join(sys.argv[1:])
    print(json.dumps(predict_emotion(sample), ensure_ascii=False, indent=2))
