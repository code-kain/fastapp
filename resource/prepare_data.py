import json, os, glob
import numpy as np

KEYPOINT_DIR = "004.수어영상/1.Training/라벨링데이터/REAL/WORD/keypoint_data/01"
SELECTED_FILE = "selected_500.json"
OUTPUT_DIR = "train_data"
SEQ_LEN = 30
TARGET_DIM = 225

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(SELECTED_FILE, 'r', encoding='utf-8') as f:
    selected = json.load(f)

# 단어 → 인덱스 매핑
word_list = sorted(set(selected.values()))
word_to_idx = {w: i for i, w in enumerate(word_list)}

print(f"학습할 단어 수: {len(word_list)}")

X, y = [], []

for word_code, word_name in selected.items():
    num = word_code.replace('WORD', '').zfill(4)
    pattern = os.path.join(KEYPOINT_DIR, f"NIA_SL_WORD{num}_REAL*")
    folders = glob.glob(pattern)
    
    if not folders:
        print(f"  없음: {word_code} ({word_name})")
        continue

    count = 0
    for folder in folders:
        json_files = sorted(glob.glob(os.path.join(folder, "*.json")))
        if not json_files:
            continue

        frames = []
        for jf in json_files:
            try:
                with open(jf, 'r') as f:
                    data = json.load(f)
                p = data.get('people', {})
                if not p:
                    continue
                pose = p.get('pose_keypoints_2d', [])
                left = p.get('hand_left_keypoints_2d', [])
                right = p.get('hand_right_keypoints_2d', [])
                row = pose[:50] + left[:75] + right[:75] + p.get('face_keypoints_2d', [])[:25]
                row = row[:TARGET_DIM]
                if len(row) < TARGET_DIM:
                    row += [0] * (TARGET_DIM - len(row))
                frames.append(row)
            except:
                continue

        if len(frames) < 5:
            continue

        # SEQ_LEN 맞추기
        if len(frames) >= SEQ_LEN:
            frames = frames[:SEQ_LEN]
        else:
            frames += [[0]*TARGET_DIM] * (SEQ_LEN - len(frames))

        X.append(frames)
        y.append(word_to_idx[word_name])
        count += 1

    if count > 0:
        print(f"  {word_code} ({word_name}): {count}개 샘플")

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)

np.save(os.path.join(OUTPUT_DIR, 'X.npy'), X)
np.save(os.path.join(OUTPUT_DIR, 'y.npy'), y)

label_map = {w: i for w, i in word_to_idx.items()}
with open(os.path.join(OUTPUT_DIR, 'label_map.json'), 'w', encoding='utf-8') as f:
    json.dump(label_map, f, ensure_ascii=False, indent=2)

print(f"\n완료! X: {X.shape}, y: {y.shape}")
print(f"label_map 저장: {OUTPUT_DIR}/label_map.json")
