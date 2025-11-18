import io
import os
from dataclasses import dataclass
from typing import List, Optional

from PIL import Image
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DETECTOR_MODEL_PATH = os.path.join(MODEL_DIR, "best_detector_v1.pt")
CLASSIFIER_MODEL_PATH = os.path.join(MODEL_DIR, "best_classification.pt")


@dataclass
class PillResult:
    pill_type: str
    confidence: float


class PillPredictorYolo:
    def __init__(self, detector_model_path: str, classifier_model_path: str):
        print("[vision_service] YOLO 기반 예측기 초기화 중...")
        self.detector_model = YOLO(detector_model_path)
        self.classifier_model = YOLO(classifier_model_path)
        print(f"[vision_service] 탐지 모델 로드 완료: {detector_model_path}")
        print(f"[vision_service] 분류 모델 로드 완료: {classifier_model_path}")

    def predict(self, image_bytes: bytes) -> List[PillResult]:
        try:
            original_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            print(f"[vision_service] 이미지 로딩 실패: {exc}")
            return []

        try:
            detection_results = self.detector_model(original_image, max_det=1)
        except Exception as exc:
            print(f"[vision_service] 탐지 모델 예측 실패: {exc}")
            return []

        results: List[PillResult] = []
        first_result = detection_results[0]
        if not first_result.boxes:
            print("[vision_service] 알약을 탐지하지 못했습니다.")
            return results

        for box in first_result.boxes:
            coords = [int(coord) for coord in box.xyxy[0].tolist()]
            cropped = original_image.crop(coords)

            try:
                classification_results = self.classifier_model(cropped)
            except Exception as exc:
                print(f"[vision_service] 분류 모델 예측 실패: {exc}")
                continue

            probs = classification_results[0].probs
            top1_index = probs.top1
            top1_conf = float(probs.top1conf)
            pill_type = self.classifier_model.names.get(top1_index, "UNKNOWN")
            results.append(PillResult(pill_type=pill_type, confidence=top1_conf))

        return results


_predictor: Optional[PillPredictorYolo] = None


def _get_predictor() -> PillPredictorYolo:
    global _predictor
    if _predictor is None:
        if not os.path.exists(DETECTOR_MODEL_PATH):
            raise FileNotFoundError(f"Detector model not found: {DETECTOR_MODEL_PATH}")
        if not os.path.exists(CLASSIFIER_MODEL_PATH):
            raise FileNotFoundError(f"Classifier model not found: {CLASSIFIER_MODEL_PATH}")
        _predictor = PillPredictorYolo(DETECTOR_MODEL_PATH, CLASSIFIER_MODEL_PATH)
    return _predictor


def identify_pill(image_bytes: bytes) -> Optional[str]:
    try:
        predictor = _get_predictor()
        predictions = predictor.predict(image_bytes)
        if not predictions:
            return None
        best = max(predictions, key=lambda item: item.confidence)
        return best.pill_type
    except Exception as exc:
        print(f"[vision_service] identify_pill 실패: {exc}")
        return None

