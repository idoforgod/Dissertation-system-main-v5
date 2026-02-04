# Citation Style Guide

워크플로우에서 지원하는 인용 스타일 가이드입니다.

---

## 지원 스타일 목록

| 스타일 키 | 표시 이름 | 주요 분야 |
|-----------|-----------|-----------|
| `apa7` | APA 7th Edition | 사회과학, 경영학, 교육학 |
| `chicago17` | Chicago Manual of Style 17th Edition | 인문학, 역사학 |
| `mla9` | MLA 9th Edition | 어문학, 인문학 |
| `harvard` | Harvard Referencing | 영연방권 대학교 표준 |
| `ieee` | IEEE Citation Style | 공학, 컴퓨터과학 |

---

## 스타일별 상세 규칙

### APA 7th Edition (`apa7`)

- **인용 방식**: 저자-연도 괄호형
- **본문 인용 예시**: `(Smith, 2024)` 또는 `Smith (2024)`
- **복수 저자 연결어**: `&` (예: Smith & Jones, 2024)
- **et al. 기준**: 저자 3인 이상
- **각주/미주**: 미주 (endnotes)
- **참고문헌 제목**: References / 참고문헌

### Chicago 17th Edition (`chicago17`)

- **인용 방식**: 각주 상첨자
- **본문 인용 예시**: `^1` (상첨자 각주 번호)
- **복수 저자 연결어**: `and`
- **et al. 기준**: 저자 4인 이상
- **각주/미주**: 각주 (footnotes)
- **참고문헌 제목**: Bibliography / 참고문헌

### MLA 9th Edition (`mla9`)

- **인용 방식**: 저자-페이지 괄호형
- **본문 인용 예시**: `(Smith 42)` 또는 `Smith (42)`
- **복수 저자 연결어**: `and`
- **et al. 기준**: 저자 3인 이상
- **각주/미주**: 미주 (endnotes)
- **참고문헌 제목**: Works Cited / 인용 문헌

### Harvard Referencing (`harvard`)

- **인용 방식**: 저자-연도 괄호형
- **본문 인용 예시**: `(Smith 2024)` 또는 `Smith (2024)`
- **복수 저자 연결어**: `&`
- **et al. 기준**: 저자 3인 이상
- **각주/미주**: 미주 (endnotes)
- **참고문헌 제목**: Reference List / 참고문헌 목록

### IEEE Citation Style (`ieee`)

- **인용 방식**: 번호 대괄호
- **본문 인용 예시**: `[1]` 또는 `[1, 2]` 또는 `[1]-[3]`
- **복수 저자 연결어**: `and`
- **et al. 기준**: 저자 3인 이상
- **각주/미주**: 미주 (endnotes)
- **참고문헌 제목**: References / 참고문헌

---

## 데이터 흐름

```
HITL-0 (사용자 선택)
  → init_session.py (citation_style_config.py에서 config 생성)
    → session.json > options.citation_style + options.citation_config
      → thesis-writer-rlm.md (RLM 프롬프트에 스타일 적용)
      → run_writing_validated.py (아웃라인에 스타일 반영)
      → manage_references.py (스타일별 인용 패턴 추출)
      → validation-checks/SKILL.md (스타일별 검증 규칙)
```

---

## session.json 내 저장 형식

```json
{
  "options": {
    "citation_style": "apa7",
    "citation_config": {
      "style_key": "apa7",
      "display_name": "APA 7th Edition",
      "note_type": "endnotes",
      "in_text_format": "author_year_parenthetical",
      "in_text_example": "(Smith, 2024) or Smith (2024)",
      "bibliography_title": "References",
      "bibliography_title_ko": "참고문헌"
    }
  }
}
```

---

## Single Source of Truth

모든 인용 스타일 정의는 다음 파일에 집중 관리됩니다:

```
.claude/skills/thesis-orchestrator/scripts/citation_style_config.py
```

다른 파일에서 인용 스타일 정보가 필요할 때, 이 모듈에서 import하거나
`session.json`의 `options.citation_config` 객체를 참조하십시오.
하드코딩된 스타일 문자열을 사용하지 마십시오.
