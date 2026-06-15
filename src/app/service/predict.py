import onnxruntime as ort
import numpy as np
import json
import os

# 현재 파일 기준 경로 계산
# predict.py 위치: src/app/service/predict.py
# resource 위치:   resource/
# → 3단계 위로 올라가서 resource 폴더 찾기
BASE_DIR = os.path.dirname(  # fastapp/
    os.path.dirname(         # fastapp/src/
        os.path.dirname(     # fastapp/src/app/
            os.path.dirname(os.path.abspath(__file__))  # fastapp/src/app/service/
        )
    )
)
RESOURCE_DIR = os.path.join(BASE_DIR, "resource")

MODEL_PATH = os.path.join(RESOURCE_DIR, "sign_model.onnx")
LABEL_MAP_PATH = os.path.join(RESOURCE_DIR, "label_map.json")

# 모델 로드
session = ort.InferenceSession(MODEL_PATH)

# label_map 로드 (반전: 숫자 → 단어)
with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
    label_map = json.load(f)
reverse_label_map = {v: k for k, v in label_map.items()}

SEQ_LEN = 30

def predict_sign(keypoints: list) -> str:
    data = np.array(keypoints, dtype=np.float32)

    # 차원 맞추기 (225로 패딩)
    TARGET_DIM = 225
    if data.shape[1] < TARGET_DIM:
        pad = np.zeros((data.shape[0], TARGET_DIM - data.shape[1]), dtype=np.float32)
        data = np.hstack([data, pad])
    elif data.shape[1] > TARGET_DIM:
        data = data[:, :TARGET_DIM]

    # 프레임 수 맞추기
    if len(data) >= SEQ_LEN:
        data = data[:SEQ_LEN]
    else:
        pad = np.zeros((SEQ_LEN - len(data), TARGET_DIM), dtype=np.float32)
        data = np.vstack([data, pad])

    data = np.expand_dims(data, axis=0)

    input_name = session.get_inputs()[0].name
    result = session.run(None, {input_name: data})
    pred_idx = int(np.argmax(result[0]))

    return reverse_label_map.get(pred_idx, "알 수 없음")
