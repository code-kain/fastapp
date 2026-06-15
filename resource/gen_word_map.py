import json

with open('selected_500.json', 'r', encoding='utf-8') as f:
    selected = json.load(f)

mapping = {}
for word_code, word_name in selected.items():
    num = word_code.replace('WORD', '').zfill(4)
    folder = f'NIA_SL_WORD{num}_REAL01_D'
    mapping[word_name] = folder

lines = ['# 텍스트 → word_folder 매핑\n']
lines.append('TEXT_TO_FOLDER = {\n')
for word_name, folder in mapping.items():
    lines.append(f'    \"{word_name}\": \"{folder}\",\n')
lines.append('}\n\n')
lines.append('def get_folder_by_text(text: str) -> str | None:\n')
lines.append('    return TEXT_TO_FOLDER.get(text.strip())\n')

with open('../src/app/service/word_map.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'완료! {len(mapping)}개 단어 매핑 생성')
