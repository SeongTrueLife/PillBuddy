import io
from PIL import Image
from ultralytics import YOLO

class PillPredictorYolo:
    """
    YOLO로 알약을 탐지하고 다른 YOLO 모델로 분류하는 예측기 클래스
    """
    def __init__(self, detector_model_path, classifier_model_path):
        """
        서버 시작 시 두 개의 YOLO 모델을 초기화합니다.
        """
        print("YOLO 기반 예측기 초기화 중...")
        # 1. YOLO 탐지 모델 로드
        self.detector_model = YOLO(detector_model_path)
        
        # 2. YOLO 분류 모델 로드
        self.classifier_model = YOLO(classifier_model_path)
        
        print(f"탐지 모델 ({detector_model_path}) 로드 완료.")
        print(f"분류 모델 ({classifier_model_path}) 로드 완료.")

    def predict(self, image_bytes: bytes) -> list:
        """
        API로부터 받은 이미지 바이트(bytes)를 처리하여 예측 결과를 반환합니다.
        
        :param image_bytes: 프론트엔드에서 전송된 원본 이미지 바이트
        :return: 탐지 및 분류 결과가 담긴 리스트 (예: [{'pill_type': '...', 'confidence': '...'}])
        """
        try:
            # 1. 바이트를 PIL 이미지로 변환
            original_image = Image.open(io.BytesIO(image_bytes))

            # 2. YOLO로 알약 탐지 (최대 1개)
            detection_results = self.detector_model(original_image, max_det=1)
            
            pill_results = []
            
            # 3. 탐지된 알약 영역 처리
            if not detection_results[0].boxes:
                print("알약을 탐지하지 못했습니다.")
                return []

            for box in detection_results[0].boxes:
                coords = box.xyxy[0].tolist() # [x1, y1, x2, y2]
                
                # 4. PIL 이미지에서 해당 영역 자르기
                cropped_pill = original_image.crop(coords)
                print(f"알약 탐지됨. 좌표: {coords}")

                # 5. YOLO 분류 모델로 분류
                classification_results = self.classifier_model(cropped_pill)

                # 6. 가장 확률이 높은 예측 결과 저장
                result = classification_results[0]
                probs = result.probs
                top1_index = probs.top1
                # 분류 모델의 클래스 이름 맵에서 이름 가져오기
                top1_class = self.classifier_model.names[top1_index] 
                top1_conf = probs.top1conf.item()
                
                result_info = {
                    "box_coords": coords,
                    "pill_type": top1_class,
                    "confidence": f"{top1_conf * 100:.2f}%"
                }
                pill_results.append(result_info)

            return pill_results

        except Exception as e:
            print(f"예측 중 오류 발생: {e}")
            return []