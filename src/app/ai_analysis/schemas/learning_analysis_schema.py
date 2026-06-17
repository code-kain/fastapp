from typing import List

from pydantic import BaseModel, Field


# 학습 문제 정답 정보
class LearningAnswerSchema(BaseModel):
    questionNumber: int
    isCorrect: bool


# Spring 요청 학습 결과
class LearningResultItemSchema(BaseModel):
    id: int
    title: str
    category: str
    correctCount: int
    totalCount: int
    studyTimeMinutes: int
    answers: List[LearningAnswerSchema] = Field(default_factory=list)


# FastAPI 분석 요청
class LearningAnalysisRequestSchema(BaseModel):
    userId: int
    streakDays: int = 0
    exp: int = 0
    results: List[LearningResultItemSchema]


# 종합 리포트 응답
class AnalysisReportSchema(BaseModel):
    totalRate: int
    grade: str
    message: str
    averageRate: str
    solvedCount: str
    studyTime: str
    streakDays: str
    exp: str


# 전체 분석 응답
class OverallAnalysisSchema(BaseModel):
    title: str
    rate: int
    color: str
    description: str
    guide: str
    danger: bool = False


# 개별 분석 응답
class IndividualAnalysisSchema(BaseModel):
    id: int
    title: str
    category: str
    rate: int
    studyTime: str
    questionCount: int
    color: str
    answers: List[str]
    guide: str


# React 화면 응답 형태
class LearningAnalysisResponseSchema(BaseModel):
    report: AnalysisReportSchema
    overallAnalysisList: List[OverallAnalysisSchema]
    individualAnalysisList: List[IndividualAnalysisSchema]