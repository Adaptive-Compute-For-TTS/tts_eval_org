# tts_eval: WER/CER scoring for dots.tts

## Critical Rules

- Never modify input data: `runs/nfe_benchmark/clips.csv`, any `.wav`, `runs/human_arush/`, `runs/demo_clean_set/clips/`
- Never delete a transcript cache (`asr_progress*.jsonl`, `transcripts_*.jsonl`). When the ASR model changes, use a new file name
- Never compare or mix WER across ASR models. Every output records its model; one output file per model
- Never write a normalization rule that turns a wrong word into a right one. Format-only rules, each with a unit test
- Report corpus WER/CER (total errors / total reference words), never the mean of per-clip values. Never cap corpus numbers
- Silent or rejected clips stay in the output with WER = CER = 1.0 and `valid: false`. Never drop them
- Test on 2-3 clips (`--limit`) before any full run and show Arush the results
- Never download a Whisper model or a large file without asking (disk has ~7 GB free)
- Commit or push only when asked. No Co-Authored-By or any Claude/Anthropic trailer

## Commands

- Run from `~/dots_WER_analysis/tts_eval` with `.venv/bin/python` (Python 3.11). Not system `python3`
- Tests: `.venv/bin/python -m pytest -q`
- Demo scoring, batch: `.venv/bin/python score_demo.py --manifest <manifest.csv> --run-id <run_id> --out <json>`
- Demo scoring, one WAV: `.venv/bin/python score_demo.py --wav <f.wav> --text "<prompt>" --run-id <id> --prompt-id <pNNN> --nfe <n> --out <json>`
- Old 972-clip benchmark: `.venv/bin/python score_clips.py runs/nfe_benchmark/clips.csv --official no_intro [--limit N]`
- Debug a mismatch: `.venv/bin/python metrics.py "<reference>" "<transcript>"`

## Architecture

- `asr.py`: `load_audio`, `check_audio` (rejects < 0.5 s or RMS < 1e-3), `ASR_SETTINGS` (Whisper small, int8, CPU, en, beam 5, temp 0)
- `metrics.py`: `normalize`, `compute_wer`, `wer_cer`, `corpus_wer`, `sim`
- `score_clips.py`: `transcribe_audio`, `score_clip` (full + no_intro versions), `corpus_cer`. Shared by all scripts
- `score_demo.py`: demo task #9. WAV(s) to one JSON keyed `run_id__prompt_id__nfe`
- `sample_eval/run_eval.py`: self-checking 8-clip eval for the backend team's infra
- `runs/nfe_benchmark/`: old 972-clip benchmark + `deliverables/`. `runs/demo_clean_set/`: demo #9 inputs + `wer_cer_demo_small.json` (see its README)
- `prompts/benchmark_prompts_v1.json`: Eric's 54 prompts (p001-p054)

## Code Style

- Reuse `score_clip()` / `transcribe_audio()`. Don't write new WER/CER logic
- No new dependencies without asking
- Official version is `no_intro`. Uncapped values everywhere in demo output

## Git

- `git push` goes to personal (`arushatre/tts_eval`); `git push origin` goes to the org (`tts_eval_org`). Never `git push -u origin main`
- Single-line commit messages, lowercase, no period

## Context

- Read `notes.md` at session start: current task, decisions, gotchas. Update it before ending a session
- Full history and past results: `../HANDOFF.md`. Read only when needed
