WER request: dots.tts NFE sweeps (from Atharv)

clips/      972 generated clips: 2 runs x 54 prompts x 9 NFE values (4-32), 48 kHz mono WAV.
            Named <run_id>__<prompt_id>__nfe<N>.wav. Unchanged copies of the WAVs in the watai_exp repo.
clips.csv   one row per clip: file, run_id, prompt_id, nfe, length, content, text (what the clip
            should say), repo_path (same clip inside watai_exp), and an empty wer column.

Runs:
  xvector_4090  experiments/nfe_benchmark_runs/nfe_54_prompts_v1_full_xvector_part_0 and _part_1
  orig_3090     experiments/nfe_benchmark_runs/nfe_54_prompts_v1_full_part_0 and _part_1

What I need back: clips.csv with the wer column filled in (0-1, per clip). If easy, also add
columns for the ASR transcript and CER. Please tell me the ASR model/version and the text
normalization used.

Notes:
- 4 clips are silent: orig_3090 p036 NFE 6; p018, p034, p045 NFE 8. Please keep them in
  (WER 1.0) rather than dropping them.
- Every orig_3090 clip is exactly 9.12 s (the length cap), so its endings may be cut off.
