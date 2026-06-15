import numpy as np
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

# ── 데이터 로드 ──────────────────────────────────────────
X = np.load('train_data/X.npy')
y = np.load('train_data/y.npy')
with open('train_data/label_map.json', 'r', encoding='utf-8') as f:
    label_map = json.load(f)

num_classes = len(label_map)
print(f'X: {X.shape}, 클래스 수: {num_classes}')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'사용 디바이스: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"})')

# ── 데이터 분할 ──────────────────────────────────────────
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = torch.FloatTensor(X_train).to(device)
y_train = torch.LongTensor(y_train).to(device)
X_val   = torch.FloatTensor(X_val).to(device)
y_val   = torch.LongTensor(y_val).to(device)

train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True)
val_loader   = DataLoader(TensorDataset(X_val,   y_val),   batch_size=32)

# ── 모델 정의 ────────────────────────────────────────────
class SignLSTM(nn.Module):
    def __init__(self, input_dim=225, hidden_dim=128, num_classes=462):
        super().__init__()
        self.lstm1 = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.drop1 = nn.Dropout(0.3)
        self.lstm2 = nn.LSTM(hidden_dim, 64, batch_first=True)
        self.drop2 = nn.Dropout(0.3)
        self.fc1   = nn.Linear(64, 128)
        self.relu  = nn.ReLU()
        self.fc2   = nn.Linear(128, num_classes)

    def forward(self, x):
        x, _ = self.lstm1(x)
        x = self.drop1(x)
        x, _ = self.lstm2(x)
        x = self.drop2(x[:, -1, :])  # 마지막 타임스텝
        x = self.relu(self.fc1(x))
        return self.fc2(x)

model = SignLSTM(num_classes=num_classes).to(device)
print(model)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

# ── 학습 ─────────────────────────────────────────────────
best_val_acc = 0
patience_cnt = 0
PATIENCE = 15

for epoch in range(1, 101):
    # Train
    model.train()
    train_loss, train_correct = 0, 0
    for xb, yb in train_loader:
        optimizer.zero_grad()
        out = model(xb)
        loss = criterion(out, yb)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        train_correct += (out.argmax(1) == yb).sum().item()

    # Validation
    model.eval()
    val_loss, val_correct = 0, 0
    with torch.no_grad():
        for xb, yb in val_loader:
            out = model(xb)
            val_loss += criterion(out, yb).item()
            val_correct += (out.argmax(1) == yb).sum().item()

    train_acc = train_correct / len(X_train)
    val_acc   = val_correct   / len(X_val)
    scheduler.step(val_loss)

    print(f'Epoch {epoch:3d} | train_loss: {train_loss/len(train_loader):.4f} | train_acc: {train_acc:.4f} | val_acc: {val_acc:.4f}')

    # Early stopping & 체크포인트
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        patience_cnt = 0
        torch.save(model.state_dict(), 'train_data/best_model.pt')
        print(f'  ✓ 최고 val_acc 갱신: {best_val_acc:.4f} → 저장')
    else:
        patience_cnt += 1
        if patience_cnt >= PATIENCE:
            print(f'Early stopping (patience={PATIENCE})')
            break

# ── ONNX 변환 ────────────────────────────────────────────
print('\nONNX 변환 중...')
model.load_state_dict(torch.load('train_data/best_model.pt'))
model.eval().cpu()

dummy = torch.randn(1, 30, 225)
torch.onnx.export(
    model, dummy, 'sign_model.onnx',
    input_names=['input'], output_names=['output'],
    dynamic_axes={'input': {0: 'batch'}, 'output': {0: 'batch'}},
    opset_version=11
)
print('완료! sign_model.onnx 저장됨')
print(f'최종 최고 val_acc: {best_val_acc:.4f}')