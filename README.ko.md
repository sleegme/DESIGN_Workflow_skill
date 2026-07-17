# design-workflow

[English](README.md) | **한국어**

`design-workflow`는 시각 작업을 사용자 의도에 따라 라우팅하고 의도하지
않은 재설계를 막는 Agent Skill입니다. 문서·슬라이드·이미지·Figma·웹·코드
등 매체별 실행 워크플로보다 먼저 변경 경계를 정하는 정책 계층으로
동작합니다.

핵심 원칙은 하나입니다. 의미 있는 기존 디자인은 사용자가 교체를 명확히
승인하기 전까지 보존합니다.

## 지원 경로

| 경로 | 목적 |
|---|---|
| `preserve` | 기존 산출물을 국소적으로 수정·개선 |
| `expand` | 기존 시스템을 따르는 새 화면·상태·슬라이드 추가 |
| `create` | 의미 있는 디자인이 없을 때 새 방향 수립 |
| `redesign` | 명시적으로 승인된 디자인 차원 교체 |
| `critique` | 수정 없이 분석·비평 |
| `brand-check` | 브랜드 또는 디자인 시스템 기준 검수 |
| `translate` | 새 매체·비율·플랫폼 제약에 맞춰 재구성 |
| `profile` | 증거에서 `DESIGN.md` 또는 디자인 프로필 추출 |

## 설치

저장소 전체가 아니라 내부의 정확한 `design-workflow/` 폴더만 클라이언트의
스킬 디렉터리에 설치합니다.

```powershell
git clone https://github.com/sleegme/DESIGN_Workflow_skill.git
Copy-Item -Recurse DESIGN_Workflow_skill\design-workflow $env:USERPROFILE\.codex\skills\design-workflow
```

릴리스 ZIP은 항상 최상위에 `design-workflow/` 폴더를 포함하며 SHA-256
체크섬을 함께 제공합니다.

## 사용 예시

```text
Use $design-workflow to polish the existing checkout without changing its layout.
```

```text
현재 앱과 자연스럽게 이어지는 결제 내역 화면을 추가해줘.
```

```text
정보 구조는 유지하고 현재 시각 방향은 완전히 교체해줘.
```

모호하거나 영향이 큰 작업은 route contract를 만들어 표준 라이브러리만으로
검증할 수 있습니다.

```bash
python design-workflow/scripts/validate_route_contract.py contract.json
```

## 개발 및 검증

Python 3.11 이상을 사용합니다.

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_project.py
agentskills validate design-workflow
python -m unittest discover -s tests -v
python scripts/package_skill.py --version 0.2.0
python scripts/package_project.py --version 0.2.0
```

CI는 구조, 공식 Agent Skills 형식, 변경 경계 계약, 평가 fixture 품질,
재현 가능한 패키징을 검증합니다. 실제 의미 라우팅은
`evals/semantic-smoke.json`을 클라이언트에서 실행하고 다음 명령으로
채점합니다.

```bash
python scripts/grade_semantic_results.py path/to/client-result.json
```

스킬 활성화는 모델과 클라이언트에 따라 비결정적입니다.
`evals/trigger-cases.json`은 반복 활성화 평가를 위한 균형 잡힌 긍정·근접
부정 사례이며, 이를 정적 단위 테스트 결과로 과장하지 않습니다.

### 현재 검증 결과

- 프로젝트·링크 검증: 통과
- 공식 `agentskills` 형식 검증: 통과
- 의존성 없는 단위 테스트: 13/13 통과
- 독립 에이전트 의미 라우팅 forward test: 8개 경로 16/16 통과
- 재현 가능한 아카이브와 최상위 폴더 검증: 통과

원시·채점 결과는 `evals/results/`에 있습니다. 이는 스킬이 로드된 뒤의
라우팅을 검증하며, 모든 모델과 클라이언트의 활성화 정확도를 주장하지
않습니다.

## 라이선스와 출처

Apache-2.0으로 배포합니다. Anthropic과 Google 자료에서 수정·적용한 부분은
`SOURCE_AUDIT.md`와 `THIRD_PARTY_NOTICES.md`에 기록되어 있으며, 필수 법적
파일은 배포 스킬에도 포함됩니다.
