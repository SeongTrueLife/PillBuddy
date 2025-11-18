import io
from PIL import Image
from ultralytics import YOLO
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

class PillPredictorAzure:
    """
    YOLO로 알약을 탐지하고 Azure Custom Vision으로 분류하는 예측기 클래스
    """
    def __init__(self, yolo_model_path, prediction_key, endpoint, project_id, model_name):
        """
        서버 시작 시 모델과 클라이언트를 초기화합니다.
        """
        print("Azure 기반 예측기 초기화 중...")
        # 1. YOLO 탐지 모델 로드
        self.yolo_model = YOLO(yolo_model_path)
        
        # 2. Azure Custom Vision 예측 클라이언트 인증
        credentials = ApiKeyCredentials(in_headers={"Prediction-Key": prediction_key})
        self.predictor = CustomVisionPredictionClient(endpoint, credentials)
        
        # 3. Azure 프로젝트 정보 저장
        self.project_id = project_id
        self.model_name = model_name
        
        print(f"YOLO 모델 ({yolo_model_path}) 로드 완료.")
        print(f"Azure 클라이언트 ({endpoint}) 초기화 완료.")

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
            results = self.yolo_model(original_image, max_det=1)
            
            pill_results = []

            # 3. 탐지된 알약 영역 처리
            if not results[0].boxes:
                print("알약을 탐지하지 못했습니다.")
                return []
                
            for box in results[0].boxes:
                coords = box.xyxy[0].tolist() # [x1, y1, x2, y2]
                
                # 4. PIL 이미지에서 해당 영역 자르기
                cropped_pill = original_image.crop(coords)
                print(f"알약 탐지됨. 좌표: {coords}")

                # 5. Custom Vision 분류를 위해 크롭된 이미지를 바이트로 변환
                with io.BytesIO() as output:
                    cropped_pill.save(output, format="JPEG")
                    cropped_image_bytes = output.getvalue()

                # 6. Azure API 호출
                cv_results = self.predictor.classify_image(
                    self.project_id,
                    self.model_name,
                    cropped_image_bytes
                )

                # 7. 가장 확률이 높은 예측 결과 저장
                top_prediction = cv_results.predictions[0]
                result_info = {
                    "box_coords": coords,
                    "pill_type": top_prediction.tag_name,
                    "confidence": f"{top_prediction.probability * 100:.2f}%"
                }
                pill_results.append(result_info)
            
            return pill_results

        except Exception as e:
            print(f"예측 중 오류 발생: {e}")
            return []