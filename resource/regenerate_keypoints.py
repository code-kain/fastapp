import json, os, glob
import numpy as np

# 진짜 keypoint json 루트
KEYPOINT_DIR = r"C:\back_0900_lgh\project\fastapp\resource\004.수어영상\1.Training\라벨링데이터\REAL\WORD\keypoint_data\01"
# 결과 저장 위치 (서빙용)
SAVE_DIR = r"C:\back_0900_lgh\project\fastapp\resource\cached_keypoints"
SEQ_LEN = 30
TARGET_DIM = 225

os.makedirs(SAVE_DIR, exist_ok=True)

# translate.py 에 있던 매핑을 그대로 가져옴 (발표용 단어만 우선)
TEXT_TO_FOLDER = {
    "고민": "NIA_SL_WORD0001_REAL01_D",
    "가수": "NIA_SL_WORD0133_REAL01_D",
    "가다": "NIA_SL_WORD0943_REAL01_D",
    "가능": "NIA_SL_WORD1282_REAL01_D",
    "행복": "NIA_SL_WORD1169_REAL01_D",
    "친구": "NIA_SL_WORD1204_REAL01_D",
    # 발표에 쓸 단어 더 추가하면 됨
}

def load_frames(folder_path):
    """폴더 안 json들을 프레임 순서대로 읽어 [x,y,conf,...] 행 리스트로"""
    json_files = sorted(glob.glob(os.path.join(folder_path, "*.json")))
    frames = []
    for jf in json_files:
        try:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            p = data.get('people', {})
            if not p:
                continue
            pose  = p.get('pose_keypoints_2d', [])
            left  = p.get('hand_left_keypoints_2d', [])
            right = p.get('hand_right_keypoints_2d', [])
            face  = p.get('face_keypoints_2d', [])
            row = pose[:50] + left[:75] + right[:75] + face[:25]
            row = row[:TARGET_DIM]
            if len(row) < TARGET_DIM:
                row += [0] * (TARGET_DIM - len(row))
            frames.append(row)
        except Exception as e:
            continue
    return frames

def pick_active_window(frames, seq_len=SEQ_LEN):
    """손이 가장 많이 움직이는 seq_len 구간을 선택 (기존 frames[:30] 대체)"""
    if len(frames) <= seq_len:
        return frames + [[0]*TARGET_DIM] * (seq_len - len(frames))
    def activity(start):
        win = frames[start:start+seq_len]
        # 오른손목(idx 4) + 왼손목(idx 7) y좌표 변화량 합산
        rwy = [f[4*3+1] for f in win]
        lwy = [f[7*3+1] for f in win]
        rwx = [f[4*3]   for f in win]
        return (max(rwy)-min(rwy)) + (max(lwy)-min(lwy)) + (max(rwx)-min(rwx))
    best = max(range(len(frames)-seq_len+1), key=activity)
    return frames[best:best+seq_len]

# ── 실행 ──
for word, folder in TEXT_TO_FOLDER.items():
    folder_path = os.path.join(KEYPOINT_DIR, folder)
    if not os.path.isdir(folder_path):
        print(f"❌ 폴더 없음: {word} → {folder}")
        continue

    frames = load_frames(folder_path)
    if len(frames) < 5:
        print(f"⚠️  프레임 부족: {word} ({len(frames)}개)")
        continue

    active = pick_active_window(frames)
    arr = np.array(active, dtype=np.float32)

    # 동작 범위 확인용 로그
    wy = [f[4*3+1] for f in active]
    rng = round(max(wy) - min(wy), 1)

    save_path = os.path.join(SAVE_DIR, f"{word}.npy")
    np.save(save_path, arr)
    print(f"✅ {word}: shape={arr.shape}, 손목Y범위={rng} → 저장됨")

print("\n완료!")