# v6 Notes

This snapshot captures the additional-experiments pass requested for stronger validity evidence.

Focus of this version:
- added latency decomposition and stream-capacity experiment in main text
- added event-density stress test to show graceful throughput degradation under dense-event regimes
- added runtime protocol robustness test across resolution and decode length
- added appendix experiments for trigger-threshold sensitivity and calibration overhead/amortization

Build status:
- local TinyTeX compile succeeded (`paper/build/main.pdf`, 21 pages)
- remaining warnings are minor overfull/underfull messages in legacy long lines
