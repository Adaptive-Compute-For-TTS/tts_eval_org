# tts_eval: WER / CER / SIM scoring for dots.tts

## What this project is
Arush's evaluation scripts for a team research project on dots.tts (a text-to-speech model).
The team studies how the number of sampling steps (NFE) affects speech quality and speed.
These scripts score generated audio: Whisper transcribes each clip, and the transcript is
compared with the text the clip was supposed to say (WER = word error rate, CER = character
error rate). SIM (speaker similarity) is a side experiment.

## Environment
- MacBook Air, 8 GB RAM, no GPU. Everything runs on CPU.
- Always work from this folder (`~/dots_messaround/tts_eval`) with the venv active:
  `source .venv/bin/activate`
- Packages: faster-whisper, jiwer, whisper-normalizer, pandas, soundfile, torch, transformers.
- ASR: faster-whisper `small`, int8, CPU, language en, beam 5, temperature 0 (set in `asr.py`).

## Layout
```
tts_eval/
  asr.py            load_audio(), check_audio() (rejects silent/short), transcribe(), ASR_SETTINGS
  metrics.py        normalize() (PRE_RULES + Whisper normalizer + POST_RULES), compute_wer(),
                    wer_cer(), corpus_wer(), sim()
  quick_score.py    scores Arush's own test recordings in runs/human_arush/audio
  score_clips.py    scores Nick's benchmark: runs/nfe_benchmark/clips.csv + clips/*.wav
  prompts/benchmark_prompts_v1.json   Eric's 54 prompts (p001-p054)
  runs/human_arush/                   Arush's own recordings (do not modify)
  runs/nfe_benchmark/clips.csv        Nick's CSV (do not modify)
  runs/nfe_benchmark/clips/           972 wavs, e.g. orig_3090__p001__nfe4.wav
```

## Data (runs/nfe_benchmark)
- clips.csv: 972 rows = 2 runs (orig_3090, xvector_4090) x 54 prompts x NFE {4,6,8,10,12,16,20,24,32}.
- Columns: file, run_id, prompt_id, nfe, length, content, text, repo_path, wer (empty; we fill it).
- The `file` column matches filenames in clips/. `text` is the expected sentence.
- 4 clips are silent (orig_3090 p036 NFE 6; p018, p034, p045 NFE 8). They must stay in the output
  with WER = 1.0, never dropped.
- Every orig_3090 clip is cut at 9.12 s. Nick wants to know if WER shows the endings cut off
  (`trailing_dels` = reference words missing at the end).
- Clips appear to start with an "intro" (extra speech before the prompt text). We are waiting on

## dots.tts background (from the model README; relevant facts only)
- dots.tts outputs 48 kHz mono audio, generated autoregressively in latent "patches" of ~160 ms.
  9.12 s = exactly 57 patches, so the orig_3090 cut is likely a max-generation-length setting.
- Voice cloning modes:
  - continuation cloning: --prompt-audio (reference wav) + --prompt-text (its exact transcript)
  - x-vector-only cloning: --prompt-audio only (no transcript)
  In continuation mode the output should contain only the target sentence, not the reference.
- The README's sample reference voice is docs/_static/audio/male-voice.wav with transcript
  "Hey, Adam here. Let's create something that feels real, sounds human, and connects every time."
  That is exactly the intro found on every orig_3090 clip. xvector_4090 clips have no intro,
  consistent with x-vector-only cloning.
- `--num-steps` = NFE (sampling steps); default 10 for flow-matching checkpoints.
- The README's published WER (~1.3% English) uses different, stronger ASR models
  (benchmark reference ASR / Qwen3-ASR-1.7B), so our Whisper-small numbers are NOT comparable.
- The README in runs/nfe_benchmark/ (if present) is Nick's experiment notes, not this model README.

## Rules
- Never modify clips.csv, the audio files, or anything in runs/human_arush/.
- Outputs go next to clips.csv: clips_with_wer.csv and wer_run_info.json.
- Normalization rules may only reconcile different WRITINGS of the same spoken words
  ("Ave." vs "avenue"). Never add a rule that turns a wrong word into a right one.
- Report corpus WER (total errors / total reference words), never the average of per-clip WER.
- WER can exceed 1.0 when extra words are inserted. Do not cap it.
- Transcription is slow on this laptop. Never delete runs/nfe_benchmark/asr_progress.jsonl
  (saved transcripts) unless the ASR model changes or Arush asks.
- Always test on a few clips (--limit) before a full run, and show Arush the results.
- Explain what you changed in plain language.

