# Demo WER/CER (task #9)

ASR quality scores for Nick's clean set (task #8): 12 prompts × NFE 4/20/32 = 36 WAVs from the archived
RTX 4090 x-vector run. The 8 demo-set prompts are included. ASR: Whisper `small` (int8, CPU, English, beam 5,
temperature 0), the same model and settings as the earlier 972-clip benchmark.

## Files

| File | What it is |
|---|---|
| `wer_cer_demo_small.json` | **The deliverable.** One entry per WAV, keyed `run_id__prompt_id__nfe`, plus corpus totals and totals by NFE |
| `transcripts_small.jsonl` | Whisper transcripts, keyed by the WAV's SHA-256 (re-scoring never re-transcribes) |
| `manifest.csv` | Input: `audio_path, text, prompt_id, nfe` (+ category, length bucket, Nick's file name) |
| `nick_clean_set_manifest.csv`, `nick_asr_scores_large_v3.csv` | Nick's files, copied unchanged from `watai_exp/experiments/clean_samples/` |

The 36 WAVs are byte-identical to `runs/nfe_benchmark/clips/xvector_4090__<prompt>__nfe<N>.wav` (checked by git
blob hash against Nick's repo), so `manifest.csv` points there.

## Results (Whisper small)

| | Word errors / words | WER | CER |
|---|---|---|---|
| All 36 clips | 8 / 417 | 0.0192 | 0.0107 |
| NFE 4 | 4 / 139 | 0.0288 | 0.0141 |
| NFE 20 | 3 / 139 | 0.0216 | 0.0141 |
| NFE 32 | 1 / 139 | 0.0072 | 0.0038 |
| 8 demo-set prompts (24 clips) | 0 / 204 | 0.0000 | 0.0000 |

All 8 errors are on **p023** ("Gewürztraminer", "Aoife"): Whisper small hears "Govert's Traminer" and "Ifa".
Nick's Whisper large-v3 makes 1 error on the same 36 clips (also p023, NFE 4). These are ASR errors on rare names,
not TTS errors, so **the NFE trend above is not evidence that NFE changes quality**. The earlier 324-clip clean
benchmark found no measurable NFE effect (permutation test p = 0.78).

Checks: transcripts and WER/CER identical to the earlier benchmark (`clips_arush.csv`) on 36/36 clips; corpus
totals recomputed independently; 0 invalid clips.

## JSON format (one entry)

```json
"xvector_4090__p001__nfe4": {
  "run_id": "xvector_4090", "prompt_id": "p001", "nfe": 4,
  "audio": "...wav", "audio_sha256": "...", "reference_text": "...", "transcript": "...",
  "asr_status": "ok", "valid": true, "flags": [], "duration_s": 2.72,
  "wer": 0.0, "cer": 0.0, "word_errors": 0, "ref_words": 7, "subs": 0, "dels": 0, "ins": 0,
  "char_errors": 0, "ref_chars": 34, "missing_end_words": 0, "intro_text": ""
}
```

- `wer` / `cer` are uncapped (insertions can push them above 1.0). Official scoring version `no_intro`.
- `valid: false` means the clip was silent or shorter than 0.5 s; it stays in with WER = CER = 1.0.
- `flags` can contain the rejection reason and `intro_detected` (a leaked "Hey, Adam here…" reference intro,
  set aside before scoring).
- To combine clips, use `word_errors / ref_words` totals (as in `corpus` and `by_nfe`), not the mean of `wer`.

## Reproduce / score new WAVs

From `tts_eval/` (needs `pip install -r requirements.txt`; CPU only, first run downloads Whisper small, ~0.5 GB):

```bash
.venv/bin/python score_demo.py --manifest runs/demo_clean_set/manifest.csv --run-id xvector_4090 \
    --out runs/demo_clean_set/wer_cer_demo_small.json

# one new WAV after a live generation (adds or replaces its entry in the JSON)
.venv/bin/python score_demo.py --wav out.wav --text "The kettle is already on the stove." \
    --run-id <run_id> --prompt-id p001 --nfe 20 --out wer_cer.json
```
