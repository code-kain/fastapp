from fastapi import APIRouter
from app.service.extract_keypoints import extract_keypoints_from_json
from app.service.predict import predict_sign
from app.service.word_map import get_folder_by_text

router = APIRouter(prefix="/sign", tags=["sign"])

@router.get("/predict")
async def predict(word_folder: str):
    keypoints = extract_keypoints_from_json(word_folder)
    if not keypoints:
        return {"error": "데이터를 읽을 수 없어요"}
    word = predict_sign(keypoints)
    return {"word": word}

@router.get("/translate")
async def translate(text: str):
    folder = get_folder_by_text(text)
    if not folder:
        return {"error": f"'{text}' 에 해당하는 수어 데이터가 없어요"}
    keypoints = extract_keypoints_from_json(text)  # 폴더명 대신 단어명으로!
    if not keypoints:
        return {"error": "데이터를 읽을 수 없어요"}
    return {
        "input": text,
        "folder": folder,
        "keypoints": keypoints
    }