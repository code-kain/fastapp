from fastapi import APIRouter

from app.ai_analysis.schemas.learning_analysis_schema import (
    LearningAnalysisRequestSchema,
    LearningAnalysisResponseSchema,
)
from app.ai_analysis.services.learning_analysis_service import analyze_learning_results


router = APIRouter(prefix="/ai/learning-analysis", tags=["AI 학습분석"])


# 학습 분석 리포트 생성
@router.post(
    "/report",
    response_model=LearningAnalysisResponseSchema,
    summary="학습 분석 리포트 생성",
)
async def create_learning_analysis_report(
    request: LearningAnalysisRequestSchema,
):
    return analyze_learning_results(request)