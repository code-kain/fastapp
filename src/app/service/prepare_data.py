import os
import numpy as np
from extract_keypoints import extract_keypoints

DATA_PATH = r"C:\back_0900_lgh\project\fastapp\resource\signhand_sample\original_data\REAL\WORD\01"
SAVE_PATH = r"C:\back_0900_lgh\project\fastapp\resource\keypoints"

os.makedirs(SAVE_PATH, exist_ok=True)

word_map = {
    "1501": "word_1501",
    "1502": "word_1502",
    "1503": "word_1503",
    "1504": "word_1504",
    "1505": "word_1505",
}

for filename in os.listdir(DATA_PATH):
    if not filename.endswith(".mp4"):
        continue

    parts = filename.split("_")
    word_num = parts[2].replace("WORD", "")

    if word_num not in word_map:
        continue

    word = word_map[word_num]
    video_path = os.path.join(DATA_PATH, filename)

    print(f"처리 중: {filename}")
    keypoints = extract_keypoints(video_path)

    if keypoints:
        save_file = os.path.join(SAVE_PATH, f"{word}_{filename.replace('.mp4', '')}.npy")
        np.save(save_file, np.array(keypoints))
        print(f"저장 완료: {save_file}")

print("전체 완료!")