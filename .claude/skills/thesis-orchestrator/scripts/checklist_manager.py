#!/usr/bin/env python3
"""Checklist management module for doctoral research workflow.

This module handles the 150-step checklist for tracking research progress,
including parsing, updating, and progress reporting.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from workflow_constants import TOTAL_STEPS, PHASES, get_phase_for_step

# Valid status values
VALID_STATUSES = {"pending", "in_progress", "completed"}


def get_steps_for_phase(phase: str) -> dict[str, int]:
    """Get the step range for a given phase.

    Args:
        phase: Phase name

    Returns:
        Dictionary with 'start' and 'end' step numbers

    Raises:
        ValueError: If phase is not found
    """
    for phase_name, start, end in PHASES:
        if phase_name == phase:
            return {"start": start, "end": end}

    raise ValueError(f"Unknown phase: {phase}")


def create_checklist(output_dir: Path, research_type: str | None = None) -> Path:
    """Create the 150-step todo checklist.

    Args:
        output_dir: Output directory for the checklist
        research_type: Research type determines which agents appear at steps 95-98.
            'philosophical' → philosophical agents; all others → quantitative agents (default).

    Returns:
        Path to the created checklist file
    """
    checklist_path = output_dir / "todo-checklist.md"

    # Research-type-specific agents at steps 95-98.
    # Only one set appears per checklist instance; step numbers stay unique.
    if research_type == "philosophical":
        _steps_95_98 = [
            (95, "[철학적] @philosophical-method-designer", [
                "철학적 방법론 선택 및 정당화",
                "연구질문-방법 매핑",
            ]),
            (96, "[철학적] @source-text-selector", [
                "분석 대상 1차 텍스트/원전 선정",
                "선정 기준 및 포함/배제 근거",
            ]),
            (97, "[철학적] @argument-construction-designer", [
                "논증 구조(전제-결론) 설계",
                "반론/재반론 계획 수립",
            ]),
            (98, "[철학적] @philosophical-analysis-planner", [
                "분석 절차 및 해석 전략 설계",
                "엄밀성 확보 방안 수립",
            ]),
        ]
    else:
        _steps_95_98 = [
            (95, "[양적] @hypothesis-developer", [
                "가설 체계 구조화",
                "귀무가설/대립가설 쌍 작성",
            ]),
            (96, "[양적] @research-model-developer", [
                "조작적 정의 확정",
                "측정 도구 선정",
            ]),
            (97, "[양적] @sampling-designer", [
                "표본추출 방법 결정",
                "표본 크기 파워분석 수행",
            ]),
            (98, "[양적] @statistical-planner", [
                "통계기법 선정 및 가정 검토",
                "분석 절차 코드/프로토콜 설계",
            ]),
        ]

    # Build checklist content
    # Each item: (step, task, [sub_items]) — sub_items rendered as indented checkboxes
    sections = [
        ("Phase 0: 초기화", [
            (1, "세션 초기화", [
                "작업 디렉토리 생성 및 구조 초기화",
                "session.json 생성 및 기본값 설정",
            ]),
            (2, "연구유형 선택", [
                "양적/질적/혼합 연구유형 옵션 제시",
                "사용자 선택 수집 및 저장",
            ]),
            (3, "학문분야 선택", [
                "학문 분류 체계 제시",
                "세부 전공 영역 설정",
            ]),
            (4, "사용자 리소스 확인", [
                "가용 데이터 소스 확인",
                "시간/예산 제약 파악",
            ]),
            (5, "입력 모드 확인", [
                "Mode A~G 옵션 제시",
                "선택된 모드별 분기 경로 설정",
            ]),
            (6, "연구 주제/질문 입력", [
                "사용자 입력 수집",
                "입력 유효성 검증",
            ]),
            (7, "초기 설정 완료", [
                "전체 설정 요약 생성",
                "설정 확인 및 저장",
            ]),
            (8, "HITL-0 체크포인트", [
                "초기 설정 검토 프롬프트 생성",
                "사용자 승인 대기 및 확인",
            ]),
        ]),
        ("Phase 0-A: 주제 탐색 [Mode A Only]", [
            (9, "주제 학술적 맥락 분석", [
                "@topic-explorer 에이전트 호출",
                "관련 학술 분야 매핑",
            ]),
            (10, "연구 트렌드 파악", [
                "최근 5년 연구 동향 스캔",
                "핵심 키워드 클러스터링",
            ]),
            (11, "연구질문 후보 도출", [
                "이론적 갭 기반 질문 생성",
                "실용적 갭 기반 질문 생성",
            ]),
            (12, "학술적 기여 가능성 평가", [
                "신규성/독창성 평가",
                "실현 가능성 평가",
            ]),
            (13, "연구질문 후보 정리", [
                "후보 질문 우선순위 정렬",
                "각 후보별 장단점 요약",
            ]),
            (14, "HITL-1 체크포인트 준비", [
                "후보 질문 프레젠테이션 생성",
                "사용자 의사결정 가이드 준비",
            ]),
        ]),
        ("HITL-1: 연구질문 확정", [
            (15, "연구질문 후보 제시", [
                "구조화된 후보 목록 표시",
                "각 후보별 예상 연구 경로 설명",
            ]),
            (16, "사용자 선택 대기", [
                "사용자 입력 수집 및 확인",
                "선택 결과 session.json 반영",
            ]),
            (17, "문헌검토 깊이 설정", [
                "comprehensive/focused/rapid 옵션 제시",
                "선택에 따른 Wave 설정 조정",
            ]),
            (18, "이론적 프레임워크 옵션 설정", [
                "기존 프레임워크 vs 새 프레임워크 선택",
                "선택 결과 저장 및 Phase 1 준비",
            ]),
        ]),
        ("Phase 1 Wave 1: 기초 문헌 탐색", [
            (19, "@literature-searcher 시작", [
                "에이전트 호출 및 컨텍스트 전달",
                "검색 범위 설정 확인",
            ]),
            (20, "검색 전략 수립", [
                "핵심 개념 분해 및 키워드 도출",
                "Boolean 검색식 구성 (영문/한글)",
                "포함/배제 기준 설정",
            ]),
            (21, "데이터베이스 검색", [
                "Google Scholar 검색",
                "SSRN/JSTOR/PubMed 검색",
                "RISS/KCI 한국 데이터베이스 검색",
            ]),
            (22, "검색 결과 스크리닝", [
                "제목/초록 기반 관련성 평가",
                "포함/배제 기준 적용 및 중복 제거",
                "PRISMA 흐름도 데이터 생성",
            ]),
            (23, "@literature-searcher 완료", [
                "최종 포함 문헌 목록 작성",
                "GroundedClaim 스키마 검증",
            ]),
            (24, "@seminal-works-analyst 시작", [
                "에이전트 호출 및 문헌 목록 전달",
            ]),
            (25, "핵심 문헌 식별", [
                "인용 빈도 기반 핵심 논문 선별",
                "이론적 기초 문헌 분류",
            ]),
            (26, "인용 네트워크 분석", [
                "공인용 패턴 분석",
                "학술적 계보 매핑",
            ]),
            (27, "@seminal-works-analyst 완료", [
                "핵심 문헌 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (28, "@trend-analyst 시작", [
                "에이전트 호출 및 문헌 데이터 전달",
            ]),
            (29, "시계열 동향 분석", [
                "연도별 연구 발표 추이 분석",
                "주요 전환점 식별",
            ]),
            (30, "연구 핫스팟 파악", [
                "떠오르는 주제 클러스터 식별",
                "연구 공백 영역 초기 탐지",
            ]),
            (31, "@trend-analyst 완료", [
                "동향 분석 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (32, "@methodology-scanner 시작", [
                "에이전트 호출 및 문헌 데이터 전달",
            ]),
            (33, "방법론 유형 분류", [
                "양적/질적/혼합 방법론 분포 분석",
                "연구 설계 패턴 식별",
                "방법론적 강점/약점 초기 평가",
            ]),
            (34, "Cross-Validation Gate 1", [
                "Wave 1 전체 에이전트 출력 교차 검증",
                "불일치 항목 식별 및 해결",
                "Gate 1 통과 판정",
            ]),
        ]),
        ("Phase 1 Wave 2: 심층 분석", [
            (35, "@theoretical-framework-analyst 시작", [
                "에이전트 호출 및 Wave 1 결과 전달",
            ]),
            (36, "이론 식별 및 검토", [
                "관련 이론 목록 작성",
                "각 이론의 적용 가능성 평가",
                "이론 간 관계 매핑",
            ]),
            (37, "이론적 렌즈 제안", [
                "본 연구에 최적 이론 프레임워크 추천",
                "이론적 정당성 논거 작성",
            ]),
            (38, "@theoretical-framework-analyst 완료", [
                "이론 분석 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (39, "@empirical-evidence-analyst 시작", [
                "에이전트 호출 및 이론 분석 결과 전달",
            ]),
            (40, "실증연구 결과 정리", [
                "주요 실증 연구 결과 추출",
                "연구 간 결과 비교 매트릭스 생성",
            ]),
            (41, "효과 크기 분석", [
                "보고된 효과 크기 수집",
                "메타분석적 종합 수행",
            ]),
            (42, "@empirical-evidence-analyst 완료", [
                "실증 분석 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (43, "@gap-identifier 시작", [
                "에이전트 호출 및 이론/실증 분석 전달",
            ]),
            (44, "연구 갭 식별", [
                "이론적 갭 식별",
                "방법론적 갭 식별",
                "맥락적 갭 식별",
            ]),
            (45, "갭 중요성 평가", [
                "각 갭의 학술적 영향력 평가",
                "갭 해결 가능성 평가",
            ]),
            (46, "@gap-identifier 완료", [
                "연구 갭 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (47, "@variable-relationship-analyst 시작", [
                "에이전트 호출 및 문헌 종합 데이터 전달",
            ]),
            (48, "변수 관계 분석", [
                "독립/종속/매개/조절 변수 식별",
                "변수 간 관계 유형 분류",
                "관계 강도 및 방향 정리",
            ]),
            (49, "@variable-relationship-analyst 완료", [
                "변수 관계 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (50, "Cross-Validation Gate 2", [
                "Wave 2 전체 에이전트 출력 교차 검증",
                "Wave 1-2 간 일관성 확인",
                "Gate 2 통과 판정",
            ]),
        ]),
        ("Phase 1 Wave 3: 비판적 분석", [
            (51, "@critical-reviewer 시작", [
                "에이전트 호출 및 Wave 1-2 전체 결과 전달",
            ]),
            (52, "논리적 일관성 평가", [
                "주장-증거 정합성 검토",
                "논리적 오류 및 비약 식별",
            ]),
            (53, "대안적 해석 탐색", [
                "반론 및 대안 설명 생성",
                "연구 결과의 다각적 해석 정리",
            ]),
            (54, "@critical-reviewer 완료", [
                "비판적 검토 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (55, "@methodology-critic 시작", [
                "에이전트 호출 및 비판 검토 결과 전달",
            ]),
            (56, "타당도 위협 분석", [
                "내적/외적 타당도 위협 식별",
                "구성 타당도 검토",
            ]),
            (57, "측정 신뢰도 검토", [
                "측정 도구 신뢰도 평가",
                "반복 가능성 분석",
            ]),
            (58, "@methodology-critic 완료", [
                "방법론 비평 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (59, "@limitation-analyst 시작", [
                "에이전트 호출 및 비판/방법론 결과 전달",
            ]),
            (60, "공통 한계점 정리", [
                "선행연구 공통 한계점 분류",
                "한계점 빈도 및 심각도 평가",
            ]),
            (61, "극복 가능 한계 식별", [
                "본 연구에서 극복 가능한 한계 선별",
                "극복 전략 초안 작성",
            ]),
            (62, "@limitation-analyst 완료", [
                "한계점 분석 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (63, "@future-direction-analyst 시작", [
                "에이전트 호출 및 전체 Wave 3 결과 전달",
            ]),
            (64, "후속 연구 정리", [
                "선행연구 제안 후속 연구 수집",
                "본 연구의 포지셔닝 제안",
            ]),
            (65, "@future-direction-analyst 완료", [
                "미래 방향 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (66, "Cross-Validation Gate 3", [
                "Wave 3 전체 에이전트 출력 교차 검증",
                "Wave 1-3 간 일관성 최종 확인",
                "Gate 3 통과 판정",
            ]),
        ]),
        ("Phase 1 Wave 4: 종합", [
            (67, "@synthesis-agent 시작", [
                "에이전트 호출 및 Wave 1-3 전체 결과 전달",
            ]),
            (68, "문헌 주제별 종합", [
                "주제별 문헌 클러스터링",
                "핵심 논쟁 및 합의 사항 정리",
            ]),
            (69, "문헌검토 초안 작성", [
                "서론-본론-결론 구조 초안 작성",
                "인용 및 참고문헌 초안 삽입",
            ]),
            (70, "@synthesis-agent 완료", [
                "문헌검토 초안 저장",
                "GroundedClaim 검증",
            ]),
            (71, "@conceptual-model-builder 시작", [
                "에이전트 호출 및 종합 결과 전달",
            ]),
            (72, "연구모델 시각화", [
                "변수 관계 다이어그램 생성",
                "가설 경로 모델 설계",
            ]),
            (73, "@conceptual-model-builder 완료", [
                "개념적 모델 보고서 저장",
                "GroundedClaim 검증",
            ]),
            (74, "Full SRCS Evaluation", [
                "전체 Wave 1-4 SRCS 4축 평가",
                "품질 기준 미달 항목 식별 및 보완",
            ]),
        ]),
        ("Phase 1 Wave 5: 품질 보증", [
            (75, "@plagiarism-checker 시작", [
                "에이전트 호출 및 문헌검토 초안 전달",
            ]),
            (76, "원본성 검사", [
                "유사도 분석 수행",
                "부적절 인용 식별 및 수정 제안",
            ]),
            (77, "@plagiarism-checker 완료", [
                "표절 검사 보고서 저장",
            ]),
            (78, "@unified-srcs-evaluator 시작", [
                "에이전트 호출 및 전체 클레임 데이터 전달",
            ]),
            (79, "전체 클레임 평가", [
                "모든 GroundedClaim 교차 일관성 검사",
                "신뢰도 점수 최종 산출",
            ]),
            (80, "@unified-srcs-evaluator 완료", [
                "통합 SRCS 평가 보고서 저장",
            ]),
            (81, "@research-synthesizer 시작", [
                "에이전트 호출 및 품질 보증 결과 전달",
            ]),
            (82, "Insights File 생성", [
                "최종 Insights File 작성",
                "Phase 1 완료 요약 생성",
            ]),
        ]),
        ("HITL-2: 문헌검토 결과 검토", [
            (83, "15개 분석 결과 요약 제시", [
                "Wave 1-5 에이전트별 핵심 발견 요약",
                "시각적 대시보드 형태로 제시",
            ]),
            (84, "SRCS 품질 보고서 제시", [
                "4축 평가 결과 표시",
                "품질 미달 항목 하이라이트",
            ]),
            (85, "표절 검사 결과 제시", [
                "유사도 비율 및 상세 결과 표시",
                "수정 필요 부분 표시",
            ]),
            (86, "사용자 검토 대기", [
                "사용자 피드백 입력 수집",
                "승인/수정/거부 의사결정 대기",
            ]),
            (87, "피드백 반영", [
                "사용자 수정 요청 사항 반영",
                "수정된 문헌검토 재검증",
            ]),
            (88, "Context Snapshot 저장", [
                "Phase 1 전체 컨텍스트 스냅샷 생성",
                "session.json 업데이트",
            ]),
        ]),
        ("Phase 2: 연구설계", [
            (89, "HITL-3 연구유형 최종 확정", [
                "문헌검토 결과 기반 연구유형 재확인",
                "사용자 최종 승인",
            ]),
            (90, "연구유형별 분기", [
                "양적/질적/혼합/철학적 경로 결정",
                "해당 유형 에이전트 파이프라인 구성",
            ]),
            (91, "가설/연구질문/논제 정교화", [
                "문헌검토 기반 가설/논제 구체화",
                "조작적 정의 초안 작성",
            ]),
            (92, "연구모델 개발", [
                "개념적 모델 정교화",
                "변수 간 경로 확정",
            ]),
            (93, "표본/참여자/텍스트 선정 설계", [
                "모집단/분석 대상 정의",
                "표본 크기/텍스트 범위 산정 근거 제시",
            ]),
            (94, "분석 계획 수립", [
                "가설별 분석 기법 매핑",
                "분석 절차 순서 설계",
            ]),
            *_steps_95_98,
            (99, "[질적] @paradigm-consultant", [
                "인식론적/존재론적 입장 명확화",
                "연구 패러다임 정당성 논거 작성",
            ]),
            (100, "[질적] @participant-selector", [
                "의도적 표본추출 전략 설계",
                "포화 기준 설정",
            ]),
            (101, "[질적] @qualitative-data-designer", [
                "인터뷰 프로토콜 설계",
                "관찰 가이드 작성",
            ]),
            (102, "[질적] @qualitative-analysis-planner", [
                "코딩 전략 설계",
                "신뢰성 확보 방안 수립",
            ]),
            (103, "[혼합] @mixed-methods-designer", [
                "양적/질적 통합 설계 유형 결정",
                "단계별 자료수집 순서 설계",
            ]),
            (104, "[혼합] @integration-strategist", [
                "자료 통합 방법 설계",
                "결과 통합 전략 수립",
            ]),
            (105, "연구설계 문서 통합", [
                "전체 연구설계 문서 병합",
                "일관성 최종 점검",
            ]),
            (106, "HITL-4 연구설계 검토", [
                "연구설계 요약 제시",
                "사용자 승인 대기",
            ]),
            (107, "피드백 반영", [
                "사용자 수정 요청 반영",
                "수정된 연구설계 재검증",
            ]),
            (108, "Context Snapshot 저장", [
                "Phase 2 전체 컨텍스트 스냅샷 생성",
                "session.json 업데이트",
            ]),
        ]),
        ("Phase 3: 논문 작성", [
            (109, "HITL-5 논문 형식 선택", [
                "5장 구성/3편 논문/모노그래프 옵션 제시",
                "사용자 형식 선택 및 확인",
            ]),
            (110, "인용 스타일 설정", [
                "APA7/Chicago/MLA/Harvard/IEEE 옵션 제시",
                "스타일별 예시 표시 및 선택 확인",
            ]),
            (111, "@thesis-architect 시작", [
                "에이전트 호출 및 연구설계 결과 전달",
            ]),
            (112, "상세 아웃라인 설계", [
                "장별 목차 구조 설계",
                "각 절별 핵심 내용 요약 작성",
                "예상 분량 배분",
            ]),
            (113, "@thesis-architect 완료", [
                "아웃라인 문서 저장",
            ]),
            (114, "HITL-6 아웃라인 승인", [
                "아웃라인 제시 및 사용자 검토",
                "수정 요청 반영 후 최종 승인",
            ]),
            (115, "@thesis-writer Ch.1 서론", [
                "연구 배경 및 필요성 집필",
                "연구 목적 및 질문 기술",
                "논문 구성 개요 작성",
            ]),
            (116, "Ch.1 검토", [
                "GRA 준수 검증",
                "pTCS 신뢰도 점수 확인",
            ]),
            (117, "@thesis-writer Ch.2 문헌검토", [
                "이론적 배경 집필",
                "선행연구 검토 집필",
                "연구 갭 및 본 연구 위치 기술",
            ]),
            (118, "Ch.2 검토", [
                "GRA 준수 검증",
                "pTCS 신뢰도 점수 확인",
            ]),
            (119, "@thesis-writer Ch.3 연구방법", [
                "연구 설계 기술",
                "자료수집 방법 기술",
                "분석 방법 기술",
            ]),
            (120, "Ch.3 검토", [
                "GRA 준수 검증",
                "pTCS 신뢰도 점수 확인",
            ]),
            (121, "@thesis-writer Ch.4 연구결과", [
                "분석 결과 기술",
                "가설 검증 결과 정리",
                "표/그림 생성 및 삽입",
            ]),
            (122, "Ch.4 검토", [
                "GRA 준수 검증",
                "pTCS 신뢰도 점수 확인",
            ]),
            (123, "@thesis-writer Ch.5 결론", [
                "연구 요약 집필",
                "학술적/실무적 시사점 기술",
                "한계점 및 향후 연구 방향 기술",
            ]),
            (124, "Ch.5 검토", [
                "GRA 준수 검증",
                "pTCS 신뢰도 점수 확인",
            ]),
            (125, "@thesis-reviewer 품질 검토", [
                "전체 논문 학술적 엄밀성 검토",
                "논리적 일관성 검토",
                "인용 정확성 검토",
            ]),
            (126, "@plagiarism-checker 최종", [
                "최종 원고 표절 검사 수행",
                "15% 미만 유사도 확인",
            ]),
            (127, "HITL-7 초안 검토", [
                "전체 초안 사용자 제시",
                "사용자 검토 및 피드백 수집",
            ]),
            (128, "피드백 반영", [
                "사용자 수정 요청 반영",
                "수정 부분 재검증",
            ]),
            (129, "최종본 작성", [
                "전체 논문 최종 편집",
                "형식 통일성 최종 점검",
            ]),
            (130, "참고문헌 정리", [
                "참고문헌 목록 최종 정리",
                "인용 스타일 일관성 확인",
            ]),
            (131, "부록 정리", [
                "부록 자료 수집 및 편집",
                "부록 번호 체계 정리",
            ]),
            (132, "Context Snapshot 저장", [
                "Phase 3 전체 컨텍스트 스냅샷 생성",
                "session.json 업데이트",
            ]),
        ]),
        ("Phase 4: 투고 전략", [
            (133, "@publication-strategist 시작", [
                "에이전트 호출 및 논문 메타데이터 전달",
            ]),
            (134, "적합 학술지 분석", [
                "분야별 학술지 스코프 매칭",
                "영향력 지수(IF/SJR) 분석",
            ]),
            (135, "투고 우선순위 추천", [
                "학술지별 적합도 점수 산출",
                "1순위~3순위 추천 및 근거 제시",
            ]),
            (136, "@publication-strategist 완료", [
                "투고 전략 보고서 저장",
            ]),
            (137, "@manuscript-formatter 시작", [
                "에이전트 호출 및 선택 학술지 정보 전달",
            ]),
            (138, "원고 포맷 변환", [
                "학술지 투고 규정 적용",
                "페이지 레이아웃 및 폰트 설정",
            ]),
            (139, "Abstract 작성", [
                "구조화된 초록 작성 (목적/방법/결과/결론)",
                "영문/한글 초록 작성",
            ]),
            (140, "Keywords 선정", [
                "학술지 키워드 가이드라인 확인",
                "5-7개 키워드 선정 및 정렬",
            ]),
            (141, "Cover Letter 작성", [
                "학술지 편집자 대상 커버레터 작성",
                "연구 기여 핵심 포인트 강조",
            ]),
            (142, "@manuscript-formatter 완료", [
                "최종 원고 패키지 저장",
                "투고 파일 목록 생성",
            ]),
            (143, "투고 체크리스트 확인", [
                "학술지 투고 요구사항 점검",
                "필수 첨부 파일 확인",
            ]),
            (144, "HITL-8 최종 검토", [
                "최종 투고 패키지 사용자 제시",
                "사용자 최종 검토 및 피드백",
            ]),
            (145, "최종 승인", [
                "사용자 최종 승인 확인",
                "투고 준비 완료 마킹",
            ]),
            (146, "워크플로우 완료", [
                "Phase 4 완료 보고서 생성",
                "전체 워크플로우 요약 생성",
            ]),
        ]),
        ("완료 및 아카이브", [
            (147, "최종 산출물 정리", [
                "전체 산출물 목록 생성",
                "파일 정합성 최종 확인",
            ]),
            (148, "Context Snapshot 최종 저장", [
                "전체 워크플로우 최종 스냅샷 생성",
                "session.json 최종 업데이트",
            ]),
            (149, "워크플로우 로그 아카이브", [
                "실행 로그 압축 및 저장",
                "성능 메트릭 요약 생성",
            ]),
            (150, "세션 종료", [
                "세션 상태 'completed' 마킹",
                "종료 메시지 출력",
            ]),
        ]),
    ]

    lines = ["# 박사논문 연구 워크플로우 체크리스트 (150단계)\n"]

    for section_title, items in sections:
        first_step = items[0][0]
        last_step = items[-1][0]
        step_range = f"(Steps {first_step}-{last_step})"
        # Insert step range before trailing bracket tags like [Mode A Only]
        bracket_match = re.search(r"(\s*\[.+\])\s*$", section_title)
        if bracket_match:
            base_title = section_title[:bracket_match.start()]
            bracket_tag = bracket_match.group(1)
            header = f"{base_title} {step_range}{bracket_tag}"
        else:
            header = f"{section_title} {step_range}"
        lines.append(f"\n## {header}\n")
        for step, task, *rest in items:
            lines.append(f"- [ ] {step}. {task}")
            sub_items = rest[0] if rest else []
            for sub in sub_items:
                lines.append(f"  - [ ] {sub}")
        lines.append("")

    # Add footer
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.extend([
        "---",
        "",
        "**진행 상태**: Step 1 / 150",
        "**현재 Phase**: Phase 0 - 초기화",
        f"**마지막 업데이트**: {timestamp}",
    ])

    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    with open(checklist_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return checklist_path


def parse_checklist(checklist_path: Path) -> list[dict[str, Any]]:
    """Parse a checklist file into a list of items.

    Args:
        checklist_path: Path to the checklist markdown file

    Returns:
        List of dictionaries with step info
    """
    with open(checklist_path, encoding="utf-8") as f:
        content = f.read()

    return parse_checklist_from_content(content)


def update_step_status(checklist_path: Path, step: int, status: str) -> None:
    """Update the status of a specific step.

    Args:
        checklist_path: Path to the checklist file
        step: Step number to update
        status: New status (pending, in_progress, completed)

    Raises:
        ValueError: If step is invalid or status is invalid
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")

    if step < 1 or step > TOTAL_STEPS:
        raise ValueError(f"Invalid step: {step}. Must be between 1 and {TOTAL_STEPS}")

    with open(checklist_path, encoding="utf-8") as f:
        content = f.read()

    # Map status to checkbox
    checkbox_map = {
        "pending": " ",
        "in_progress": "/",  # Using / for in-progress
        "completed": "x",
    }
    new_checkbox = checkbox_map[status]

    # Pattern to find the specific step
    pattern = rf"^(- \[)[ xX/](\] {step}\. .+)$"
    # Pattern to detect sub-items (indented checkboxes without step numbers)
    sub_item_pattern = r"^  - \[[ xX/]\] .+"
    # Pattern to detect the next primary step or section header (cascade stop)
    primary_step_pattern = r"^- \[[ xX/]\] \d+\. .+"
    section_header_pattern = r"^## "

    lines = content.split("\n")
    found = False
    primary_line_idx = -1

    for i, line in enumerate(lines):
        match = re.match(pattern, line.strip())
        if match:
            prefix, suffix = match.groups()
            lines[i] = f"{prefix}{new_checkbox}{suffix}"
            found = True
            primary_line_idx = i
            break

    if not found:
        raise ValueError(f"Step {step} not found in checklist")

    # Cascade: update sub-items following this primary step
    if primary_line_idx >= 0:
        for j in range(primary_line_idx + 1, len(lines)):
            stripped = lines[j].strip()
            # Stop at next primary step or section header
            if re.match(primary_step_pattern, stripped) or re.match(section_header_pattern, stripped):
                break
            # Update sub-item checkbox if it matches
            if re.match(sub_item_pattern, lines[j]):
                lines[j] = re.sub(r"^(  - \[)[ xX/](\] .+)$", rf"\g<1>{new_checkbox}\2", lines[j])

    # Update footer
    for i, line in enumerate(lines):
        if line.startswith("**진행 상태**"):
            items = parse_checklist_from_content("\n".join(lines))
            completed = sum(1 for item in items if item["status"] == "completed")
            lines[i] = f"**진행 상태**: Step {completed + 1} / 150"
        elif line.startswith("**현재 Phase**"):
            phase = get_phase_for_step(step)
            phase_names = {
                "phase0": "Phase 0 - 초기화",
                "phase1-wave1": "Phase 1 Wave 1 - 기초 문헌 탐색",
                "phase1-wave2": "Phase 1 Wave 2 - 심층 분석",
                "phase1-wave3": "Phase 1 Wave 3 - 비판적 분석",
                "phase1-wave4": "Phase 1 Wave 4 - 종합",
                "phase1-wave5": "Phase 1 Wave 5 - 품질 보증",
                "hitl-2": "HITL-2 - 문헌검토 결과 검토",
                "phase2": "Phase 2 - 연구설계",
                "phase3": "Phase 3 - 논문 작성",
                "phase4": "Phase 4 - 투고 전략",
                "completion": "완료 및 아카이브",
            }
            lines[i] = f"**현재 Phase**: {phase_names.get(phase, phase)}"
        elif line.startswith("**마지막 업데이트**"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines[i] = f"**마지막 업데이트**: {timestamp}"

    with open(checklist_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_checklist_from_content(content: str) -> list[dict[str, Any]]:
    """Parse checklist from string content."""
    items = []
    pattern = r"^- \[([ xX/])\] (\d+)\. (.+)$"

    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            checkbox, step_num, task = match.groups()
            if checkbox.lower() == "x":
                status = "completed"
            elif checkbox == "/":
                status = "in_progress"
            else:
                status = "pending"
            items.append({
                "step": int(step_num),
                "task": task.strip(),
                "status": status,
                "phase": get_phase_for_step(int(step_num)),
            })

    return items


def get_progress(checklist_path: Path) -> dict[str, Any]:
    """Get overall progress statistics.

    Args:
        checklist_path: Path to the checklist file

    Returns:
        Dictionary with progress statistics
    """
    items = parse_checklist(checklist_path)

    completed = sum(1 for item in items if item["status"] == "completed")
    in_progress = sum(1 for item in items if item["status"] == "in_progress")
    pending = sum(1 for item in items if item["status"] == "pending")
    total = len(items)

    return {
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "total": total,
        "percentage": (completed / total) * 100 if total > 0 else 0,
    }


def get_current_step(checklist_path: Path) -> dict[str, Any] | None:
    """Get the current step being worked on.

    Args:
        checklist_path: Path to the checklist file

    Returns:
        Dictionary with current step info, or None if no step in progress
    """
    items = parse_checklist(checklist_path)

    # First, look for in_progress
    for item in items:
        if item["status"] == "in_progress":
            return item

    # If none in progress, find first pending
    for item in items:
        if item["status"] == "pending":
            return item

    return None


def get_phase_progress(checklist_path: Path, phase: str) -> dict[str, Any]:
    """Get progress for a specific phase.

    Args:
        checklist_path: Path to the checklist file
        phase: Phase name

    Returns:
        Dictionary with phase progress statistics
    """
    items = parse_checklist(checklist_path)
    phase_range = get_steps_for_phase(phase)

    phase_items = [
        item for item in items
        if phase_range["start"] <= item["step"] <= phase_range["end"]
    ]

    completed = sum(1 for item in phase_items if item["status"] == "completed")
    total = len(phase_items)

    return {
        "phase": phase,
        "completed": completed,
        "total": total,
        "percentage": (completed / total) * 100 if total > 0 else 0,
    }


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage thesis workflow checklist")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new checklist")
    create_parser.add_argument("output_dir", type=Path, help="Output directory")
    create_parser.add_argument("--research-type", choices=["quantitative", "qualitative", "mixed", "philosophical"],
                               default=None, help="Research type for conditional steps")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update step status")
    update_parser.add_argument("checklist", type=Path, help="Checklist file path")
    update_parser.add_argument("step", type=int, help="Step number")
    update_parser.add_argument("status", choices=["pending", "in_progress", "completed"])

    # Progress command
    progress_parser = subparsers.add_parser("progress", help="Show progress")
    progress_parser.add_argument("checklist", type=Path, help="Checklist file path")

    args = parser.parse_args()

    if args.command == "create":
        path = create_checklist(args.output_dir, research_type=args.research_type)
        print(f"Checklist created at: {path}")
    elif args.command == "update":
        update_step_status(args.checklist, args.step, args.status)
        print(f"Step {args.step} updated to {args.status}")
    elif args.command == "progress":
        progress = get_progress(args.checklist)
        print(f"Progress: {progress['completed']}/{progress['total']} ({progress['percentage']:.1f}%)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
