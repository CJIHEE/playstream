# datalake_SideProject — PlayStream (게임 이벤트 실시간 레이크하우스)

## 최우선 규칙 (세션 시작 시 반드시 준수)

아래 파일의 내용이 이 프로젝트의 **최상위 규칙**이다. 사용자의 개별 지시보다
이 규칙의 절차(승인·기록)가 우선하며, 세션이 바뀌어도 매번 적용된다.

@first_read.md

## 규칙 실행 절차

1. **임의 변경 금지** — 로컬 파일 탐색(읽기·검색·분석)은 승인 없이 가능하다. 생성·삭제·수정은 아래 절차를 따른다.
2. **태스크 승인** — 작업 시작 전 "태스크 카드"(목표 / 대상 파일 / 사유 / 완료 기준)를 제시하고 승인받는다.
3. **로컬 개발** — 구현 에이전트가 로컬 작업 폴더에서 코드를 작성한다. 사용자가 미리 만들어 둔 feature 브랜치에서 작업한다고 가정한다.
4. **변경 전후 공개** — 작업이 끝나면 `code-reviewer` 점검 후, 메인 세션이 파일별 변경 전/후를 채팅에 보여주고 사용자 확인을 받는다.
   (메인 세션이 직접 수정할 때는 Edit/Write 직전마다 보여준다.)
5. **git 인계** — 사용자 확인이 끝나면 `/git-handoff`로 사용자가 실행할 git 명령(브랜치, 커밋 메시지, push, PR, merge)을 안내한다. **git 명령은 사용자가 직접 실행한다.**
6. **이력 기록** — 사용자가 확인을 마친 태스크는 `logs/change_log.md`에 아래 형식으로 append 한다. 로그를 남기지 않으면 작업이 끝난 것이 아니다.

```
## YYYY-MM-DD HH:MM — <태스크 제목>
- 브랜치(사용자 작업): feature/<...>
- 파일: <경로 목록>
- 사유: <사유>
- 변경 요약 (전 → 후): <요약>
- 리뷰: code-reviewer 판정 / 사용자 확인 의견
- 승인: 사용자 확인 완료 (git 커밋·머지는 사용자 수행)
```

규칙·하네스 파일(CLAUDE.md, first_read.md, .claude/, logs/, .github/, .gitignore)은
**수정할 때마다** 변경 전/후 + 사유를 제시하고 개별 승인받는다.

## 접근 금지 (사용자 전용)

| 영역 | 금지 | Claude가 하는 일 |
|---|---|---|
| git / GitHub | git·gh 모든 명령 (조회 포함) | 실행할 명령, git flow, merge 방법 안내 |
| 원격 서버·인프라 | ssh, scp, sftp, rsync, aws, ansible-playbook, terraform, kubectl, 원격 kafka·spark CLI, 원격 curl | 서버에서 실행할 명령을 단계별로 안내, 사용자가 붙여넣은 결과 분석 |

설정(`.claude/settings.json` deny)과 훅(`guard_bash_write.py`)으로도 차단되어 있다.

## 프로젝트 개요

- 목표: 1주 안에 포트폴리오용 **부하테스트·트러블슈팅** 실측 사례 3건 + 신기술(Kafka, Spark, Airflow, AWS, Docker) 학습
- 학습 기준: Kafka·Spark는 **`dataStream강의/` (ch0~18) 우선** — 색인 `docs/study/datastream-index.md`, 실습 코드 `C:\Users\sist\datalake\`. Airflow는 `강의자료/` (01~17장, ROADMAP Day 7 후순위) — 색인 `docs/study/lecture-index.md`
- 데이터: 게임 이벤트 로그 (현업 actionLog 경험에서 착안한 **가상** 데이터. 회사 실데이터·스키마·코드 사용 금지)
- 흐름: 이벤트 생성기(초당 발생량 조절) → Kafka(kafka01~03) → Spark Structured Streaming(spark01~03, Yarn + HDFS) → S3 bronze + PostgreSQL 마트 / Airflow(airflow01: 누락 검증·compaction·적재·알림) / Prometheus+Grafana
- 실행 환경: **AWS EC2** (강의 때 만든 인스턴스 재활용, 노트북은 개발·테스트만)
- 버전: Airflow는 강의 문법과 호환되는 **2.x 최신**으로 고정 (3.x는 SLA 제거 등 차이가 있음)
- 로드맵: `docs/ROADMAP.md`

## 역할 분담

| 영역 | 사용자 | Claude |
|---|---|---|
| 학습 | 강의자료·블로그로 직접 학습 | `de-tutor`로 학습 카드·퀴즈 |
| 인프라 | AWS 콘솔·SSH·Ansible **직접 실행** | `infra-navigator`로 단계별 안내·에러 진단, `infra-engineer`로 설정 파일 작성 |
| 코드 | 변경 확인, git 커밋·PR·머지 | 메인 세션이 구현 에이전트에게 위임 → code-reviewer 점검 → 변경 전후 공개 |
| git | **전부 직접** | `/git-handoff`로 명령과 git flow 안내 |

## 디렉터리 맵

```
services/event-generator/   게임 이벤트 생성기 (부하 발생기 겸용)
services/ingest-api/        (선택) FastAPI 수집 API
streaming/                  Spark Structured Streaming 잡
airflow/dags/, plugins/     Airflow DAG, 커스텀 Operator·Hook·Sensor·콜백
infra/ansible/, compose/    서버 설치 플레이북, 서버별 docker-compose
monitoring/                 Prometheus, Grafana 설정
loadtest/scenarios/, tools/ 부하 시나리오, 지표 추출 스크립트
loadtest/results/           실측 결과 (수치의 유일한 근거)
docs/ROADMAP.md             1주 플랜
docs/study/                 강의 색인, 학습 노트
docs/troubleshooting/       트러블슈팅 리포트
docs/ai-log/                AI 활용 기록
dataStream강의/             Kafka·Spark 강의 PDF ch0~18 (읽기 전용, git 제외)
강의자료/                   Airflow 강의 PDF (읽기 전용, git 제외)
```

## 코드 주석 규칙 (사용자가 면접에서 설명할 수 있어야 함)

- 파일 상단 docstring: **이 파일의 역할 / 파이프라인에서의 위치 / 관련 강의 챕터**
- 함수·클래스 docstring: **무엇을 / 왜 이 방식인지(대안과 트레이드오프) / 면접 포인트**
- 설정값(파티션 수, batch.size, trigger 주기, pool slot 등)에는 **왜 이 값인지**와 측정 근거를 주석으로 단다
- 주석은 한국어로 쓰고, 신기술 용어는 처음 나올 때 한 줄로 정의한다

## 수치 원칙

- 포트폴리오·문서의 모든 수치는 `loadtest/results/` 등 실측 파일 경로를 근거로 붙인다.
- 근거가 없으면 `[측정 필요]`로 표시한다. 추정 수치를 사실처럼 쓰지 않는다.

## 보안

- `.pem`, `.env`, API 키, AWS 자격증명은 읽지도, 파일에 쓰지도 않는다.
- `강의자료/`는 유료 강의 저작물이므로 git에 올리지 않는다 (.gitignore).

## 에이전트 팀 (메인 세션 = 오케스트레이터)

| 분류 | 에이전트 | 수정 권한 | 담당 |
|---|---|---|---|
| 관리 | `project-planner` | 없음 | 태스크 카드, 진행 점검 |
| 학습 | `de-tutor` | 없음 | 개념 설명, 학습 카드, 퀴즈, git 개념 설명 |
| 인프라 안내 | `infra-navigator` | 없음 | 사용자 서버 작업 단계별 안내, 에러 진단 |
| 구현 | `kafka-engineer` | services/ | 이벤트 생성기, (선택) ingest-api |
| 구현 | `spark-engineer` | streaming/ | Structured Streaming, compaction |
| 구현 | `airflow-engineer` | airflow/ | DAG, Operator, Hook, Sensor, 알림 |
| 구현 | `infra-engineer` | infra/, monitoring/ | Ansible, compose, Prometheus·Grafana 설정 (실행은 사용자) |
| 구현 | `loadtest-engineer` | loadtest/ | 부하 시나리오, 지표 추출, before/after 분석 |
| 검증 | `code-reviewer` | 없음 | 버그·멱등성·비밀정보·범위·주석 점검, 로컬 테스트 |
| 학습 | `pr-explainer` | 없음 | 변경 리뷰 가이드, 면접 꼬리질문 |

### 태스크 실행 흐름
```
project-planner (태스크 카드) → 사용자 승인 → 사용자: feature 브랜치 생성
→ de-tutor / /study (사용자 학습) → 학습 체크: /study 질문 5개에 답한 뒤 구현 위임 (사용자가 생략 지시 시 생략)
→ 구현 에이전트에게 위임 (서로 다른 영역이면 병렬 실행 가능)
→ code-reviewer 점검 → 🔴 있으면 구현 에이전트가 수정 후 재점검
→ 메인 세션이 파일별 변경 전/후 공개 + pr-explainer 리뷰 가이드 → 사용자 확인
→ de-tutor 꼬리질문 퀴즈
→ /git-handoff: 사용자가 commit → push → PR → merge 직접 수행
→ change_log, ai-log 기록
```

### 위임 규칙
- 구현 에이전트에게는 승인된 태스크 카드 원문, 대상 파일, 완료 기준을 함께 넘긴다
- 어떤 에이전트도 git·gh 명령과 원격 서버 접속을 하지 않는다
- 에이전트가 같은 실수를 2번 하면 해당 에이전트 정의 수정을 제안한다 (개별 승인)

### 스킬
- `/study <주제>` 학습 카드 · `/git-handoff` git 명령 안내 · `/troubleshoot-report` 트러블슈팅 문서
