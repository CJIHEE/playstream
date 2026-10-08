"""PreToolUse 훅: Bash/PowerShell 명령을 검사해 (1) 사용자 전용 명령은 차단하고 (2) 파일 쓰기 명령은 승인을 묻는다.

왜 필요한가:
    settings.json 의 permissions 규칙은 "Bash(git *)" 처럼 명령의 앞부분만 비교한다.
    그래서 `cd x && git push`, `cat > a.py`, `sed -i` 같은 명령은 규칙을 피해 갈 수 있다.
    이 훅은 명령 전체를 정규식으로 검사해서 빈틈을 막는다.

규칙:
    DENY (first_read.md 4·5번): git·gh, 원격 접속(ssh/scp/sftp/rsync/aws/ansible/terraform/kubectl/nc/telnet),
                                localhost 가 아닌 주소로의 curl/wget/Invoke-WebRequest
    ASK  (first_read.md 1번):   리디렉션 쓰기, tee, sed -i, PowerShell 쓰기·파일 조작, 파이썬 파일 쓰기

동작:
    stdin 으로 {"tool_name": ..., "tool_input": {"command": ...}} JSON 을 받는다.
    걸리면 결정(deny/ask)을 stdout(JSON)으로 내보내고, 아니면 아무것도 출력하지 않는다.
"""
import json
import re
import sys

# 명령 위치: 문자열 시작 또는 ; & | ( ` $( 줄바꿈 뒤. 경로 안의 단어("git clone" 폴더명 등)는 걸리지 않게 한다.
CMD_START = r"(?:^|[;&|\n(`]|\$\()\s*(?:sudo\s+)?(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"

DENY_PATTERNS = [
    ("git/GitHub 명령 (사용자 전용)", CMD_START + r"(?:git|gh)(?:\.exe)?(?=\s|$)"),
    ("원격 접속 명령 (사용자 전용)",
     CMD_START + r"(?:ssh|scp|sftp|rsync|aws|ansible[\w-]*|terraform|kubectl|nc|ncat|telnet)(?:\.exe)?(?=\s|$)"),
    ("원격 세션 (사용자 전용)", r"\bEnter-PSSession\b|\bInvoke-Command\b[^|;]*-ComputerName"),
]

ASK_PATTERNS = [
    ("리디렉션 쓰기(> / >>)", r"(?<![0-9&=\-<>])>{1,2}(?!&)\s*(?!/dev/null\b|\$null\b)[^\s|&;]"),
    ("tee", r"\btee\b"),
    ("sed -i", r"\bsed\b[^|;]*\s-i"),
    ("PowerShell 쓰기", r"\b(Set-Content|Add-Content|Out-File)\b"),
    ("PowerShell 파일 조작", r"\b(Copy-Item|Rename-Item|Move-Item|Remove-Item|New-Item)\b"),
    ("파이썬 파일 쓰기", r"open\([^)]*['\"][wa]b?\+?\\?['\"]|write_text\(|write_bytes\("),  # \\? : 셸 이스케이프된 따옴표 대응
]

HTTP_CLIENT = CMD_START + r"(?:curl|wget|Invoke-WebRequest|Invoke-RestMethod|iwr|irm)(?:\.exe)?(?=\s|$)"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "[::1]", "0.0.0.0"}


def remote_http(command: str) -> bool:
    """HTTP 클라이언트로 localhost 가 아닌 주소에 접속하는지 확인한다."""
    if not re.search(HTTP_CLIENT, command, re.IGNORECASE):
        return False
    hosts = re.findall(r"https?://([^/:\s'\"]+)", command)
    return any(h.lower() not in LOCAL_HOSTS for h in hosts) or not hosts and "@" in command


def decide(decision: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }))  # ensure_ascii 기본값(True): Windows 콘솔 인코딩 문제 방지


def main() -> None:
    data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    command = (data.get("tool_input") or {}).get("command", "")

    denied = [name for name, p in DENY_PATTERNS if re.search(p, command, re.IGNORECASE)]
    if remote_http(command):
        denied.append("원격 HTTP 접속 (사용자 전용)")
    if denied:
        decide("deny", "first_read.md 4·5번 규칙 위반: " + ", ".join(denied)
               + " — 사용자가 직접 실행하도록 명령을 안내하세요.")
        return

    asked = [name for name, p in ASK_PATTERNS if re.search(p, command)]
    if asked:
        decide("ask", "쓰기 명령 감지: " + ", ".join(asked) + " — 변경 전/후를 확인한 뒤 승인하세요.")


if __name__ == "__main__":
    main()
