---
name: git-handoff
description: 태스크의 로컬 개발과 사용자 확인이 끝났을 때, 사용자가 직접 실행할 git 명령(브랜치, 커밋, push, PR, merge)을 git flow 방식으로 안내한다. 사용자가 /git-handoff 를 입력하거나 "커밋 어떻게 해", "머지 어떻게 해"라고 물을 때 사용.
---

# /git-handoff

**Claude는 git·gh 명령을 실행하지 않는다.** 아래 내용을 사용자에게 안내만 한다.

## 1. 커밋할 파일 정리
- 이번 태스크에서 바뀐 파일 목록 (메인 세션 기록과 `logs/edit_audit.jsonl` 기준)
- 커밋하면 안 되는 파일 경고: `.pem`, `.env`, `강의자료/`, `logs/edit_audit.jsonl` (.gitignore 대상인지 함께 확인하라고 안내)

## 2. git flow 기준 브랜치
| 브랜치 | 용도 | 만드는 곳 → 합치는 곳 |
|---|---|---|
| `main` | 포트폴리오로 보여줄 안정 버전 | release 브랜치에서 머지 |
| `develop` | 개발 통합 | feature 브랜치에서 머지 |
| `feature/day<N>-<주제>` | 태스크 하나 | develop에서 생성 → develop으로 머지 |
| `release/v0.<N>` | (선택) 하루 작업 마무리 | develop에서 생성 → main과 develop으로 머지 |
| `hotfix/<이슈>` | main 긴급 수정 | main에서 생성 → main과 develop으로 머지 |

## 3. 사용자가 실행할 명령 (VS Code 터미널, 프로젝트 폴더에서)
각 명령에 **무엇을 하는지 한 줄 설명**을 붙여서 아래 순서로 제시한다.

```
git status                          # 바뀐 파일 확인 (빨간색 = 아직 스테이징 안 됨)
git diff                            # 변경 내용 최종 확인
git add <파일 경로들>                # 커밋할 파일만 골라서 스테이징 (git add . 는 비밀파일 위험)
git status                          # 초록색으로 바뀐 파일이 의도한 것만인지 확인
git commit -m "<커밋 메시지>"        # 아래 규칙으로 작성한 메시지
git push -u origin feature/<이름>    # 원격(GitHub)에 브랜치 올리기 (-u: 다음부터 git push만 해도 됨)
```
그다음 GitHub에서 **PR 생성 (base: develop ← compare: feature/...)**, 변경 내용 확인 후 **Merge**.
머지 후 로컬 정리:
```
git switch develop                  # develop으로 이동
git pull                            # 머지된 최신 develop 받기
git branch -d feature/<이름>         # 다 쓴 로컬 브랜치 삭제
```

## 4. 커밋 메시지 규칙
- 형식: `<type>(<영역>): <요약>` 예) `feat(streaming): Kafka → S3 bronze 적재 잡 추가`
- type: feat(기능) / fix(버그) / docs(문서) / refactor / test / chore(설정)
- 본문에 "왜" 바꿨는지 1~2줄

## 5. PR 본문 템플릿 (사용자가 GitHub에 붙여넣기)
```
## 태스크
Day N — <태스크 제목>

## 변경 사유

## 변경 내용
| 파일 | 변경 요약 |

## 리뷰 포인트 (pr-explainer 요약)

## 동작 확인 방법

## 예상 면접 질문
```

## 6. 자주 하는 실수와 복구 방법 (필요할 때 안내)
- 커밋 전 파일을 잘못 add: `git restore --staged <파일>`
- 직전 커밋 메시지 수정 (push 전): `git commit --amend`
- develop에서 실수로 작업함: 커밋 전이면 `git switch -c feature/<이름>`으로 새 브랜치로 옮기기
- 머지 충돌: 충돌 파일의 `<<<<<<<` ~ `>>>>>>>` 구간을 보고 사용자가 선택. Claude는 충돌 내용을 읽고 어느 쪽을 남길지 설명만 한다

## 7. 마무리
사용자가 머지를 마쳤다고 알려주면 `logs/change_log.md`에 태스크 기록을 추가하고(개별 승인), ROADMAP 체크박스 갱신을 제안한다.
