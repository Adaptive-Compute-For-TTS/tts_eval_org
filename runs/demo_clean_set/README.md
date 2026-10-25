# Demo WER/CER (task #9)

ASR quality scores for Nick's clean set (task #8): 12 prompts × NFE 4/20/32 = 36 WAVs from the archived
RTX 4090 x-vector run. The 8 demo-set prompts are included. Scored twice, with one file per ASR model
(never mix or compare WER across models):

- **Whisper `large-v3`** — the model Nick used for task #8, so his selection and these scores agree. **Use this
  one for the dashboard.**
- **Whisper `small`** — the model of the earlier 972-clip benchmark, for comparison with past results.

Both use the same settings: faster-whisper, int8, CPU, English, beam 5, temperature 0.

## Files

| File | What it is |
|---|---|
| `wer_cer_demo_large-v3.json` | **The deliverable (large-v3).** One entry per WAV, keyed `run_id__prompt_id__nfe`, plus corpus totals and totals by NFE |
| `wer_cer_demo_small.json` | Same format, Whisper small |
| `transcripts_large-v3.jsonl`, `transcripts_small.jsonl` | Whisper transcripts, keyed by the WAV's SHA-256 (re-scoring never re-transcribes) |
| `manifest.csv` | Input: `audio_path, text, prompt_id, nfe` (+ category, length bucket, Nick's file name) |
| `nick_clean_set_manifest.csv`, `nick_asr_scores_large_v3.csv` | Nick's files, copied unchanged from `watai_exp/experiments/clean_samples/` |

The 36 WAVs are byte-identical to `runs/nfe_benchmark/clips/xvector_4090__<prompt>__nfe<N>.wav` (checked by git
blob hash against Nick's repo), so `manifest.csv` points there.

## Results

Corpus totals (word errors / reference words). 0 invalid clips with either model.

| | large-v3 WER | large-v3 CER | small WER | small CER | Nick large-v3 WER |
|---|---|---|---|---|---|
| All 36 clips | **0.0000** (0/417) | **0.0000** | 0.0192 (8/417) | 0.0107 | 0.0024 (1/417) |
| NFE 4 | 0.0000 (0/139) | 0.0000 | 0.0288 (4/139) | 0.0141 | 0.0072 (1/139) |
| NFE 20 | 0.0000 (0/139) | 0.0000 | 0.0216 (3/139) | 0.0141 | 0.0000 |
| NFE 32 | 0.0000 (0/139) | 0.0000 | 0.0072 (1/139) | 0.0038 | 0.0000 |
| 8 demo-set prompts (24 clips) | 0.0000 (0/204) | 0.0000 | 0.0000 (0/204) | 0.0000 | 0.0000 |

large-v3 is 0 in every group: short and medium prompts, and all six categories (plain, numbers, names/rare
words, acronyms, prosody, phonetic). No clip has a missing ending, a leaked intro or a rejection.

**Why small has errors:** all 8 are on **p023** ("Gewürztraminer", "Aoife"): small hears "Govert's Traminer" /
"Govots tramina" and "Ifa". large-v3 hears both names correctly at every NFE, so these are ASR errors on rare
names, not TTS errors. **No NFE effect:** with large-v3 every NFE is 0, and small's trend comes only from p023.
The earlier 324-clip clean benchmark also found no measurable NFE effect (permutation test p = 0.78).

**Agreement with Nick (task #8):** same word-error count on 35/36 clips. The one difference is p023 NFE 4, where
Nick's run heard "Ife" for "Aoife" (1 error) and ours heard "Aoife" (0). 32/36 transcripts are character-for-character
identical; of the other 4, three differ only in commas or capitals (removed by normalization) and the fourth is
that p023 clip. Small
differences are expected: same model weights, but our run uses faster-whisper (CTranslate2, int8, beam 5) and
Nick's used Hugging Face transformers (greedy).

**Checks:** the small run reproduces the earlier benchmark (`clips_arush.csv`) exactly on 36/36 clips
(transcripts and WER/CER); corpus totals of both files recomputed independently from the per-clip counts.

**Cost on this laptop (M2, 8 GB, CPU):** small ~1.6 s/clip, peak RAM ~0.9 GB; large-v3 ~11 s/clip, peak RAM
2.1 GB, model download ~3 GB.

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

From `tts_eval/` (needs `pip install -r requirements.txt`; CPU only; the first run of each model downloads it:
small ~0.5 GB, large-v3 ~3 GB. On a CUDA GPU large-v3 would be much faster, but that changes the ASR settings,
so it would need its own output file):

```bash
.venv/bin/python score_demo.py --manifest runs/demo_clean_set/manifest.csv --run-id xvector_4090 \
    --asr-model large-v3 --out runs/demo_clean_set/wer_cer_demo_large-v3.json
.venv/bin/python score_demo.py --manifest runs/demo_clean_set/manifest.csv --run-id xvector_4090 \
    --out runs/demo_clean_set/wer_cer_demo_small.json            # default model: small

# one new WAV after a live generation (adds or replaces its entry in the JSON)
.venv/bin/python score_demo.py --wav out.wav --text "The kettle is already on the stove." \
    --run-id <run_id> --prompt-id p001 --nfe 20 --asr-model large-v3 --out wer_cer_large-v3.json
```
