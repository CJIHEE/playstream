# 강의 색인 (Airflow 강의자료 01~17장)

> 강의자료 PDF 79개의 텍스트를 읽고 정리한 색인이다. 에이전트는 강의 내용을 말할 때 이 문서를 근거로 삼는다.
> 강의 환경: **Airflow 2.5.x** (`apache/airflow:2.5.1~2.5.2`), 공식 docker-compose, **CeleryExecutor**, WSL, Postgres 13
> ⚠️ PDF에 "vscode에서…"로만 적힌 실습 코드는 슬라이드에 없다 (강의 영상에서만 나옴).

## 챕터별 핵심과 PlayStream 사용처

| 장 | 핵심 내용 | PlayStream 사용처 |
|---|---|---|
| 01 소개 | DAG·Task, Cron 스케줄, **단점: 실시간 부적합 (최소 분 단위)** | 실시간은 Kafka·Spark, 배치·관리는 Airflow로 나누는 이유 (면접 포인트) |
| 02 설치 | Docker vs VM, 공식 compose 설치, 권장 사양 **16GB (최소 8GB)**, pip 설치는 한 번에 Task 1개만 실행 | airflow01 EC2 사양 근거 |
| 03 오퍼레이터 기본 | Operator와 Task, **스케줄러는 파싱, 워커는 실행**, Cron, `>>` 연결, 외부 쉘(볼륨 마운트), Email | DAG 기본 구조 |
| 04 Python 오퍼레이터 | PythonOperator, **plugins 폴더 sys.path 자동 추가**, `@task`, op_args/op_kwargs | `airflow/plugins/common/` 구조 |
| 05 Template | Jinja, **data_interval_start/end (논리적 기준일)**, ds·ts, macro와 relativedelta | **멱등성**: 재실행해도 같은 구간 처리 (`datetime.now()` 금지 근거) |
| 06 데이터 공유 | XCom (메타DB 저장, **소용량 전용, 대용량은 S3**), Variable (**top-level Variable.get은 스케줄러 부하 유발**) | 건수만 XCom, 데이터는 S3/Postgres |
| 07 Task 고급 | Branch 3종, **Trigger Rule 11종**, Task Group, Edge Label | DQ 결과에 따라 정상 / 재처리 / 알림 분기 |
| 08 More 오퍼레이터 | BaseOperator 표, **TriggerDagRun과 ExternalTask 센서 비교**, run_id, SimpleHttp + Connection, **Variable로 API 키 마스킹**, CustomOperator (`template_fields`, `execute`) | 커스텀 오퍼레이터 |
| 09 Connection & Hook | compose 해석 (x-airflow-common, volumes, **network_custom 고정 IP**), Hook (접속정보 노출 방지), **bulk_load 한계 (Tab 고정, 헤더 포함, 특수문자 오류)** → Custom Hook, 이미지 Extend (Dockerfile) | 마트 적재 COPY Hook (**트러블슈팅 3**) |
| 10 Sensor | poke(), **poke vs reschedule (Slot 점유 차이)**, Pool·Slot, File / Python / ExternalTask 센서, Custom 센서 | S3 파티션 감지 → compaction |
| 11 기능 더보기 | **Dataset (pub/sub 약한 연결)**, default_args vs DAG 파라미터, 실패 email, **SLA 제약 3가지**, **sla / execution_timeout / dagrun_timeout 비교**, CLI (trigger / **backfill** / clear), **Triggerer·Deferrable** | compaction → 마트 적재를 Dataset으로 연결 |
| 12 Rshiny | 커스텀 이미지·컨테이너로 대시보드 | (대체) Grafana |
| 13 메신저 연동 | **Slack Incoming Webhook Connection**, `on_failure_callback` (plugins/config), 카카오 (토큰 6시간 만료), **sla_miss_callback은 묶음 호출** | 실패·누락 Slack 알림 |
| 14 관리 | **메타DB 주요 테이블** (dag_run, task_instance, sla_miss 등), **Pool: 대상 DB 보호용으로 일부러 작게** (pool_slots, priority_weight, weight_rule), Role | Postgres 보호 Pool (**트러블슈팅 3**) |
| 15 모니터링 | dag·dag_run으로 **수행 중 / 성공 / 실패 / 미수행(누락)** 쿼리, Slack Block, Email HTML | Airflow 수행 현황 리포트 |
| 16 아키텍처 | Executor 4종, Celery 노드 분산 조건 (같은 cfg, 같은 DAG 소스), MWAA, **Flower** (`--profile flower`), **parallelism · worker_concurrency · max_active_*** 공식, **스케줄러 부하 줄이기** (import는 callable 안으로, init 경량화, Variable은 템플릿으로, 파싱 파라미터, SSD, **PGBouncer**) | **트러블슈팅 2의 근거** |
| 17 chatGPT | GPT API 옵션 (role, temperature, n), pykrx, 블로그 자동 포스팅 | 범위 밖 |

## 강의에서 바로 나오는 부하·트러블슈팅 소재

| 소재 | 강의 근거 | 측정 방법 |
|---|---|---|
| DAG 파싱 부하 (top-level import, Variable.get, 무거운 init) | 06-5, 16-5 | `airflow dags report` 파싱 시간, 스케줄러 CPU |
| poke vs reschedule 센서의 Slot 점유 | 10-1, 14-2 | 센서 N개 동시 실행 시 Pool 점유, 대기 Task 수 |
| Pool로 대상 DB 보호 | 14-2 | slot 수별 Postgres 커넥션·CPU·총 소요 시간 |
| bulk_load 한계 → Custom Hook(COPY) | 09-4, 09-5 | 같은 건수 적재 시간: insert / executemany / COPY |
| backfill 몰림 | 11-6, 16-4 | `max_active_runs` 값별 완료 시간, 스케줄러 지연 |
| parallelism · worker_concurrency 병목 | 16-4 | 동시 Task 수와 대기열 (Flower) |

## 버전 메모
- 강의는 Airflow 2.5 기준이다. Airflow 3.x는 **SLA 제거** 등 강의 문법과 다른 부분이 있으므로 **Airflow 2.x 최신 버전**으로 고정한다 (정확한 버전은 Day 4 설치 시 결정하고 근거 기록).
- 최신 HTTP provider에서는 `SimpleHttpOperator`가 `HttpOperator`로 바뀌었으므로 설치 버전 문서를 확인한다.
