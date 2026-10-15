# tts_eval

**Intelligibility scoring (WER / CER) for dots.tts text-to-speech samples, built for an NFE (sampling-step) sweep.**

![Python](https://img.shields.io/badge/python-3.11-blue)
![ASR](https://img.shields.io/badge/ASR-faster--whisper%20small-orange)
![Tests](https://img.shields.io/badge/tests-87%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

`tts_eval` transcribes generated speech with Whisper and compares each transcript with the text the clip was
supposed to say. It reports **word error rate (WER)**, **character error rate (CER)** and a set of diagnostic
measures (cut-off endings, an unexpected spoken "intro", silent clips), per clip and as corpus totals. Every
number is reproducible from cached transcripts, and every scoring rule is unit-tested.

> **All WER, CER and other metric calculations in this project are done here, by this code** — `asr.py`
> (transcription), `metrics.py` (normalization, WER) and `score_clips.py` (per-clip WER/CER, intro handling,
> cut-off measures, corpus totals). No scores were taken from another tool or copied from elsewhere.

---

## Contents

- [Results at a glance](#results-at-a-glance)
- [Benchmark results vs. test and sample runs](#benchmark-results-vs-test-and-sample-runs)
- [How it works](#how-it-works)
- [Metrics: what is calculated and where](#metrics-what-is-calculated-and-where)
- [Text normalization](#text-normalization)
- [Installation](#installation)
- [Usage](#usage)
- [Reproducing the benchmark results](#reproducing-the-benchmark-results)
- [Output files](#output-files)
- [Testing](#testing)
- [Project structure](#project-structure)
- [Findings about the audio](#findings-about-the-audio)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Results at a glance

Benchmark: **972 generated clips** = 2 runs (`orig_3090`, `xvector_4090`) × 54 prompts × 9 NFE values
(4, 6, 8, 10, 12, 16, 20, 24, 32). Official scores ignore a spoken intro found in the `orig_3090` clips
(see [Findings](#findings-about-the-audio)).

| | Corpus WER | Corpus CER |
|---|---|---|
| **All 972 clips** | **0.583** (12,712 errors / 21,798 words) | **0.568** (68,318 / 120,222 chars) |
| `orig_3090` | 0.966 | 0.957 |
| `xvector_4090` | 0.200 | 0.180 |
| Intro counted as errors (all clips) | 0.709 | 0.602 |

**NFE vs. quality, clean subset** (`xvector_4090`, short + medium prompts; no clip hits a length cap; 36 clips per NFE):

| NFE | 4 | 6 | 8 | 10 | 12 | 16 | 20 | 24 | 32 |
|---|---|---|---|---|---|---|---|---|---|
| WER | 0.027 | 0.039 | 0.036 | 0.036 | 0.032 | 0.046 | 0.036 | 0.036 | 0.027 |
| CER | 0.012 | 0.016 | 0.017 | 0.019 | 0.019 | 0.024 | 0.018 | 0.018 | 0.013 |

Full breakdowns (by run, NFE, run × NFE, run × prompt length) are in
[`runs/nfe_benchmark/deliverables/summary.md`](runs/nfe_benchmark/deliverables/summary.md).

---

## Benchmark results vs. test and sample runs

This folder contains one real evaluation and several smaller test and sample runs used to build and check the
pipeline. **Only the benchmark run produced the reported results.**

| | What it is | Audio | Command | Where results go | Used in reported results? |
|---|---|---|---|---|---|
| **Benchmark run** | Transcription and scoring of every generated clip | `runs/nfe_benchmark/clips/` (972 WAVs, 48 kHz) | `python score_clips.py runs/nfe_benchmark/clips.csv --official no_intro` | `runs/nfe_benchmark/deliverables/` | **Yes — all reported WER/CER** |
| Test-mode benchmark runs | The same script on a few clips (`--limit`, `--files`) to check behaviour before the full run | A subset of the 972 clips | `score_clips.py ... --files a.wav b.wav` | Transcripts cached in `asr_progress.jsonl`; no deliverables are written until all clips are done | Indirectly: the first 13 transcripts were cached by a test run with identical settings and reused (transcription is deterministic; re-transcribing 3 of them gave byte-identical text) |
| Sample: own recordings | A sanity check on real human speech, not TTS | `runs/human_<name>/audio/` (3 recordings of prompts p002, p004, p005) | `python quick_score.py` | Printed only | **No.** Result: corpus WER 0.047 (2 errors / 43 words) |
| Sample: sentence pairs | Normalization debugging on typed text, no audio | none | `python metrics.py "<written>" "<spoken>"` | Printed only | **No** |
| Unit tests | Synthetic strings that pin down every metric and normalization rule | none | `pytest` | Pass/fail | **No** (they verify the code that produced the results) |

---

## How it works

```
 clips.csv + clips/*.wav
          │
          ▼
 ┌────────────────────┐   too short (<0.5 s) or silent (RMS < 1e-3)
 │ asr.check_audio    │ ───────────────────────────────► scored as WER = CER = 1.0
 └────────────────────┘
          │
          ▼
 ┌────────────────────┐   faster-whisper "small", int8, CPU, English,
 │ asr / score_clips  │   beam 5, temperature 0  → transcript
 │ transcribe_audio   │   cached per clip in asr_progress.jsonl (resumable)
 └────────────────────┘
          │
          ▼
 ┌────────────────────┐   same rules applied to reference and transcript
 │ metrics.normalize  │   (Whisper EnglishTextNormalizer + format-only rules)
 └────────────────────┘
          │
          ▼
 ┌────────────────────┐   jiwer word / character alignment, two versions:
 │ score_clips        │     full      transcript as is
 │ score_clip         │     no_intro  leading intro speech set aside
 └────────────────────┘
          │
          ▼
 deliverables: per-clip CSV, run info JSON, summary, findings
```

Transcription is the slow step (about 40 minutes for 972 clips on an 8 GB laptop CPU). Scoring is fast and
always recomputed from the cached transcripts, so changing a scoring rule never requires re-transcription.

---

## Metrics: what is calculated and where

All metrics are calculated in this repository with [jiwer](https://github.com/jitsi/jiwer) alignments on
normalized text.

| Metric | Definition | Calculated in |
|---|---|---|
| **WER** | (substitutions + deletions + insertions) / reference words | `score_clips.py` `score_version()`; also `metrics.py` `compute_wer()` |
| **CER** | character edit distance / reference characters (spaces included) | `score_clips.py` `score_version()` |
| **Corpus WER** | total word errors / total reference words over a group of clips — never the mean of per-clip WER | `metrics.py` `corpus_wer()` |
| **Corpus CER** | total character errors / total reference characters | `score_clips.py` `corpus_cer()` |
| `missing_end_words` | reference words after the last correctly heard word (all of them if none was heard); the main cut-off measure | `score_clips.py` `word_errors()` |
| `trailing_dels` | reference words in a deletion at the very end of the alignment | `score_clips.py` `word_errors()` |
| `heard_ref_words`, `heard_errors`, `wer_heard` | WER over the part of the sentence before the cut (empty if nothing was heard) | `score_clips.py` `heard_scores()` |
| Intro split (`intro_text`) | transcript prefix up to the last exact match to the known intro phrase | `score_clips.py` `split_intro()` |
| Silent-clip rejection | duration < 0.5 s or RMS < 1e-3 (about -60 dBFS) | `asr.py` `check_audio()` |
| SIM (side experiment, not in results) | cosine similarity of WavLM x-vectors | `metrics.py` `sim()` |

**Two scoring versions.** Each clip is scored twice from the same normalized texts:

- `full` — the transcript as is; any intro speech counts as inserted words.
- `no_intro` — transcript words matching the known intro phrase at the start are set aside in `intro_text`, and
  the rest is scored against the reference. This is the official version (`wer_version = no_intro`).

**Capping.** The `wer` and `cer` columns are the official values capped at 1.0 (the requested 0–1 range).
Uncapped values are kept in `wer_uncapped`, `cer_uncapped` and every `*_full` / `*_no_intro` column.
12 clips were capped.

**Silent clips** (4 in the benchmark) are never dropped: empty transcript, WER = CER = 1.0, every reference
word counted as a deletion, in both versions.

---

## Text normalization

Reference and transcript go through the same steps (`metrics.py` `normalize()`):

1. Lowercase.
2. `PRE_RULES` — format-only rewrites.
3. Whisper `EnglishTextNormalizer` (numbers, currency, contractions, spelling variants, punctuation).
4. `POST_RULES` — joins split digit groups and "N and a half".

| Rule | Example (written ↔ spoken) |
|---|---|
| Dotted acronyms and times | `a.m.` ↔ `AM` |
| Clock times | `6:15` ↔ `6 15` |
| Fractions | `2 1/2`, `2½` ↔ `2 and a half` |
| Street / road / room | `Ave.` ↔ `Avenue`, `Hwy.` ↔ `Highway`, `Rm.` ↔ `Room` |
| Months, with or without a dot | `Jan.`, `Jan` ↔ `January`; `Mar.`, `Mar` ↔ `March` |
| Compounds | `doorframe` ↔ `door frame`; `quetzal feather` ↔ `Quetzalfeather` |
| Startups | `startup's` ↔ `start-ups` ↔ `startups` |
| Digit groups | `555-0147` ↔ `555 0147` |

**Golden rule:** a rule may only reconcile different *writings* of the same spoken words. A rule must never turn
a wrong word into a right one (for example, correcting a misrecognised name), because that would hide real TTS
errors. Every rule has a written/spoken pair in the unit tests. The full rule list used for a run is recorded
in `wer_run_info.json`.

---

## Installation

**Requirements:** Python 3.11 and about 1 GB of disk for the Whisper model and packages. No GPU is needed, and no
separate FFmpeg install: faster-whisper decodes audio itself (via PyAV).

```bash
git clone <this-repo> tts_eval        # or copy the folder
cd tts_eval
python3.11 -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The Whisper `small` model downloads automatically on first use. For the optional SIM experiment, also install
`torch` and `transformers` (commented out in `requirements.txt`).

---

## Usage

Always run from the project folder with the virtual environment active.

### Score a benchmark (`score_clips.py`)

```bash
# Test on a few clips first (only these clips' audio needs to exist)
python score_clips.py runs/nfe_benchmark/clips.csv --official no_intro --limit 10
python score_clips.py runs/nfe_benchmark/clips.csv --official no_intro --files orig_3090__p036__nfe6.wav

# Full run (resumable: rerun the same command if it stops)
caffeinate -i python score_clips.py runs/nfe_benchmark/clips.csv --official no_intro   # macOS: keeps the laptop awake
```

| Option | Meaning |
|---|---|
| `csv` | Benchmark CSV with columns `file, run_id, prompt_id, nfe, length, content, text, repo_path, wer`; audio is looked up in `clips/` next to it |
| `--official {full,no_intro}` | **Required.** Which version fills the `wer` / `cer` columns |
| `--limit N` | Transcribe only the next N untranscribed clips |
| `--files F [F ...]` | Transcribe only these clips (values from the `file` column) |

Deliverables are written only once every clip has a transcript. Rerunning after a scoring change re-scores all
clips from the cache in seconds.

### Debug a normalization mismatch (`metrics.py`)

```bash
python metrics.py "St. Clair Ave. is closed from Jan. to Mar." "Saint Clair Avenue is closed from January to March"
# reference -> saint clair avenue is closed from january to march
# transcript-> saint clair avenue is closed from january to march
# {'wer': 0.0, 'subs': 0, 'dels': 0, 'ins': 0, 'ref_words': 9}
```

### Score your own recordings (`quick_score.py`)

Recordings named `<prompt_id>.wav` (e.g. `p002.wav`) are scored against `prompts/benchmark_prompts_v1.json`.
Change the `glob` path in the script to point at your own recordings folder.

```bash
python quick_score.py
```

### Transcribe a single file (`asr.py`)

```bash
python asr.py path/to/clip.wav
```

---

## Reproducing the benchmark results

1. Place the requester's `clips.csv` and the `clips/` folder (972 WAVs) in `runs/nfe_benchmark/`.
2. Record the CSV hash so you can prove it was not modified: `shasum -a 256 runs/nfe_benchmark/clips.csv`.
3. Run `pytest` (all tests must pass).
4. Run the full command above with `--official no_intro`.
5. Compare with `summary.md`: corpus WER 0.5832 (no_intro) / 0.7089 (full), corpus CER 0.5683 / 0.6024.
6. Re-hash `clips.csv`; it must match step 2.

Results are deterministic for a given model, settings and package versions (`wer_run_info.json` records all of
them). A different Whisper model or version will change absolute numbers.

**Changing the ASR model:** edit `ASR_SETTINGS` in `asr.py` (e.g. `"model": "large-v3"`, `"device": "cuda"`,
`"compute_type": "float16"` on a GPU). The script refuses to mix models; delete `asr_progress.jsonl` only when
you intentionally switch models, because it holds the slow-to-make transcripts.

---

## Output files

Written to `runs/nfe_benchmark/deliverables/` by `score_clips.py` (CSV and JSON) or during review (Markdown).

| File | Contents |
|---|---|
| Scored CSV (written as `clips.csv`; the shared copy may be renamed) | The 9 original columns with `wer` filled in, then the columns below, same row order |
| `wer_run_info.json` | ASR package, versions and every setting; normalization rules; metric definitions; corpus WER and CER (overall, by run, NFE, run × NFE); capping counts; intro phrase and method |
| `summary.md` | Results, rule effects and the full verification output |
| `intro_and_cut_findings.md` | Investigation of the intro and the 9.12 s length cap; each claim marked confirmed, likely or unverified |
| Message draft (`check1.md`) | Short write-up for the requester |

**Columns added to the CSV**

| Column | Meaning |
|---|---|
| `wer` | Official WER (no_intro), capped at 1.0 |
| `transcript` | Raw Whisper transcript |
| `cer` | Official CER, capped at 1.0 |
| `wer_uncapped`, `cer_uncapped` | Same without the cap |
| `wer_version` | Version used for `wer` / `cer` |
| `missing_end_words` | Reference words after the last correctly heard word |
| `heard_ref_words`, `heard_errors`, `wer_heard` | WER before the cut |
| `intro_text` | Transcript words set aside as intro (normalized) |
| `{wer,cer,subs,dels,ins,trailing_dels,missing_end_words}_{full,no_intro}` | Uncapped metrics per version |
| `ref_words`, `ref_norm`, `hyp_norm` | Reference word count and the normalized texts that were compared |
| `duration_s`, `asr_status` | Clip length; `ok` or the reason a clip was not transcribed |

---

## Testing

```bash
pytest -q          # 87 tests
```

The suite in `tests/test_metrics.py` covers: identical text → 0; one wrong word in seven → 1/7; empty transcript →
1.0; every normalization rule with a written/spoken pair; intro handling (full, partial, absent, misheard first
word, intro-only clips); `missing_end_words` and `trailing_dels` on cut-off endings; heard-portion WER; capping
never changing uncapped values; per-clip and corpus CER; and all 54 benchmark prompts scoring 0 against
themselves with nothing taken as intro.

Verification of the benchmark output (row count and order, original columns unchanged, `wer` / `cer` in [0, 1],
the 4 silent clips at 1.0, corpus totals recomputed independently, input hash unchanged) is recorded in
`summary.md`.

---

## Project structure

```
tts_eval/
├── README.md                     this file
├── LICENSE                       MIT
├── requirements.txt              pinned dependencies
├── asr.py                        audio loading, silent/short rejection, Whisper transcription, ASR_SETTINGS
├── metrics.py                    normalize(), compute_wer(), corpus_wer(), sim()
├── score_clips.py                benchmark scoring: caching, full/no_intro, CER, cut-off measures, outputs
├── quick_score.py                sample: score your own recordings
├── tests/test_metrics.py         unit tests
├── prompts/
│   └── benchmark_prompts_v1.json 54 benchmark prompts (p001–p054) with length and category labels
├── runs/
│   ├── human_<name>/             SAMPLE: own recordings (audio/p002.wav, p004.wav, p005.wav); not modified
│   └── nfe_benchmark/            BENCHMARK
│       ├── clips.csv             input CSV (read-only)
│       ├── <requester>_README.txt  request notes (read-only)
│       ├── clips/                972 generated WAVs (read-only, ~740 MB)
│       ├── asr_progress.jsonl    cached transcripts (do not delete)
│       └── deliverables/         scored CSV, JSON, summary, findings, message draft
└── CLAUDE.md                     working notes for AI coding assistants
```

---

## Findings about the audio

Details and evidence: [`intro_and_cut_findings.md`](runs/nfe_benchmark/deliverables/intro_and_cut_findings.md).

- **Spoken intro (orig_3090 only).** 481 of 486 `orig_3090` clips begin with "Hey, Adam here. Let's create
  something that feels real, sounds human, and connects every time." — the sample transcript from the dots.tts
  README. It was used as `reference_text` for a reference voice clip that actually says something else, in
  continuation-cloning mode. The mismatch is the likely cause. No `xvector_4090` clip has it.
- **Length caps.** In continuation mode the reference audio shares the `--max-generate-length 80` patch budget, so
  `orig_3090` clips stop at 9.12 s (445 of 486 clips are exactly 9.12 s). `xvector_4090` long-prompt clips stop at
  12.8 s. WER shows the cut clearly: `orig_3090` clips at the cap miss on average 22 reference words at the end.
- **Silent clips.** `orig_3090` p036 NFE 6 and p018, p034, p045 NFE 8 are silent and scored 1.0.

---

## Known limitations

- **Whisper `small` on CPU.** Less accurate than `large-v3`; comparisons across NFE are sound, absolute WER is
  approximate.
- **orig_3090 scores mostly measure the cut, not pronunciation**, because the intro leaves little time for the
  sentence. Use `xvector_4090` short + medium for NFE vs. quality.
- **Intro alignment edge cases.** When the intro's last word is cut or misheard, that word counts as an error
  (about 18 clips). One clip blending the intro with other speech (p035 NFE 16) gets no intro detected.
- **`wer_heard` is only meaningful when most of the sentence is heard** (it is for `xvector_4090`, not for
  `orig_3090`).
- **Normalization is English-only.**

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `N audio files not found` | Put the WAVs in `clips/` next to the CSV, or test with `--limit` / `--files` |
| `asr_progress.jsonl was made with ASR model ...` | You changed `ASR_SETTINGS`; delete the cache only if you mean to re-transcribe everything |
| `row N is X, but clips.csv row N is Y` | The CSV changed after transcription; restore the original CSV |
| A correct-sounding clip scores badly | Run `python metrics.py "<reference>" "<transcript>"` to see both normalized texts; propose a format-only rule if they differ only in writing |
| Run stops when the laptop sleeps | Use `caffeinate -i` (macOS) and rerun; it resumes from the cache |
| `ModuleNotFoundError` | Activate `.venv` and `pip install -r requirements.txt` |

---

## Contributing

1. Keep input data read-only: never edit `clips.csv`, the audio or the sample recordings.
2. Report corpus metrics as totals / totals, never as a mean of per-clip values.
3. New normalization rules must be format-only, come with a written/spoken unit test, and be listed in the run
   info automatically (they are, if added to `PRE_RULES` / `POST_RULES`).
4. Test on a few clips (`--limit`) before a full run.
5. Run `pytest` before submitting changes.

---

## License

The code in this repository is released under the [MIT License](LICENSE).

The license does **not** cover the data in `runs/` (generated audio, benchmark CSV, prompts and recordings),
which belongs to the research project that produced it.

**Third-party software and models used**

| Component | Version | License |
|---|---|---|
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 1.2.1 | MIT |
| [CTranslate2](https://github.com/OpenNMT/CTranslate2) | 4.8.3 | MIT |
| Whisper `small` model weights ([OpenAI Whisper](https://github.com/openai/whisper)) | — | MIT |
| [jiwer](https://github.com/jitsi/jiwer) | 4.0.0 | Apache-2.0 |
| [whisper-normalizer](https://github.com/kurianbenoy/whisper_normalizer) | 0.1.15 | MIT |
| [pandas](https://pandas.pydata.org/) | 3.0.6 | BSD-3-Clause |
| [NumPy](https://numpy.org/) | 2.4.6 | BSD-3-Clause (and others) |
| [soundfile](https://github.com/bastibe/python-soundfile) | 0.14.0 | BSD-3-Clause |
| [openpyxl](https://openpyxl.readthedocs.io/) (optional) | 3.1.5 | MIT |
| [pytest](https://pytest.org/) (tests) | 9.1.1 | MIT |
| [PyTorch](https://pytorch.org/) (optional SIM) | 2.14.1 | as declared in its package metadata (Apache-2.0 and others) |
| [Transformers](https://github.com/huggingface/transformers) (optional SIM) | 5.19.0 | Apache-2.0 |
| `microsoft/wavlm-base-plus-sv` (optional SIM model) | — | see its model card |
| dots.tts (generated the evaluated audio) | — | Apache-2.0 |

---

## Acknowledgements

- [dots.tts](https://github.com/studio-dots-ai/dots.tts) for the text-to-speech model under evaluation.
- [OpenAI Whisper](https://github.com/openai/whisper) and [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
  for speech recognition.
- [jiwer](https://github.com/jitsi/jiwer) for WER / CER alignment.
