# WER run summary: dots.tts NFE sweeps (Atharv's request)

Generated 2026-10-14 from `runs/nfe_benchmark/deliverables/clips.csv` (972 clips, official version `no_intro`).
ASR: faster-whisper 1.2.1 (ctranslate2 4.8.3), Whisper `small`, int8, CPU, English, beam 5, temperature 0,
condition_on_previous_text off. Normalization: Whisper EnglishTextNormalizer (whisper-normalizer 0.1.15) +
PRE_RULES/POST_RULES from metrics.py, applied to reference and transcript. jiwer 4.0.0.
The intro / 9.12 s investigation is in `intro_and_cut_findings.md`.

**All verification checks passed (sections 1-12 below). Rescoring only: no clip was re-transcribed.**

## Key results
- Corpus WER: **no_intro 0.5832** (12,712 errors / 21,798 words), **full 0.7089** (15,452 / 21,798).
- orig_3090: no_intro 0.9661, full 1.2175. xvector_4090: 0.2002 (identical in both versions; no intro).
- Clean subset for NFE vs quality, xvector_4090 short + medium (324 clips, none capped): corpus WER 0.0351,
  between 0.027 and 0.046 per NFE with no trend (section 10).
- Corpus `wer_heard` (WER before the cut): xvector 0.0235, orig 0.2550 (not meaningful for orig; see section 9).
- Corpus CER (total character errors / total reference characters): **no_intro 0.5683** (68,318 / 120,222),
  full 0.6024. orig_3090 0.9567, xvector_4090 0.1799; clean subset (xvector short + medium) 0.0173, between 0.012 and
  0.024 per NFE. By run and NFE in section 12.
- Clips capped at 1.0 in `wer`: 12.
- 4 silent clips, all orig_3090 (p036 NFE 6; p018, p034, p045 NFE 8): empty transcript, WER 1.0 in both versions.
- 9.12 s question: yes, WER shows the cut (section 5; conclusion in intro_and_cut_findings.md).

## Changes since the first STOP POINT 2 (all approved)
### 1. Format-only normalization rules (PRE_RULES in metrics.py, each with a written/spoken unit test)
| rule | written / spoken | no_intro errors removed |
|---|---|---|
| `\bjan\b\.?` -> january | "Jan." / "Jan" | 8 |
| `\bmar\b\.?` -> march | "Mar." / "Mar" | 8 |
| `\bdoor[ -]frame` -> doorframe | "doorframe" / "door frame" | 18 |
| `\bquetzal[ -]?feather` -> quetzal feather | "quetzal feather" / "Quetzalfeather" | 16 |
| `\bstart-?up(?:'s\|s)\b` -> startups | "startup's" / "start-ups", "startups", "start-up's" | 23 |
| total | | 73 |
"jan" and "mar" occur in no prompt except as these abbreviations (p033); "March" in p013 is unaffected. The startups
rule also changes the reference word count ("startup's" became "startup is" = 2 words, now "startups" = 1), so total
reference words went from 21,816 to 21,798.

### 2. Stricter intro attribution
The intro is now the transcript only up to its last EXACT match to an intro word. Measured with the old rules:
12,778 -> 12,785 no_intro errors (+7). With the new rules and strict attribution: 12,712.
- xvector clips with non-empty `intro_text`: 22 -> **0**.
- Side effect: when the intro's own last word is cut or misheard ("connect" x9, "hu" x4, "con" x2, "sound"), that word
  now counts as an inserted error in about 18 orig clips. 66 clips (44 orig, 22 xvector) now have leading words
  that are scored rather than set aside; for xvector these are the misheard first words ("Savan", "past"...).
- orig clips with an intro: 482 -> 481. The one orig speech clip without a detected intro is p035 NFE 16
  ("Hello, my name is Adam here."): an alignment edge case, not a bug. Its 6 blended words align at equal or lower
  cost to the reference than to the intro (jiwer matches "is" to a reference "is" and "adam here" as substitutions),
  so nothing is attributed. Scoring left as is: WER 0.977 either way; the stray "is" match gives it heard_ref_words
  32 / missing_end_words 12 instead of 0 / 44.

### 3. heard_ref_words / heard_errors / wer_heard (new columns, official version)
No earlier definition reached this session, so these are defined as follows (unit-tested):
- `heard_ref_words` = reference words up to and including the last correctly heard word (= ref_words - missing_end_words).
- `heard_errors` = S + D + I between those reference words and the transcript up to the same matched word.
- `wer_heard` = heard_errors / heard_ref_words; empty when nothing was heard (276 orig clips, 0 xvector).
- Corpus wer_heard = total heard_errors / total heard_ref_words.

## Duration checks
- `duration_s` matches `audio_duration_seconds` in watai_exp results.csv for all 972 clips.
- orig_3090: 445 clips exactly 9.12 s, 41 shorter (7.52-8.96 s); xvector_4090: 1.44-12.80 s, all 162 long clips 12.80 s.

## Known limitations
- orig_3090 WER mostly measures the cut, not pronunciation: little of the target sentence fits after the intro.
- 5 orig clips repeat the intro mid-clip and several loop a phrase; these count as errors (they are real output).
- Whisper `small` is less accurate than large-v3; NFE comparisons are sound, absolute WER is approximate.

---

# Verification output
## 1. Deliverable CSV checks
- PASS: 972 rows
- PASS: row order identical to clips.csv
- PASS: original columns identical incl. dtypes as read: ['file', 'run_id', 'prompt_id', 'nfe', 'length', 'content', 'text', 'repo_path']
- PASS: first 9 columns are the original columns in order
- PASS: `wer` has no blanks, all in [0, 1]
- PASS: `cer` has no blanks, all in [0, 1]
- PASS: wer_version = no_intro on every row

## 2. Silent / rejected clips
| file | run_id | prompt | nfe | status | transcript | wer | wer_full | wer_no_intro |
|---|---|---|---|---|---|---|---|---|
| orig_3090__p018__nfe8.wav | orig_3090 | p018 | 8 | rejected: silent (RMS 0.00017 < 0.001) | '' | 1.0 | 1.0 | 1.0 |
| orig_3090__p034__nfe8.wav | orig_3090 | p034 | 8 | rejected: silent (RMS 0.00017 < 0.001) | '' | 1.0 | 1.0 | 1.0 |
| orig_3090__p036__nfe6.wav | orig_3090 | p036 | 6 | rejected: silent (RMS 0.00021 < 0.001) | '' | 1.0 | 1.0 | 1.0 |
| orig_3090__p045__nfe8.wav | orig_3090 | p045 | 8 | rejected: silent (RMS 0.00021 < 0.001) | '' | 1.0 | 1.0 | 1.0 |
- PASS: exactly 4 rejected clips, = p036 NFE 6, p018/p034/p045 NFE 8 (got [('p018', 8), ('p034', 8), ('p036', 6), ('p045', 8)])
- PASS: all 4 are in orig_3090
- PASS: all 4 have wer = 1.0 in both versions
- PASS: all 4 have an empty transcript

Every clip matching the README's 4 (prompt, NFE), both runs:
- orig_3090__p018__nfe8.wav: rejected: silent (RMS 0.00017 < 0.001), transcript ''
- orig_3090__p034__nfe8.wav: rejected: silent (RMS 0.00017 < 0.001), transcript ''
- orig_3090__p036__nfe6.wav: rejected: silent (RMS 0.00021 < 0.001), transcript ''
- orig_3090__p045__nfe8.wav: rejected: silent (RMS 0.00021 < 0.001), transcript ''
- xvector_4090__p018__nfe8.wav: ok, transcript 'In the final round, the runner finished the 400 meters in 47'
- xvector_4090__p034__nfe8.wav: ok, transcript 'According to the WHO, the new guidelines were drafted with i'
- xvector_4090__p036__nfe6.wav: ok, transcript 'Mr. Okafor, the VP of Ops, sent an email at 9am asking every'
- xvector_4090__p045__nfe8.wav: ok, transcript "Honestly, what did they expect? You can't cancel the festiva"
- PASS: no other clip has an empty transcript (0 found)

## 3. Corpus WER recomputed from saved columns
- PASS: full: 15452 errors / 21798 words = 0.7089 (run printed 0.7089)
  - independent jiwer recompute (full): 15452 errors (alignment ties can differ by a few)
- PASS: no_intro: 12712 errors / 21798 words = 0.5832 (run printed 0.5832)
  - independent jiwer recompute (no_intro): 12712 errors (alignment ties can differ by a few)

## 4. Corpus WER breakdowns
Overall: full 0.7089, no_intro 0.5832

### By run_id
| run_id | clips | WER full | WER no_intro | mean missing_end_words full | no_intro |
|---|---|---|---|---|---|
| orig_3090 | 486 | 1.2175 | 0.9661 | 12.23 | 20.28 |
| xvector_4090 | 486 | 0.2002 | 0.2002 | 3.89 | 3.89 |

### By nfe
| nfe | clips | WER full | WER no_intro | mean missing_end_words full | no_intro |
|---|---|---|---|---|---|
| 4 | 108 | 0.7436 | 0.6007 | 8.02 | 12.08 |
| 6 | 108 | 0.7164 | 0.5904 | 8.10 | 12.49 |
| 8 | 108 | 0.6833 | 0.5545 | 8.15 | 11.98 |
| 10 | 108 | 0.6709 | 0.5479 | 7.19 | 12.04 |
| 12 | 108 | 0.6685 | 0.5516 | 7.75 | 12.18 |
| 16 | 108 | 0.7675 | 0.6350 | 8.05 | 11.85 |
| 20 | 108 | 0.7271 | 0.6111 | 8.21 | 11.81 |
| 24 | 108 | 0.7188 | 0.6061 | 8.27 | 12.26 |
| 32 | 108 | 0.6837 | 0.5512 | 8.77 | 12.06 |

### By run_id x nfe
| run_id | nfe | clips | WER full | WER no_intro | mean missing_end_words full | no_intro |
|---|---|---|---|---|---|---|
| orig_3090 | 4 | 54 | 1.2692 | 0.9835 | 11.52 | 19.65 |
| orig_3090 | 6 | 54 | 1.2106 | 0.9587 | 11.63 | 20.41 |
| orig_3090 | 8 | 54 | 1.1759 | 0.9182 | 12.67 | 20.33 |
| orig_3090 | 10 | 54 | 1.1536 | 0.9075 | 10.61 | 20.30 |
| orig_3090 | 12 | 54 | 1.1577 | 0.9240 | 11.81 | 20.67 |
| orig_3090 | 16 | 54 | 1.3518 | 1.0867 | 12.48 | 20.09 |
| orig_3090 | 20 | 54 | 1.2147 | 0.9827 | 12.91 | 20.09 |
| orig_3090 | 24 | 54 | 1.2477 | 1.0223 | 12.70 | 20.69 |
| orig_3090 | 32 | 54 | 1.1767 | 0.9116 | 13.70 | 20.30 |
| xvector_4090 | 4 | 54 | 0.2180 | 0.2180 | 4.52 | 4.52 |
| xvector_4090 | 6 | 54 | 0.2221 | 0.2221 | 4.57 | 4.57 |
| xvector_4090 | 8 | 54 | 0.1908 | 0.1908 | 3.63 | 3.63 |
| xvector_4090 | 10 | 54 | 0.1883 | 0.1883 | 3.78 | 3.78 |
| xvector_4090 | 12 | 54 | 0.1792 | 0.1792 | 3.69 | 3.69 |
| xvector_4090 | 16 | 54 | 0.1833 | 0.1833 | 3.61 | 3.61 |
| xvector_4090 | 20 | 54 | 0.2395 | 0.2395 | 3.52 | 3.52 |
| xvector_4090 | 24 | 54 | 0.1899 | 0.1899 | 3.83 | 3.83 |
| xvector_4090 | 32 | 54 | 0.1908 | 0.1908 | 3.83 | 3.83 |

### By run_id x length
| run_id | length | clips | WER full | WER no_intro | mean missing_end_words full | no_intro |
|---|---|---|---|---|---|---|
| orig_3090 | long | 162 | 0.9782 | 0.9896 | 23.66 | 43.60 |
| orig_3090 | medium | 162 | 1.1857 | 1.0586 | 11.54 | 15.77 |
| orig_3090 | short | 162 | 3.2732 | 0.4796 | 1.48 | 1.48 |
| xvector_4090 | long | 162 | 0.2850 | 0.2850 | 11.59 | 11.59 |
| xvector_4090 | medium | 162 | 0.0348 | 0.0348 | 0.05 | 0.05 |
| xvector_4090 | short | 162 | 0.0363 | 0.0363 | 0.02 | 0.02 |

- Clips with uncapped WER > 1.0 (full): 220; CER > 1.0: 169
- Clips with uncapped WER > 1.0 (no_intro): 12; CER > 1.0: 8
- Clips capped in Atharv's `wer` column: 12

### Intro per run (clips with / without intro_text)
- orig_3090: 481 with / 5 without
- xvector_4090: 0 with / 486 without

### Top 5 intro_text values
- 387 x `hey adam here let us create something that feels real sounds human and connects every time`
- 26 x `hey adam here let us create something that feels real sounds human`
- 26 x `hey adam here let us create something that feels real sounds human and connects`
- 20 x `hey adam here let us create something that feels real sounds human and`
- 4 x `hey adam here let us create something that feels real sounds human and connects every`

Clips with words before the first reference match NOT attributed to the intro: 66
- orig_3090__p008__nfe16.wav (1 words): 'hey adam here let us create something that feels real sounds human and connect'
- orig_3090__p009__nfe20.wav (1 words): 'hey adam here let us create something that feels real sounds hu'
- orig_3090__p010__nfe12.wav (3 words): 'hey adam here let us create something that feels real sounds human and connects every time you are .'
- orig_3090__p016__nfe4.wav (1 words): 'hey adam here let us create something that feels real sounds human and connect'
- orig_3090__p017__nfe4.wav (1 words): 'hey adam here let us create something that feels real sounds human and connect'
- orig_3090__p017__nfe8.wav (1 words): 'hey adam here let us create something that feels real sounds human and connect'
- orig_3090__p018__nfe12.wav (1 words): 'hey adam here let us create something that feels real sounds human and connects everything'
- orig_3090__p019__nfe4.wav (1 words): 'hey adam here let us create something that feels real sounds human and connects every time saban met joaquin i'
- orig_3090__p019__nfe6.wav (4 words): 'hey adam here let us create something that feels real sounds human and connects every time see you all soon'
- orig_3090__p019__nfe8.wav (1 words): 'hey adam here let us create something that feels real sounds human and connects every time elban met joaquin i'
- orig_3090__p019__nfe10.wav (1 words): 'hey adam here let us create something that feels real sounds human and connects every time siaban met joaquin '
- orig_3090__p019__nfe12.wav (1 words): 'hey adam here let us create something that feels real sounds human and connects every time siaban met joquine '
- orig_3090__p019__nfe20.wav (1 words): 'hey adam here let us create something that feels real sounds human and connects every time siaban met jaquen i'
- orig_3090__p019__nfe24.wav (3 words): 'hey adam here let us create something that feels real sounds human and connects every time see you abon met jo'
- orig_3090__p019__nfe32.wav (3 words): 'hey adam here let us create something that feels real sounds human and connects every time see you bonn met yo'
- orig_3090__p020__nfe16.wav (2 words): 'hey adam here let us create something that feels real sounds human and connects every time that is the quit'
- orig_3090__p025__nfe4.wav (1 words): 'hey adam here let us create something that feels real sounds human and connect'
- orig_3090__p025__nfe16.wav (1 words): 'hey adam here does this create something that feels real sounds you'
- orig_3090__p027__nfe32.wav (1 words): 'hey adam here let us create something that feels real sounds human and connect'
- orig_3090__p030__nfe16.wav (1 words): 'hey adam here let us create something that feels real sounds human and connects every time said delayed the la'
- orig_3090__p033__nfe4.wav (2 words): 'hey adam here let us create something that feels real sounds human and connects every time state claire avenue'
- orig_3090__p033__nfe6.wav (2 words): 'hey adam here let us create something that feels real sounds human and connects every time stay claire avenue'
- orig_3090__p033__nfe10.wav (2 words): 'hey adam here let us create something that feels real sounds human and connects every time stay claire avenue'
- orig_3090__p033__nfe12.wav (2 words): 'hey adam here let us create something that feels real sounds human and connects every time stay clear'
- orig_3090__p033__nfe16.wav (2 words): 'hey adam here let us create something that feels real sounds human and connects every time stay clear'

## 5. The 9.12 s question
| run | min s | median s | max s |
|---|---|---|---|
| orig_3090 | 7.52 | 9.12 | 9.12 |
| xvector_4090 | 1.44 | 6.8 | 12.8 |

orig_3090: 445 clips at 9.12 s, 41 shorter (README says every clip is exactly 9.12 s)

| file | duration s | asr_status | sentence completed (missing_end_words_no_intro = 0) |
|---|---|---|---|
| orig_3090__p001__nfe6.wav | 8.48 | ok | yes |
| orig_3090__p003__nfe10.wav | 8.8 | ok | yes |
| orig_3090__p003__nfe32.wav | 8.8 | ok | yes |
| orig_3090__p011__nfe6.wav | 8.8 | ok | yes |
| orig_3090__p011__nfe8.wav | 8.32 | ok | yes |
| orig_3090__p019__nfe16.wav | 8.64 | ok | yes |
| orig_3090__p019__nfe32.wav | 8.64 | ok | yes |
| orig_3090__p020__nfe6.wav | 8.96 | ok | no (1 missing) |
| orig_3090__p020__nfe8.wav | 8.96 | ok | yes |
| orig_3090__p020__nfe10.wav | 8.8 | ok | no (1 missing) |
| orig_3090__p020__nfe24.wav | 8.96 | ok | no (1 missing) |
| orig_3090__p020__nfe32.wav | 8.96 | ok | no (1 missing) |
| orig_3090__p028__nfe20.wav | 8.8 | ok | yes |
| orig_3090__p029__nfe6.wav | 8.48 | ok | yes |
| orig_3090__p029__nfe10.wav | 8.64 | ok | yes |
| orig_3090__p030__nfe4.wav | 8.32 | ok | yes |
| orig_3090__p037__nfe4.wav | 8.96 | ok | yes |
| orig_3090__p037__nfe10.wav | 8.48 | ok | yes |
| orig_3090__p037__nfe24.wav | 8.64 | ok | yes |
| orig_3090__p037__nfe32.wav | 8.8 | ok | yes |
| orig_3090__p038__nfe24.wav | 8.8 | ok | yes |
| orig_3090__p038__nfe32.wav | 8.32 | ok | yes |
| orig_3090__p039__nfe4.wav | 8.32 | ok | yes |
| orig_3090__p039__nfe6.wav | 8.96 | ok | yes |
| orig_3090__p039__nfe8.wav | 8.48 | ok | yes |
| orig_3090__p039__nfe10.wav | 8.48 | ok | yes |
| orig_3090__p039__nfe12.wav | 8.0 | ok | yes |
| orig_3090__p039__nfe16.wav | 8.96 | ok | yes |
| orig_3090__p039__nfe20.wav | 8.0 | ok | yes |
| orig_3090__p039__nfe24.wav | 8.64 | ok | yes |
| orig_3090__p039__nfe32.wav | 7.52 | ok | yes |
| orig_3090__p046__nfe4.wav | 8.32 | ok | yes |
| orig_3090__p046__nfe6.wav | 8.8 | ok | yes |
| orig_3090__p046__nfe10.wav | 8.16 | ok | yes |
| orig_3090__p046__nfe12.wav | 7.52 | ok | yes |
| orig_3090__p046__nfe24.wav | 7.68 | ok | yes |
| orig_3090__p048__nfe12.wav | 7.84 | ok | yes |
| orig_3090__p048__nfe16.wav | 8.8 | ok | yes |
| orig_3090__p048__nfe20.wav | 8.96 | ok | yes |
| orig_3090__p048__nfe24.wav | 8.48 | ok | yes |
| orig_3090__p048__nfe32.wav | 8.16 | ok | no (1 missing) |

xvector_4090 duration range: 1.44 - 12.8 s; clips >= 9.12 s: 172

### Paired orig_3090 vs xvector_4090 (same prompt + NFE), mean per clip
| length | pairs | ref words | missing_end no_intro orig | xvector | paired diff | missing_end full orig | xvector | paired diff | trailing_dels no_intro orig | xvector | WER no_intro orig | xvector |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| short | 162 | 5.4 | 1.48 | 0.02 | +1.46 | 1.48 | 0.02 | +1.46 | 1.12 | 0.00 | 0.4796 | 0.0363 |
| medium | 162 | 17.4 | 15.77 | 0.05 | +15.72 | 11.54 | 0.05 | +11.49 | 15.25 | 0.04 | 1.0586 | 0.0348 |
| long | 162 | 44.4 | 43.60 | 11.59 | +32.01 | 23.66 | 11.59 | +12.07 | 43.43 | 10.99 | 0.9896 | 0.2850 |
| ALL | 486 | 22.4 | 20.28 | 3.89 | +16.39 | 12.23 | 3.89 | +8.34 | 19.93 | 3.68 | 0.9661 | 0.2002 |

Share of clips with the sentence unfinished (missing_end_words_no_intro > 0), speech clips only:
- short: orig_3090 58%, xvector_4090 2%; target sentence entirely missing: orig 14%, xvector 0%
- medium: orig_3090 99%, xvector_4090 2%; target sentence entirely missing: orig 69%, xvector 0%
- long: orig_3090 100%, xvector_4090 97%; target sentence entirely missing: orig 87%, xvector 0%

### orig_3090 at the 9.12 s cap vs shorter
| group | clips | mean missing_end no_intro | mean missing_end full | mean trailing_dels no_intro | WER no_intro | share unfinished |
|---|---|---|---|---|---|---|
| at 9.12 s | 445 | 22.14 | 13.34 | 21.77 | 0.9837 | 92% |
| shorter | 41 | 0.12 | 0.12 | 0.00 | 0.0534 | 12% |

## 6. Spot-check (5 random clips, seed 7)
- **orig_3090__p047__nfe32.wav** (wer 0.2, wer_full 3.4000, missing_end_no_intro 1)
  - ref: Crisp crusts crackle and crumble.
  - hyp: Hey Adam here. Let's create something that feels real, sounds human, and connects every time. Crisp crusts crackle and crum-
- **xvector_4090__p010__nfe4.wav** (wer 0.0, wer_full 0.0000, missing_end_no_intro 0)
  - ref: Your total comes to $42.75.
  - hyp: Your total comes to $42.75.
- **orig_3090__p044__nfe4.wav** (wer 0.8913, wer_full 0.9783, missing_end_no_intro 41)
  - ref: "Where were you last night?" her brother asked, leaning against the doorframe. "Out," she said. "Out where?" "Just out!" He laughed and shook his head, because he already knew the answer, and she knew that he knew, and neither of them was going to say it.
  - hyp: Hey, Adam here. Let's create something that feels real, sounds human, and connects every time. Where were you last night?
- **orig_3090__p003__nfe20.wav** (wer 1.0, wer_full 2.6667, missing_end_no_intro 6)
  - ref: We walked home along the river.
  - hyp: Hey Adam here, let's create something that feels real, sounds human, and connects every time.
- **xvector_4090__p001__nfe24.wav** (wer 0.0, wer_full 0.0000, missing_end_no_intro 0)
  - ref: The kettle is already on the stove.
  - hyp: The kettle is already on the stove.

## 7. Most common substitutions (no_intro alignment, ref -> hyp)
| ref | hyp | count |
|---|---|---|
| pass | past | 9 |
| grazed | graze | 9 |
| gnawed | nod | 9 |
| aoife | ifa | 8 |
| valladolid | dalid | 7 |
| przybylski | przebilski | 7 |
| tsawwassen | tsawasun | 7 |
| restart | re | 6 |
| siobhan | savan | 6 |
| ngozi | nozi | 6 |
| counting | count | 5 |
| thandiwe | thandiway | 5 |
| szymanowski | szymonowski | 5 |
| saint | stay | 4 |
| nocturne | turn | 4 |

## 9. Heard-portion WER (wer_heard, official no_intro)
- PASS: wer_heard filled exactly when heard_ref_words > 0
- PASS: heard_ref_words = ref_words - missing_end_words
- PASS: corpus wer_heard 478/10053 = 0.0475 matches run info
- clips with nothing heard (excluded from wer_heard): 276 (orig 276, xvector 0)

| run_id | nfe | clips | heard words | ref words | corpus wer_heard | corpus WER no_intro |
|---|---|---|---|---|---|---|
| orig_3090 | 4 | 54 | 150 | 1211 | 0.8333 | 0.9835 |
| orig_3090 | 6 | 54 | 109 | 1211 | 0.0183 | 0.9587 |
| orig_3090 | 8 | 54 | 113 | 1211 | 0.0088 | 0.9182 |
| orig_3090 | 10 | 54 | 115 | 1211 | 0.0261 | 0.9075 |
| orig_3090 | 12 | 54 | 95 | 1211 | 0.0316 | 0.9240 |
| orig_3090 | 16 | 54 | 126 | 1211 | 0.3968 | 1.0867 |
| orig_3090 | 20 | 54 | 126 | 1211 | 0.4206 | 0.9827 |
| orig_3090 | 24 | 54 | 94 | 1211 | 0.2234 | 1.0223 |
| orig_3090 | 32 | 54 | 115 | 1211 | 0.0696 | 0.9116 |
| xvector_4090 | 4 | 54 | 967 | 1211 | 0.0207 | 0.2180 |
| xvector_4090 | 6 | 54 | 964 | 1211 | 0.0228 | 0.2221 |
| xvector_4090 | 8 | 54 | 1015 | 1211 | 0.0315 | 0.1908 |
| xvector_4090 | 10 | 54 | 1007 | 1211 | 0.0228 | 0.1883 |
| xvector_4090 | 12 | 54 | 1012 | 1211 | 0.0168 | 0.1792 |
| xvector_4090 | 16 | 54 | 1016 | 1211 | 0.0256 | 0.1833 |
| xvector_4090 | 20 | 54 | 1021 | 1211 | 0.0255 | 0.2395 |
| xvector_4090 | 24 | 54 | 1004 | 1211 | 0.0229 | 0.1899 |
| xvector_4090 | 32 | 54 | 1004 | 1211 | 0.0229 | 0.1908 |
| orig_3090 | all | 486 | 1043 | 10899 | 0.2550 | 0.9661 |
| xvector_4090 | all | 486 | 9010 | 10899 | 0.0235 | 0.2002 |

## 10. Clean subset: xvector_4090 short + medium, corpus WER (no_intro) by NFE
(long xvector clips are all capped at 12.8 s, so they are left out; max duration in this subset: 10.72 s)

| nfe | clips | ref words | errors | corpus WER | unfinished clips |
|---|---|---|---|---|---|
| 4 | 36 | 411 | 11 | 0.0268 | 0 |
| 6 | 36 | 411 | 16 | 0.0389 | 1 |
| 8 | 36 | 411 | 15 | 0.0365 | 0 |
| 10 | 36 | 411 | 15 | 0.0365 | 1 |
| 12 | 36 | 411 | 13 | 0.0316 | 2 |
| 16 | 36 | 411 | 19 | 0.0462 | 2 |
| 20 | 36 | 411 | 15 | 0.0365 | 0 |
| 24 | 36 | 411 | 15 | 0.0365 | 0 |
| 32 | 36 | 411 | 11 | 0.0268 | 1 |
| all | 324 | 3699 | 130 | 0.0351 | 7 |

## 11. intro_text on xvector_4090
- xvector clips with non-empty intro_text: 0

## 12. Corpus CER (total character errors / total reference characters)
- PASS: per-clip cer_full = recomputed char errors / ref chars
- PASS: corpus CER full: 72423 / 120222 = 0.6024 matches run info
- PASS: per-clip cer_no_intro = recomputed char errors / ref chars
- PASS: corpus CER no_intro: 68318 / 120222 = 0.5683 matches run info

Overall: CER no_intro 0.5683, full 0.6024

### By run_id
| run_id | clips | ref chars | CER no_intro | CER full | WER no_intro |
|---|---|---|---|---|---|
| orig_3090 | 486 | 60111 | 0.9567 | 1.0250 | 0.9661 |
| xvector_4090 | 486 | 60111 | 0.1799 | 0.1799 | 0.2002 |

### By nfe
| nfe | clips | ref chars | CER no_intro | CER full | WER no_intro |
|---|---|---|---|---|---|
| 4 | 108 | 13358 | 0.5884 | 0.6411 | 0.6007 |
| 6 | 108 | 13358 | 0.5770 | 0.6149 | 0.5904 |
| 8 | 108 | 13358 | 0.5454 | 0.5943 | 0.5545 |
| 10 | 108 | 13358 | 0.5380 | 0.5713 | 0.5479 |
| 12 | 108 | 13358 | 0.5463 | 0.5683 | 0.5516 |
| 16 | 108 | 13358 | 0.6130 | 0.6538 | 0.6350 |
| 20 | 108 | 13358 | 0.5835 | 0.5979 | 0.6111 |
| 24 | 108 | 13358 | 0.5844 | 0.6028 | 0.6061 |
| 32 | 108 | 13358 | 0.5383 | 0.5774 | 0.5512 |

### By run_id x nfe
| run_id | nfe | clips | ref chars | CER no_intro | CER full | WER no_intro |
|---|---|---|---|---|---|---|
| orig_3090 | 4 | 54 | 6679 | 0.9742 | 1.0797 | 0.9835 |
| orig_3090 | 6 | 54 | 6679 | 0.9545 | 1.0304 | 0.9587 |
| orig_3090 | 8 | 54 | 6679 | 0.9171 | 1.0147 | 0.9182 |
| orig_3090 | 10 | 54 | 6679 | 0.9063 | 0.9728 | 0.9075 |
| orig_3090 | 12 | 54 | 6679 | 0.9232 | 0.9672 | 0.9240 |
| orig_3090 | 16 | 54 | 6679 | 1.0585 | 1.1401 | 1.0867 |
| orig_3090 | 20 | 54 | 6679 | 0.9723 | 1.0010 | 0.9827 |
| orig_3090 | 24 | 54 | 6679 | 0.9966 | 1.0332 | 1.0223 |
| orig_3090 | 32 | 54 | 6679 | 0.9075 | 0.9856 | 0.9116 |
| xvector_4090 | 4 | 54 | 6679 | 0.2026 | 0.2026 | 0.2180 |
| xvector_4090 | 6 | 54 | 6679 | 0.1994 | 0.1994 | 0.2221 |
| xvector_4090 | 8 | 54 | 6679 | 0.1738 | 0.1738 | 0.1908 |
| xvector_4090 | 10 | 54 | 6679 | 0.1698 | 0.1698 | 0.1883 |
| xvector_4090 | 12 | 54 | 6679 | 0.1693 | 0.1693 | 0.1792 |
| xvector_4090 | 16 | 54 | 6679 | 0.1674 | 0.1674 | 0.1833 |
| xvector_4090 | 20 | 54 | 6679 | 0.1948 | 0.1948 | 0.2395 |
| xvector_4090 | 24 | 54 | 6679 | 0.1723 | 0.1723 | 0.1899 |
| xvector_4090 | 32 | 54 | 6679 | 0.1692 | 0.1692 | 0.1908 |

### Clean subset: xvector_4090 short + medium, by nfe
| nfe | clips | ref chars | CER no_intro | WER no_intro |
|---|---|---|---|---|
| 4 | 36 | 2271 | 0.0119 | 0.0268 |
| 6 | 36 | 2271 | 0.0163 | 0.0389 |
| 8 | 36 | 2271 | 0.0172 | 0.0365 |
| 10 | 36 | 2271 | 0.0189 | 0.0365 |
| 12 | 36 | 2271 | 0.0189 | 0.0316 |
| 16 | 36 | 2271 | 0.0238 | 0.0462 |
| 20 | 36 | 2271 | 0.0176 | 0.0365 |
| 24 | 36 | 2271 | 0.0181 | 0.0365 |
| 32 | 36 | 2271 | 0.0132 | 0.0268 |
| all | 324 | 20439 | 0.0173 | 0.0351 |

## 8. clips.csv hash
- PASS: clips.csv sha256 3788f07cd0dff2d05d619e12ed4efc4e371a78a854e5061261da332abbdca872 (start: 3788f07cd0dff2d05d619e12ed4efc4e371a78a854e5061261da332abbdca872)

FAILED CHECKS: none
