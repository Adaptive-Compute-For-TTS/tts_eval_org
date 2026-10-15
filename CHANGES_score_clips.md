
## Full run (2026-10-14)
Ran `caffeinate -i python score_clips.py runs/nfe_benchmark/clips.csv --official no_intro` (Arush's update:
`wer` reported with the intro ignored). All 972 transcribed; Phase 4 checks all passed. Results, intro-source
investigation and the 9.12 s answer are in `runs/nfe_benchmark/deliverables/summary.md`.

## Rescore after STOP POINT 2 review (2026-10-14)
- metrics.py: format-only PRE_RULES for Jan/Mar without dots, door frame, quetzal feather, startup's/start-ups (approved).
- score_clips.py: intro = transcript up to the last EXACT intro match (approved); new columns heard_ref_words,
  heard_errors, wer_heard (official version).
- tests: 86 passing. Rescored from cached transcripts only.
- Fetched watai_exp experiments/my_files/abhi1.wav (approved) into watai_exp_ref/.
- Corpus CER (total char errors / total ref chars) overall, by run_id, nfe and run_id x nfe, both versions:
  in wer_run_info.json ("corpus_cer") and summary.md section 12. Per-clip values unchanged.
