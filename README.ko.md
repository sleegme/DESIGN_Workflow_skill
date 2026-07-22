# design-workflow

[English](README.md) | **한국어**

`design-workflow`는 실제 작업을 시작하기 전에 무엇을 유지하고 무엇을
바꿀 수 있는지, 기존 디자인을 개선할지 처음부터 만들지를 ChatGPT가
판단하도록 돕습니다.

## 설치하면 무엇이 달라지나요?

이 스킬은 시각 작업에 관한 판단을 안내합니다. 스스로 산출물을 그리거나
렌더링·편집하지 않으며, 설치만으로 모든 결과물의 스타일이나 ChatGPT
화면이 자동으로 바뀌지 않습니다. 실제 작업은 ChatGPT 또는 연결된 이미지,
웹, 문서, 슬라이드, 디자인, 브라우저, 코드 실행 워크플로가 수행합니다.

기술적으로 `design-workflow`는 routing과 change boundary를 관리하는
guardrail입니다. 실행 도구가 작업하기 전에 요청을 보존, 개선, 확장, 신규
제작 또는 명시적 재설계로 분류합니다. 핵심 원칙은 하나입니다. 의미 있는
기존 디자인은 사용자가 교체를 명확히 승인하기 전까지 보존합니다.

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

## ChatGPT에 설치

사용 중인 ChatGPT 환경에서 스킬 생성 또는 업로드를 지원한다면:

1. **Plugins / Skills**를 엽니다.
2. 스킬 생성 또는 업로드 옵션을 선택합니다.
3. 해당 GitHub Release에서 `design-workflow-<version>.zip`을 내려받아
   선택합니다.
4. 스킬을 검토하고 설치를 완료합니다.

스킬 지원 여부와 정확한 메뉴 이름은 클라이언트, 계정, workspace 설정에
따라 다를 수 있습니다. 모든 ChatGPT 환경에서 업로드할 수 있다는 의미는
아닙니다.

macOS와 Windows에서 ChatGPT용 `design-workflow`를 별도 native application으로
설치하지 않습니다. 호환되는 ChatGPT Skills 화면에서 스킬을 추가합니다.

## Codex에 설치

저장소 전체가 아니라 내부의 정확한 `design-workflow/` 폴더만 클라이언트의
스킬 디렉터리에 설치합니다. 저장소 root를 설치하면 안 됩니다.

```bash
git clone https://github.com/sleegme/DESIGN_Workflow_skill.git
cp -R DESIGN_Workflow_skill/design-workflow ~/.codex/skills/design-workflow
```

```powershell
git clone https://github.com/sleegme/DESIGN_Workflow_skill.git
Copy-Item -Recurse DESIGN_Workflow_skill\design-workflow $env:USERPROFILE\.codex\skills\design-workflow
```

릴리스 ZIP은 항상 최상위에 `design-workflow/` 폴더를 포함하며 SHA-256
체크섬을 함께 제공합니다.

## 설치 확인

편집을 요청하지 않고 다음 prompt를 복사해 실행해 보세요.

```text
Use $design-workflow to classify this request without editing:
“Polish the existing dashboard while preserving its layout and brand identity.”
```

정확한 표현은 client와 model에 따라 달라지지만 다음과 같은 결과를 기대할
수 있습니다.

```text
Selected route: preserve
Fixed constraints: existing layout and brand identity
Changeable areas: local visual polish that does not alter those constraints
Redesign authorized: no
```

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
  v0.2.1 또는 v0.2.2 결과로 재실행하거나 이름을 바꾸지 않음
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
   project를 검증하고 결정적 archive를 만든 뒤 tag를 확인합니다. Release가
   없으면 만들고, 재실행 시 이미 있으면 ZIP과 checksum asset을 교체합니다.
   불일치하면 GitHub Release를 만들기 전에 실패합니다.

## 자주 묻는 질문

### 설치했는데 아무것도 달라지지 않았습니다

정상일 수 있습니다. 이 스킬은 ChatGPT 화면이나 기본 시각 스타일을 바꾸지
않습니다. 시각 디자인 판단이 필요한 요청에서 호환 workflow를 안내합니다.
위 설치 확인 prompt로 명시적으로 시험해 보세요.

### 스스로 디자인을 만드나요?

아닙니다. route를 선택하고 고정할 부분과 변경 가능한 부분을 정합니다.
실제 산출물은 ChatGPT 또는 연결된 실행 workflow가 만듭니다.

### 초안이 없어도 새 디자인을 만들 수 있나요?

의미 있는 디자인이 없으면 `create` route를 선택해 방향을 정할 수 있습니다.
이후 연결된 실행 workflow가 디자인을 만듭니다.

### 기존 디자인이 있을 때 더 유용한가요?

기존 디자인을 의도하지 않은 재설계로부터 보호할 때 특히 유용합니다. 신규
작업, 확장, 비평, brand check, 매체 변환, design profile 추출도 안내합니다.

### ChatGPT 또는 Mac에는 어떻게 설치하나요?

위 안내처럼 호환되는 ChatGPT Skills 화면에서 release ZIP을 업로드합니다.
Mac용 별도 native application은 필요하지 않습니다. Codex에서는 별도의
filesystem 설치 안내를 따릅니다.

## 라이선스와 출처

Apache-2.0으로 배포합니다. Anthropic과 Google 자료에서 수정·적용한 부분은
`SOURCE_AUDIT.md`와 `THIRD_PARTY_NOTICES.md`에 기록되어 있으며, 필수 법적
파일은 배포 스킬에도 포함됩니다.
