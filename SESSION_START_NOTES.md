# SESSION_START_NOTES

Updated: 2026-02-23

## 세션 시작 체크
- 먼저 `AGENTS.md`와 `memory.md`를 확인.
- 먼저 `README.md`와 `team/README.md` 확인.
- 실험/논문 중 이번 세션의 1차 목표를 명확히 고른다:
  - method/evidence
  - paper-quality iteration
- 환경 미설정 시:
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `python -m pip install -r requirements.txt`
  - `python -m pip install -e .`

## 안전 유의사항
- 논문 숫자는 단일 실행보다 multi-seed 결과를 우선 사용한다.
- `paper/versions/vN/`는 immutable 원칙으로 다루고 덮어쓰지 않는다.
- 서버/보안 VM 연동은 `experiments/coordination/` 문서를 단일 기준으로 맞춘다.

## 자주 쓰는 명령
- 단일 평가: `python experiments/evaluate.py --config experiments/configs/ucf_crime.yaml`
- 멀티시드: `python experiments/multi_seed_eval.py --configs ... --seeds 41,42,43 --variants core,full`
- 논문 빌드: `bash scripts/build_paper.sh`

## 세션 종료 전
- 산출물 경로(`outputs/*`, `paper/versions/*`)와 실험 설정(config/seed/variant) 기록
- 다음 실행자가 바로 재현 가능하도록 입력 커맨드 남기기
