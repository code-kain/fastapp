# 학습 카테고리
class LearningCategory:
    SIGN = "학습 > 수어"
    MORSE = "수신호 > 모스부호"
    BRAILLE = "수신호 > 점자"


# 카테고리 색상
CATEGORY_COLOR = {
    LearningCategory.SIGN: "#4359FC",
    LearningCategory.MORSE: "#38C172",
    LearningCategory.BRAILLE: "#FF4D4F",
}


# 카테고리 이름 화면 표시용
def normalize_category(category: str) -> str:
    if not category:
        return LearningCategory.SIGN

    category_text = category.strip()

    if category_text in ["SIGN", "sign", "수어", "학습 > 수어"]:
        return LearningCategory.SIGN

    if category_text in ["MORSE", "morse", "모스부호", "수신호 > 모스부호"]:
        return LearningCategory.MORSE

    if category_text in ["BRAILLE", "braille", "점자", "수신호 > 점자"]:
        return LearningCategory.BRAILLE

    return category_text


# 카테고리 색상 조회
def get_category_color(category: str) -> str:
    normalized_category = normalize_category(category)
    return CATEGORY_COLOR.get(normalized_category, "#4359FC")