import numpy as np
import os

CACHE_DIR = r"C:\back_0900_lgh\project\fastapp\resource\cached_keypoints"

def extract_keypoints_from_json(word_name: str) -> list:
    npy_path = os.path.join(CACHE_DIR, f"{word_name}.npy")
    if not os.path.exists(npy_path):
        return []
    data = np.load(npy_path)
    return data.tolist()