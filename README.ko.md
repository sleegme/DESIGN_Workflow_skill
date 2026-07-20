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

계약의 `meaningful_design_exists`는 파일 존재 여부가 아니라 증거에 보존해야
할 확립된 디자인 체계가 있는지를 뜻합니다. 따라서 wireframe이 있어도 의미
있는 시각 체계가 없다면 `false`인 `create`를 사용하고 content order와
information architecture를 `fixed`에 기록할 수 있습니다.

## 개발 및 검증

Python 3.11 이상을 사용합니다.

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_project.py
agentskills validate design-workflow
python -m unittest discover -s tests -v
python scripts/package_skill.py
python scripts/package_project.py
```

루트의 `VERSION`이 릴리스 버전의 단일 기준입니다. 두 패키징 명령은 이를
기본으로 읽으며, 선택적으로 전달한 `--version`도 반드시 일치해야 합니다.

결정적인 단위·불변식 검증은 구조, 공식 Agent Skills 형식, route contract,
fixture 정합성, 패키지 allowlist와 재현 가능한 ZIP을 검사하며 모델을
실행하지 않습니다. 실제 의미 라우팅은 `evals/semantic-smoke.json`을
클라이언트에서 실행하고 다음 명령으로 별도 채점합니다.

```bash
python scripts/grade_semantic_results.py path/to/client-result.json
```

스킬 activation test는 모델과 클라이언트에 따라 비결정적입니다.
`evals/trigger-cases.json`은 반복 활성화 평가를 위한 균형 잡힌 긍정·근접
부정 사례이며, 이를 정적 단위 테스트 결과로 과장하지 않습니다.
Semantic forward test 역시 기록된 한 client·model·commit·suite revision의
post-activation 동작만 보여줍니다. v0.2.1부터 원시 결과는
[`evals/semantic-result.schema.json`](evals/semantic-result.schema.json)을 따르고
실행 시각, commit SHA, skill version, runner, 모델, reasoning effort, suite
provenance, 실제 route와 boundary 근거를 기록해야 합니다. 자세한 절차는
[`evals/README.md`](evals/README.md)에 있습니다.

grader는 필드 완전성, route 일치, 실행자가 선언한 boundary 판정과 근거
존재를 확인할 뿐 실제 응답이 경계를 지켰다고 독립적으로 의미 판정하지
않습니다. 사람 또는 별도 모델이 근거와 안전하게 기록된 응답 일부를
expected boundary와 대조해야 합니다.

### 현재 검증 결과

- 프로젝트·링크 검증: 통과
- 공식 `agentskills` 형식 검증: 통과
- 의존성 없는 단위 테스트: 이 revision에서 22/22 통과
- 과거 v0.2.0 post-activation semantic forward test: 8개 경로 16/16 기록;
  v0.2.1 결과로 재실행하거나 이름을 바꾸지 않음
- 재현 가능한 아카이브와 최상위 폴더 검증: 통과

원시·채점 결과는 `evals/results/`에 있습니다. 이는 기록된 실행에서 스킬이
로드된 뒤의 라우팅을 보여주며, 모든 모델·클라이언트의 activation 정확도나
독립적으로 입증된 semantic boundary를 주장하지 않습니다.

릴리스 skill ZIP은 명시적 파일·디렉터리 allowlist를 사용합니다. 생성된
Python cache는 제외합니다. 숨김 파일, 임시·백업 파일, ZIP/checksum, symlink,
credential로 보이는 파일명, 예상하지 않은 형식과 대형 파일이 있으면
조용히 포함하지 않고 패키징을 실패시킵니다. 저장소 문서·eval·tests는
runtime skill ZIP에 포함되지 않습니다.

## 릴리스

1. `VERSION`과 `CHANGELOG.md`를 갱신합니다.
2. 위 검증 명령을 모두 실행합니다.
3. `git tag "v$(<VERSION)"`처럼 `VERSION`에서 tag를 생성해 push합니다.
4. release workflow는 `GITHUB_REF_NAME == "v" + VERSION`을 요구합니다.
   불일치하면 GitHub Release를 만들기 전에 실패합니다.

## 라이선스와 출처

Apache-2.0으로 배포합니다. Anthropic과 Google 자료에서 수정·적용한 부분은
`SOURCE_AUDIT.md`와 `THIRD_PARTY_NOTICES.md`에 기록되어 있으며, 필수 법적
파일은 배포 스킬에도 포함됩니다.
