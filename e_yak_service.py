# e_yak_service.py

import requests
import json
import config # 1. '금고'를 수입(import)한다!

# --- (열쇠를 '금고'에서 꺼내 쓰도록 수정!) ---
E_YAK_API_KEY = config.E_YAK_API_KEY # 2. '금고'에서 꺼내 씀

API_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"


# --- 이게 '메인 공장(app.py)'이 호출할 '부품' 함수 ---
def get_drug_info(item_name):
    """
    'e약은요' API를 호출해서 약물 정보를 '조회'하고,
    'Plan A' 또는 'Plan B'를 결정해서 결과를 반환합니다.
    """
    
    # API에 보낼 '요청 파라미터' (Request Parameter)
    params = {
        'ServiceKey': E_YAK_API_KEY,
        'itemName': item_name,         # (app.py가 넘겨준 '약 이름')
        'type': 'json'                   # (응답 형식을 JSON으로!)
    }
    
    print(f"[부품 1호] 'e약은요' API에 '{item_name}' 재고 확인 요청...")
    
    try:
        # 'requests' 라이브러리를 사용해 API에 GET 요청 전송
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status() # 오류가 났으면 여기서 멈춤
        
        # API가 돌려준 응답(JSON)을 Python 딕셔너리로 변환
        data = response.json()
        
        # --- (여기가 'Plan A / Plan B' 로직!) ---
        # 1. 'body'가 있고, 'totalCount'가 0보다 큰지 확인 (성공!)
        if 'body' in data and data['body'].get('totalCount', 0) > 0:
            print(f"[부품 1호] Plan A: '{item_name}' 재고 찾음! (JSON 덩어리 납품)")
            # 'JSON 덩어리' (items 리스트 전체)를 통째로 '납품'
            return data['body']['items'] #
        
        # 2. 'totalCount'가 0이면? (실패!)
        else:
            print(f"[부품 1호] Plan B: '{item_name}' 재고 없음! ('None' 납품)")
            return None # '재고 없음' (None)을 '납품'

    except requests.exceptions.RequestException as req_err:
        print(f"[부품 1호 / 오류!] API 요청 실패: {req_err}")
        return None # 오류가 나도 '재고 없음'으로 처리
    except json.JSONDecodeError:
        print(f"[부품 1호 / 오류!] API 응답이 JSON이 아님 (키가 틀렸을 수도?)")
        print(f"받은 원본 내용: {response.text}")
        return None
    except Exception as e:
        print(f"[부품 1호 / 알 수 없는 오류!] {e}")
        return None

# --- (이 파일 자체를 테스트하기 위한 '시동 장치') ---
# (이 부분은 '메인 공장(app.py)'에 '납품'할 땐 안 쓰여)
if __name__ == "__main__":
    
    print("--- [부품 1호 공장] 자체 테스트 시작 ---")
    
    # (테스트 1: Plan A - 재고가 있는 약)
    print("\n[테스트 1: '타이레놀정500밀리그람' (Plan A)]")
    plan_a_data = get_drug_info("타이레놀정500밀리그람") # (네가 매핑한 '풀네임')
    if plan_a_data:
        # JSON 덩어리를 예쁘게 찍어보자
        print(json.dumps(plan_a_data, indent=2, ensure_ascii=False))

    # (테스트 2: Plan B - 재고가 없는 약)
    print("\n[테스트 2: '가짜약123' (Plan B)]")
    plan_b_data = get_drug_info("가짜약123")
    if plan_b_data is None:
        print("✅ 'None' (재고 없음)이 정확히 반환되었습니다.")
    
    print("\n--- [부품 1호 공장] 자체 테스트 종료 ---")