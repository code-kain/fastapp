import tensorflow as tf
import tf2onnx
import numpy as np

MODEL_PATH = r"C:\back_0900_lgh\project\fastapp\resource\sign_model.keras"
ONNX_PATH = r"C:\back_0900_lgh\project\fastapp\resource\sign_model.onnx"

model = tf.keras.models.load_model(MODEL_PATH)

# saved_model 형식으로 먼저 저장
SAVED_MODEL_PATH = r"C:\back_0900_lgh\project\fastapp\resource\sign_saved_model"
model.export(SAVED_MODEL_PATH)

# saved_model → onnx 변환
import subprocess
subprocess.run([
    "python", "-m", "tf2onnx.convert",
    "--saved-model", SAVED_MODEL_PATH,
    "--output", ONNX_PATH,
    "--opset", "13"
])

print(f"변환 완료: {ONNX_PATH}")