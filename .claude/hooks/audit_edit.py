"""PostToolUse 훅: Edit/Write/NotebookEdit 가 실행될 때마다 logs/edit_audit.jsonl 에 자동 기록한다.

왜 필요한가:
    규칙 3(이력 기록)은 CLAUDE.md '지시'에만 의존하면 Claude 가 빠뜨릴 수 있다.
    이 훅은 하네스가 직접 실행하므로, 모든 파일 수정이 기계적으로 남는다.
    사람이 읽는 요약 로그는 태스크 단위의 logs/change_log.md, 원본 감사 기록은 이 파일이 담당한다.
    code-reviewer 는 이 파일로 "이번 태스크에서 바뀐 파일"을 찾는다 (git 을 쓰지 않기 때문).
"""
import datetime
import json
import os
import sys

MAX_CHARS = 2000  # 로그가 과도하게 커지지 않도록 변경 내용은 앞부분만 저장


def main() -> None:
    data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    tool_input = data.get("tool_input") or {}
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    record = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "tool": data.get("tool_name"),
        "file": tool_input.get("file_path") or tool_input.get("notebook_path"),
        "session": data.get("session_id"),
        "agent": data.get("agent_type") or data.get("subagent_type") or "main",
        "old": (tool_input.get("old_string") or "")[:MAX_CHARS],
        "new": (tool_input.get("new_string") or tool_input.get("content")
                or tool_input.get("new_source") or "")[:MAX_CHARS],
    }

    log_dir = os.path.join(project_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "edit_audit.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
