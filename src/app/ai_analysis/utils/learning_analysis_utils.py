from typing import List


# 정답률 계산
def calculate_rate(correct_count: int, total_count: int) -> int:
    if total_count <= 0:
        return 0

    return round((correct_count / total_count) * 100)


# 학습 시간 표시
def format_study_time(total_minutes: int) -> str:
    if total_minutes <= 0:
        return "0분"

    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours == 0:
        return f"{minutes}분"

    if minutes == 0:
        return f"{hours}시간"

    return f"{hours}시간 {minutes}분"


# 연속 학습 일수 표시
def format_streak_days(streak_days: int) -> str:
    if streak_days <= 0:
        return "0일"

    return f"{streak_days}일"


# 경험치 표시
def format_exp(exp: int) -> str:
    if exp <= 0:
        return "0EXP"

    return f"{exp}EXP"


# 종합 등급 계산
def get_grade(total_rate: int) -> str:
    if total_rate >= 90:
        return "최상위 학습자"

    if total_rate >= 75:
        return "성장세 우수"

    if total_rate >= 60:
        return "안정형"

    if total_rate >= 40:
        return "성장 중"

    return "도약 필요"


# 종합 리포트 문구
def get_report_message(total_rate: int) -> str:
    if total_rate >= 85:
        return "높은 정답률을 유지하고 있어요!"

    if total_rate >= 70:
        return "꾸준한 학습으로 좋은 성과를 내고 있어요!"

    if total_rate >= 50:
        return "부족한 영역을 보완하면 더 좋아질 수 있어요."

    return "기초부터 다시 학습하며 실력을 다져보세요."


# 전체 분석 설명
def get_overall_description(rate: int) -> str:
    if rate >= 85:
        return "전반적으로 높은 학습 성취도를 보여주고 있어요."

    if rate >= 70:
        return "전반적으로 안정적인 학습 수준을 보여주고 있어요."

    if rate >= 50:
        return "일부 영역에서 보완이 필요한 학습 수준이에요."

    return "기초 개념과 반복 학습이 필요한 상태예요."


# 전체 분석 추천 문구
def get_overall_guide(rate: int) -> str:
    if rate >= 85:
        return "현재 학습 흐름을 유지하면서 고난도 문제에 도전해보세요."

    if rate >= 70:
        return "꾸준한 복습과 약점 보완으로 다음 단계 실력을 만들어가요!"

    if rate >= 50:
        return "오답이 반복되는 영역을 중심으로 복습해보세요."

    return "쉬운 문제부터 다시 풀면서 기본 규칙을 먼저 익혀보세요."


# 정답 여부 O/X 변환
def convert_answers_to_marks(answer_list) -> List[str]:
    if not answer_list:
        return []

    marks = []

    for answer in answer_list:
        marks.append("O" if answer.isCorrect else "X")

    return marks


# 위험 점수 여부
def is_danger_rate(rate: int) -> bool:
    return rate < 50