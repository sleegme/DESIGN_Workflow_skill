# design-workflow

[English](README.md) | **한국어**

기존 제품을 실수로 재설계하지 않도록 시각 디자인 작업을 라우팅하는 매체 중립적 Agent Skill입니다.

핵심 원칙은 단순합니다.

> 의미 있는 기존 디자인이 있다면 기본적으로 보존합니다. 완전히 새로운 작업이거나 사용자가 명시적으로 재설계를 승인한 경우에만 새로운 디자인 방향을 만듭니다.

## 적용 범위

이 스킬은 인터페이스, 웹사이트, 문서, 슬라이드, 포스터, 브랜드 자산, 이미지, 데이터 시각화, 영상, 인쇄물을 다룹니다.

작업은 다음 8개 의도로 분류됩니다.

- `preserve`: 기존 디자인을 유지하면서 수정
- `expand`: 기존 시스템과 일치하는 화면·상태·구성 요소 추가
- `create`: 의미 있는 기존 디자인이 없는 상태에서 새 디자인 생성
- `redesign`: 명시적으로 승인된 전면 재설계
- `critique`: 수정하지 않고 분석·비평
- `brand-check`: 브랜드·디자인 시스템 일관성 검수
- `translate`: 다른 매체·비율·플랫폼으로 디자인 변환
- `profile`: `DESIGN.md` 또는 디자인 프로필 추출

## 설치

전체 `design-workflow/` 디렉터리를 Agent Skills 호환 스킬 디렉터리에 배치합니다. 공개 Agent Skills 표준은 `SKILL.md`를 포함한 폴더를 사용하며, 여러 클라이언트가 프로젝트 로컬 경로인 `.agents/skills/design-workflow/`를 지원합니다.

Agent Skills 명세상 디렉터리 이름은 `SKILL.md`의 `name` 필드와 일치해야 하므로 반드시 `design-workflow`를 사용해야 합니다.

## 사용법

자연어로 요청하면 됩니다.

```text
기존 체크아웃 화면의 레이아웃은 유지하고 완성도만 높여줘.
```

```text
현재 앱과 자연스럽게 이어지는 계정 보안 화면을 추가해줘.
```

```text
아직 디자인이 없어. 과학 주석 도구의 시각 방향을 새로 설계해줘.
```

```text
콘텐츠 계층은 유지하되 현재 랜딩 페이지를 처음부터 다시 디자인해줘.
```

```text
현재 구현과 스크린샷을 바탕으로 DESIGN.md를 추출해줘.
```

## 디렉터리 구조

```text
design-workflow/
├── SKILL.md
├── README.md
├── README.ko.md
├── LICENSE
├── NOTICE
├── THIRD_PARTY_NOTICES.md
├── SOURCE_AUDIT.md
├── CHANGELOG.md
├── RELEASE_CHECKLIST.md
├── CONTRIBUTING.md
├── SECURITY.md
├── references/
├── assets/
├── examples/
├── scripts/
├── tests/
└── .github/workflows/ci.yml
```

`SKILL.md`에는 핵심 라우팅과 디자인 변경 경계만 들어 있습니다. 조건별 상세 지침은 `references/`에서 점진적으로 불러옵니다.

## 검증

의존성 없는 기본 검사는 다음과 같이 실행합니다.

```bash
python scripts/validate_skill.py .
python scripts/test_routing_cases.py

# 스킬 디렉터리를 패키징하거나 설치하기 전
python scripts/validate_skill.py --strict-directory-name .
```

공식 형식 검사도 함께 실행할 수 있습니다.

```bash
skills-ref validate .
```

라우팅 테스트에는 실제 사용에 가까운 긍정·부정·모호한 요청과 매체 변환 요청이 포함됩니다. 저장소에 포함된 v0.1.0 보고서는 작성 세션 기준 dry run이며, 모든 모델과 클라이언트에서 동일한 동작을 보장하는 벤치마크는 아닙니다.

## 디자인 변경 경계

다음 표현만으로는 재설계가 승인되지 않습니다.

- 개선해줘
- 다듬어줘
- 현대적으로 바꿔줘
- 정리해줘
- 더 좋게 만들어줘
- 기능을 추가해줘
- 반응형 문제를 고쳐줘
- 브랜드에 맞춰줘

재설계로 분류하려면 기존 구조나 시각 언어를 교체하라는 명시적 요청 또는 그에 준하는 분명한 승인이 필요합니다.

## 프로젝트별 규칙

이 저장소에는 특정 프로젝트, 회사, 팔레트, 제품에 종속된 맥락이 포함되지 않습니다. 프로젝트별 규칙은 대상 저장소의 `DESIGN.md`, `.design/PROFILE.md`, 브랜드 가이드, 컴포넌트 라이브러리 또는 이에 해당하는 기준 문서에 작성해야 합니다.

## 라이선스와 출처

이 패키지는 Apache-2.0 라이선스로 배포됩니다. Anthropic과 Google 자료에서 수정·적용한 부분은 `SOURCE_AUDIT.md`와 `THIRD_PARTY_NOTICES.md`에 기록되어 있습니다. 출처를 검증하지 못한 Canva 자료는 포함하지 않았습니다.
