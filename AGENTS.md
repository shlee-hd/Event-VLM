# AGENTS.md

## Repository Working Agreement
- 이 저장소의 handoff 단일 기준은 루트 `memory.md`입니다.
- 세션 시작/진행/종료 시 메모리를 갱신해 다음 세션이 바로 이어받을 수 있게 합니다.

## Mandatory Memory Checkpoints
1. Start checkpoint
- `memory.md`, `README.md`, `team/README.md`를 먼저 읽고 목표를 고정합니다.

2. Periodic checkpoint
- 45분마다 또는 주요 마일스톤마다 `memory.md`를 다시 확인합니다.

3. Pre-commit checkpoint
- 커밋 전에 `memory.md` Session Log에 변경/근거/리스크/다음 액션을 추가합니다.

4. Handoff checkpoint
- 세션 종료 시 다음 실행자가 바로 시작 가능한 수준으로 상태/블로커/정확한 next command를 남깁니다.

## Memory Update Format
- Date (YYYY-MM-DD)
- Change summary (what)
- Rationale (why)
- Impact/risk
- Validation (command + output path)
- Next step

## Priority of Truth
- `memory.md` > 일시적 채팅 맥락.
- 실험 수치/논문 근거는 커맨드와 아티팩트 경로를 함께 기록합니다.

## Technical Guardrails
- 논문 수치 보고는 가능하면 multi-seed 결과를 기준으로 합니다.
- `paper/versions/vN/` 스냅샷은 immutable로 취급하고 덮어쓰지 않습니다.
- 서버/보안 VM 연동 규칙은 `experiments/coordination/*` 문서를 기준으로 유지합니다.
