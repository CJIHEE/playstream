# PlayStream 로드맵 (1주)

> 게임 이벤트 실시간 레이크하우스. 목표는 **실측 기반 부하테스트·트러블슈팅 3건**과 신기술 학습이다.
> 진행 규칙: 학습(사용자) → 인프라(사용자 실행, Claude 안내) → 코드(에이전트 작성) → 확인·git(사용자) → 기록
> **git과 서버 접속은 사용자만 한다.** Claude는 명령과 방법을 안내한다.

## 아키텍처

```
[event-generator] (초당 발생량 조절 = 부하 발생기)
        │ produce
        ▼
[Kafka kafka01~03] ──► [Spark Structured Streaming spark01]
        │                   │                     │
        │                   ▼                     ▼
        │            [S3 bronze Parquet]    [PostgreSQL 마트]
        ▼
[Airflow airflow01 (Docker, Celery, Flower)] 누락 검증 · compaction · 마트 적재 · Slack 알림
[Prometheus + Grafana + kafka-exporter] 모니터링
```
FastAPI 수집 API와 Locust는 범위에서 뺐다. 시간이 남으면 추가한다.

## ⭐ 부하테스트·트러블슈팅 3선

| # | 시나리오 | 강의 근거 | 측정 |
|---|---|---|---|
| 1 | 발생량을 단계적으로 늘릴 때 **Kafka Consumer lag 폭증** → 파티션 수, `maxOffsetsPerTrigger` 조정 | Kafka·Spark 강의 | lag, 배치 처리 시간, 처리량 |
| 2 | **Airflow 스케줄러 파싱 부하** (DAG 50개, top-level import·Variable.get·무거운 init) → 개선 | 06-5, 16-5 | `airflow dags report` 파싱 시간, 스케줄러 CPU |
| 3 | **Postgres 적재 병목** (row insert / executemany / COPY Custom Hook) + Pool로 DB 보호 | 09-4·5, 14-2 | 적재 시간, Postgres CPU·커넥션 수 |

## Day 1. 하네스·레포·AWS 점검
- 학습: 강의 02-2, 09-1, 16-1·16-2 / git flow 기초
- [ ] 하네스 반영 (Claude, 승인 완료)
- [ ] (사용자) 프로젝트 폴더 `git init`, `.gitignore` 확인, 첫 커밋, `develop` 브랜치 생성
- [ ] (사용자) GitHub private 레포 생성 → 연결 → push, `main` 브랜치 보호 규칙
- [ ] (사용자) 기존 EC2 상태 확인 (이름, 유형, OS, 상태) → infra-navigator와 재활용 점검
- [ ] (사용자) AWS Budgets 예산 알림
- 🤖 `de-tutor`(Day 1 퀴즈), `infra-navigator`(EC2 점검 안내), `/git-handoff`(첫 커밋 안내)
- 완료 기준: GitHub에 main·develop 브랜치가 있고, 기존 인스턴스의 재활용 가능 여부가 정리됨

## Day 2. 수집 — Kafka
- 학습: datalake `kafka-producer` 복습 (acks, idempotence, compression, 키와 파티션)
- [ ] (사용자) kafka01~03 기동, 클러스터 상태 확인, 토픽 `game.events.raw` 생성 (파티션·복제 수 근거 기록)
- [ ] (에이전트) `kafka-engineer`: `services/event-generator` — 이벤트 생성 + 초당 발생량 옵션
- [ ] (사용자) spark01 또는 별도 서버에서 생성기 실행 → console-consumer로 확인
- 🤖 `kafka-engineer` → `code-reviewer` → `pr-explainer` → `de-tutor` 퀴즈 → `/git-handoff`
- 완료 기준: 초당 N건으로 이벤트가 Kafka에 쌓이는 것을 확인

## Day 3. 처리 — Spark Structured Streaming
- 학습: datalake `pyspark-apps` (BaseStreamApp, foreachBatch), checkpoint, watermark
- [ ] (사용자) spark01 기동, S3 버킷과 IAM 권한, Postgres 준비
- [ ] (에이전트) `spark-engineer`: Kafka → S3 bronze (dt/hour 파티션), 1분 집계 → Postgres (멱등 적재)
- [ ] (사용자) `spark-submit` 실행, 결과 확인
- 완료 기준: S3에 파일이 생기고 집계 테이블이 1분 단위로 갱신됨

## Day 4. 오케스트레이션 — Airflow
- 학습: 강의 05, 07, 09, 10, 11, 13 (`docs/study/lecture-index.md` 참고)
- [ ] (에이전트) `infra-engineer`: airflow01용 compose (2.x 최신 버전 고정, Celery, Flower, 커스텀 이미지)
- [ ] (사용자) airflow01 기동, Connection·Variable 등록 (Postgres, Slack, AWS)
- [ ] (에이전트) `airflow-engineer`:
  - `dag_dq_missing_check`: Kafka 적재 건수와 S3·Postgres 건수 비교, 누락 시 Slack 알림 (07 분기, 13 콜백)
  - `dag_compaction`: S3 파티션 도착 감지(10 reschedule 모드) → small files 병합 → Dataset 발행 (11)
  - `dag_mart_load`: Dataset 구독 → COPY 기반 Custom Hook으로 마트 적재 (09), Pool 적용 (14)
- 완료 기준: 누락을 일부러 만들면 Slack 알림이 오고, 재실행해도 결과가 같음 (멱등)

## Day 5. 모니터링
- 학습: 강의 14, 15, 16-3·16-4
- [ ] (에이전트) `infra-engineer`: Prometheus·Grafana·kafka-exporter·node-exporter 설정, 대시보드
- [ ] (에이전트) `loadtest-engineer`: Prometheus 지표 → CSV 추출 스크립트
- [ ] (사용자) 설치, 대시보드 확인
- 완료 기준: lag, 처리량, 배치 시간, CPU·메모리를 파일로 남길 수 있음 (**이 단계가 끝나야 Day 6 시작**)

## Day 6. 부하테스트·트러블슈팅
- 학습: 강의 16-5, Kafka·Spark 튜닝 자료
- [ ] (에이전트) `loadtest-engineer`: 시나리오 3개 설계 (가설, 부하 프로파일, 한 번에 변수 하나만 변경, 종료 조건)
- [ ] (사용자) 시나리오별 before 측정 → 개선 → after 측정 (각 2~3회 반복)
- [ ] (에이전트) 개선 코드는 해당 구현 에이전트가 작성
- 완료 기준: `loadtest/results/` 아래 시나리오별 before/after 원본 파일

## Day 7. 포트폴리오
- [ ] `/troubleshoot-report` 3건
- [ ] README: 아키텍처 → 핵심 수치(근거 파일) → 트러블슈팅 3선 → AI 활용 방식
- [ ] 이력서 문장, 예상 면접 질문
- [ ] (사용자) `release` → `main` 머지, **EC2 stop**

---

## git flow (사용자 실행, 자세한 명령은 `/git-handoff`)
```
main ─────────────────────────────●──────── (Day 7 release 머지)
develop ──●─────●─────●─────●─────┘
           \   / \   / \   /
feature/day2-generator  feature/day3-streaming ...
```
- 태스크 하나 = `feature/day<N>-<주제>` 브랜치 하나 = PR 하나 (base: develop)

## 🤖 AI 활용 트랙

### 태스크마다 반복하는 에이전트 사이클
| 순서 | 에이전트 / 스킬 | 시점 |
|---|---|---|
| ① | `project-planner` | 태스크 카드 → 사용자 승인 → 사용자가 feature 브랜치 생성 |
| ② | `/study` → `de-tutor` | 학습 |
| ③ | `infra-navigator` | 서버 작업 안내 (사용자 실행), 에러 진단 |
| ④ | 구현 에이전트 | 로컬에서 코드 작성 (영역이 다르면 병렬) |
| ⑤ | `code-reviewer` | 🔴 있으면 재작업 |
| ⑥ | 메인 세션 + `pr-explainer` | 변경 전/후 공개, 리뷰 가이드 → 사용자 확인 |
| ⑦ | `de-tutor` 퀴즈 | 꼬리질문 3개에 **내 말로** 답변 |
| ⑧ | `/git-handoff` | 사용자가 commit → push → PR → merge |
| ⑨ | `change_log`, `docs/ai-log/` | 기록 |

### 단계별 AI 역량 목표
| Day | 익힐 AI 활용 기술 | 산출물 |
|---|---|---|
| 1 | 하네스 설계: 권한(allow/ask/deny), 훅, 에이전트·스킬 구조 | `.claude/` 구조 설명 |
| 2 | 태스크 명세 작성: 목표·제약·완료 기준을 줘서 한 번에 원하는 결과 얻기 | 요청 원문과 다듬은 요청 비교 |
| 3 | 컨텍스트 관리: 필요한 파일만 지정, 서브에이전트에 위임 | 세션 운영 메모 |
| 4 | AI 코드 비판적 리뷰: 에이전트 코드의 버그·과잉 설계 찾기 | 리뷰에서 찾은 AI 오류 목록 |
| 5 | AI로 지표·로그 해석 → 직접 검증 | 가설과 검증 결과 |
| 6 | 환각 검증: AI 추정과 실측 비교 | "AI 추정 vs 실측" 표 |
| 7 | 하네스 개선 회고 | README "AI 활용 방식" 섹션 |

### ai-log 템플릿: `docs/ai-log/YYYY-MM-DD-<태스크>.md`
```
- 태스크:
- 사용한 에이전트·스킬:
- 효과가 좋았던 요청 (원문):
- AI가 틀렸거나 과했던 것 → 내가 어떻게 잡았나:
- 하네스 개선 (있으면):
- 소요 시간 체감:
```
