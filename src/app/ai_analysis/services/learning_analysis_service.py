from collections import defaultdict
from typing import Dict, List

from app.ai_analysis.enums.learning_category import (
    LearningCategory,
    get_category_color,
    normalize_category,
)
from app.ai_analysis.schemas.learning_analysis_schema import (
    AnalysisReportSchema,
    IndividualAnalysisSchema,
    LearningAnalysisRequestSchema,
    LearningAnalysisResponseSchema,
    LearningResultItemSchema,
    OverallAnalysisSchema,
)
from app.ai_analysis.utils.learning_analysis_utils import (
    calculate_rate,
    convert_answers_to_marks,
    format_exp,
    format_streak_days,
    format_study_time,
    get_grade,
    get_overall_description,
    get_overall_guide,
    get_report_message,
    is_danger_rate,
)


# 학습 분석 전체 실행
def analyze_learning_results(
    request: LearningAnalysisRequestSchema,
) -> LearningAnalysisResponseSchema:
    report = create_analysis_report(request)
    overall_analysis_list = create_overall_analysis_list(request.results)
    individual_analysis_list = create_individual_analysis_list(request.results)

    return LearningAnalysisResponseSchema(
        report=report,
        overallAnalysisList=overall_analysis_list,
        individualAnalysisList=individual_analysis_list,
    )


# 종합 리포트 생성
def create_analysis_report(
    request: LearningAnalysisRequestSchema,
) -> AnalysisReportSchema:
    total_correct_count = sum(result.correctCount for result in request.results)
    total_question_count = sum(result.totalCount for result in request.results)
    total_study_minutes = sum(result.studyTimeMinutes for result in request.results)

    total_rate = calculate_rate(total_correct_count, total_question_count)

    return AnalysisReportSchema(
        totalRate=total_rate,
        grade=get_grade(total_rate),
        message=get_report_message(total_rate),
        averageRate=f"{total_rate}%",
        solvedCount=f"{total_correct_count} / {total_question_count}",
        studyTime=format_study_time(total_study_minutes),
        streakDays=format_streak_days(request.streakDays),
        exp=format_exp(request.exp),
    )


# 전체 분석 목록 생성
def create_overall_analysis_list(
    results: List[LearningResultItemSchema],
) -> List[OverallAnalysisSchema]:
    overall_analysis_list = []

    overall_analysis_list.append(create_total_overall_analysis(results))

    category_group = group_results_by_category(results)

    ordered_categories = [
        LearningCategory.SIGN,
        LearningCategory.MORSE,
        LearningCategory.BRAILLE,
    ]

    for category in ordered_categories:
        category_results = category_group.get(category, [])

        if not category_results:
            continue

        category_rate = calculate_category_rate(category_results)

        overall_analysis_list.append(
            OverallAnalysisSchema(
                title=category,
                rate=category_rate,
                color=get_category_color(category),
                description=get_category_description(category, category_rate),
                guide=get_category_guide(category, category_rate),
                danger=is_danger_rate(category_rate),
            )
        )

    return overall_analysis_list


# 전체 분석 결과 생성
def create_total_overall_analysis(
    results: List[LearningResultItemSchema],
) -> OverallAnalysisSchema:
    total_correct_count = sum(result.correctCount for result in results)
    total_question_count = sum(result.totalCount for result in results)
    total_rate = calculate_rate(total_correct_count, total_question_count)

    return OverallAnalysisSchema(
        title="전체 분석 결과",
        rate=total_rate,
        color="#4359FC",
        description=get_overall_description(total_rate),
        guide=get_overall_guide(total_rate),
        danger=is_danger_rate(total_rate),
    )


# 개별 분석 목록 생성
def create_individual_analysis_list(
    results: List[LearningResultItemSchema],
) -> List[IndividualAnalysisSchema]:
    individual_analysis_list = []
    grouped_results = group_results_for_individual_analysis(results)

    for index, grouped_result in enumerate(grouped_results, start=1):
        category = grouped_result["category"]

        rate = calculate_rate(
            grouped_result["correct_count"],
            grouped_result["total_count"],
        )

        individual_analysis_list.append(
            IndividualAnalysisSchema(
                id=index,
                title=grouped_result["title"],
                category=category,
                rate=rate,
                studyTime=format_study_time(
                    grouped_result["study_time_minutes"]
                ),
                questionCount=grouped_result["total_count"],
                color=get_category_color(category),
                answers=grouped_result["answers"],
                guide=get_individual_guide(
                    grouped_result["guide_result"],
                    rate,
                ),
            )
        )

    return individual_analysis_list


# 같은 학습은 최근 결과만 사용
def group_results_for_individual_analysis(
    results: List[LearningResultItemSchema],
):
    grouped_map = {}

    # Spring에서 최근 학습 순서로 전달되므로 첫 번째 결과만 저장
    for result in results:
        category = normalize_category(result.category)
        key = f"{category}:{result.title}"

        if key in grouped_map:
            continue

        grouped_map[key] = {
            "title": result.title,
            "category": category,
            "correct_count": result.correctCount,
            "total_count": result.totalCount,
            "study_time_minutes": result.studyTimeMinutes,
            "answers": convert_answers_to_marks(result.answers),
            "guide_result": result,
        }

    return list(grouped_map.values())


# 카테고리별 묶기
def group_results_by_category(
    results: List[LearningResultItemSchema],
) -> Dict[str, List[LearningResultItemSchema]]:
    category_group = defaultdict(list)

    for result in results:
        category = normalize_category(result.category)
        category_group[category].append(result)

    return category_group


# 카테고리 정답률 계산
def calculate_category_rate(
    results: List[LearningResultItemSchema],
) -> int:
    correct_count = sum(result.correctCount for result in results)
    total_count = sum(result.totalCount for result in results)

    return calculate_rate(correct_count, total_count)


# 카테고리 분석 설명
def get_category_description(category: str, rate: int) -> str:
    if category == LearningCategory.SIGN:
        if rate >= 80:
            return "수어 표현 이해도가 높고 문제 풀이 속도도 좋아요."
        if rate >= 50:
            return "수어 표현은 이해하고 있지만 반복 복습이 필요해요."
        return "수어 기초 표현과 문장 이해를 다시 학습할 필요가 있어요."

    if category == LearningCategory.MORSE:
        if rate >= 80:
            return "모스부호 기호 암기와 해석 능력이 좋아요."
        if rate >= 50:
            return "기호 암기와 해석 능력이 꾸준히 향상되고 있어요."
        return "모스부호 기초 규칙과 신호 구분 연습이 필요해요."

    if category == LearningCategory.BRAILLE:
        if rate >= 80:
            return "점자 규칙 이해와 패턴 인식이 안정적이에요."
        if rate >= 50:
            return "점자 규칙은 이해하고 있지만 오답 패턴이 남아있어요."
        return "점자 규칙 이해와 패턴 인식이 부족해요."

    return get_overall_description(rate)


# 카테고리 추천 문구
def get_category_guide(category: str, rate: int) -> str:
    if category == LearningCategory.SIGN:
        if rate >= 80:
            return "고난도 문장 표현을 추가로 학습해보세요."
        if rate >= 50:
            return "자주 틀린 표현을 중심으로 다시 복습해보세요."
        return "기초 수어 표현부터 다시 학습하는 것을 추천해요."

    if category == LearningCategory.MORSE:
        if rate >= 80:
            return "긴 신호 조합 문제로 응용력을 높여보세요."
        if rate >= 50:
            return "복습을 통해 오답 패턴을 줄여보세요."
        return "짧은 신호와 긴 신호를 구분하는 연습부터 시작해보세요."

    if category == LearningCategory.BRAILLE:
        if rate >= 80:
            return "단어 단위 점자 읽기 속도를 높여보세요."
        if rate >= 50:
            return "오답이 많은 점자 패턴을 반복해서 익혀보세요."
        return "기초부터 차근차근 복습하고 반복 연습을 추천해요."

    return get_overall_guide(rate)


# 개별 추천 문구
def get_individual_guide(
    result: LearningResultItemSchema,
    rate: int,
) -> str:
    category = normalize_category(result.category)

    if rate >= 85:
        return (
            f"{result.title} 학습 성취도가 높아요. "
            "다음 단계 학습으로 넘어가도 좋아요."
        )

    if rate >= 70:
        return (
            f"{result.title} 이해도는 안정적이에요. "
            "틀린 문제만 다시 확인해보세요."
        )

    if rate >= 50:
        return (
            f"{result.title}에서 오답이 반복되고 있어요. "
            "관련 개념을 다시 복습해보세요."
        )

    if category == LearningCategory.SIGN:
        return (
            "수어 표현 이해가 부족해요. "
            "기초 표현과 예문을 다시 학습해보세요."
        )

    if category == LearningCategory.MORSE:
        return (
            "모스부호 신호 구분에서 오답이 많아요. "
            "짧은 신호와 긴 신호를 반복 연습하세요."
        )

    if category == LearningCategory.BRAILLE:
        return (
            "점자 영역 규칙과 반복 패턴에서 오답이 많아요. "
            "기초 규칙을 다시 학습하고 유사 패턴을 반복 연습하세요."
        )

    return "기초 개념을 다시 학습하고 오답 문제를 반복해서 풀어보세요."