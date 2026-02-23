---
title: Event-VLM memory
date_created: 2026-02-23
last_updated: 2026-02-23
tags: [memory, context, Event-VLM]
---

## 1) Project Identity
- Name: Event-VLM
- Mission: 실시간 감시 비디오 이해를 위한 VLM 효율화 방법(Event-VLM-Core/Full) 연구 및 ECCV 2026 제출.
- Primary users: 연구/엔지니어링 팀, 논문 작성 팀.

## 2) Current Product Scope
- 모델/파이프라인 구현: `src/`
- 실험 실행/설정: `experiments/`
- 논문/버전 스냅샷: `paper/`
- 팀 운영 규칙: `team/`
- 교차 환경 동기화: `experiments/coordination/`

## 3) Architecture Snapshot
- 평가 진입점: `experiments/evaluate.py`
- 멀티시드 집계: `experiments/multi_seed_eval.py`
- 논문 빌드: `scripts/build_paper.sh`
- 서버 one-click: `scripts/server_ready_one_click.sh`

## 4) Evidence Policy
- 수치 보고는 config/seed/variant/detector를 항상 명시.
- 산출물 경로(`outputs/*`, `paper/versions/*`)를 Session Log에 함께 기록.
- 단일 실행 수치는 참고값, 제출/결론값은 다중 시드 기준.

## 5) Long-Memory Protocol
1. 세션 시작 시 `memory.md` 확인.
2. 45분/마일스톤마다 재확인.
3. 커밋 전 Session Log 업데이트.
4. 종료 시 blockers + next command 기록.

## 6) Session Log
### 2026-02-23
- Change summary:
  - handoff 메모리 운영 규칙 도입(`AGENTS.md`, `memory.md` 신설).
- Rationale:
  - 새 세션 간 연속성 확보 및 실험/논문 증거 추적성 강화.
- Impact/risk:
  - Impact: 실행자 교체 시 문맥 손실 감소.
  - Risk: 기록 누락 시 문서 신뢰도 하락.
- Validation:
  - 파일 생성 확인.
- Next step:
  - 다음 세션에서 첫 실행 커맨드와 아티팩트 경로를 Session Log에 누적 시작.
