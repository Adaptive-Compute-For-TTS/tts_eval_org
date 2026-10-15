Hi Atharv,

WER for all 972 clips is done. Attached: `clips.csv` (your `wer` column filled in, 0-1 per clip),
`wer_run_info.json` (ASR model, versions, settings, normalization) and `intro_and_cut_findings.md` (details).

**Does WER show the orig_3090 endings cut off at 9.12 s? Yes, clearly.** orig clips at 9.12 s miss on average 22
words at the end, and 92% are unfinished. Compared with xvector at the same prompt and NFE, orig misses 1.5 more
end words on short prompts, 15.7 on medium and 32 on long; on 14% / 69% / 87% of short / medium / long orig clips
none of the sentence is heard.

**Why: every orig_3090 clip starts with an intro the README doesn't mention.** The model first says "Hey, Adam
here. Let's create something that feels real, sounds human, and connects every time.", which ends at about 8.0 s
(median), leaving little room for the prompt. It's in 481 of 486 orig clips: the other 5 are the 4 silent clips and
one (p035 NFE 16) that blends it into "Hello, my name is Adam here." It's in no xvector clip.
- Cause: that sentence is the dots.tts README's sample transcript, and it was the `reference_text` for
  `my_files/abhi1.wav`, but abhi1.wav actually says "Hello, my name's Obby and this is a voice test." The orig run
  used continuation cloning (the script before `--voice-conditioning` existed), which sends prompt_text + text to
  be spoken, so the mismatch likely makes the model speak the intro (the p035 clip blending both sentences
  supports this). 5 orig clips also repeat the intro mid-clip.
- Cap: in continuation mode the reference audio shares the 80-patch `--max-generate-length` budget, leaving about
  57 patches (9.12 s) for orig (exact patch count unverified). xvector's long clips are capped too, at 12.8 s.
- 41 orig clips are shorter than 9.12 s (7.52-8.96 s), unlike what the README says.

`wer` is reported with the intro ignored (`wer_version` = no_intro); the full-version columns, where it counts as
errors, are included too. Which do you want as official?

**Recommendations:** fix `reference_text` to match abhi1.wav and rerun orig_3090; raise `--max-generate-length`
for both runs. Until then, use xvector short + medium prompts for NFE vs quality (none hit the cap; 36 clips,
411 reference words per NFE, so 0.01 is about 4 words):

| NFE | 4 | 6 | 8 | 10 | 12 | 16 | 20 | 24 | 32 |
|---|---|---|---|---|---|---|---|---|---|
| WER | 0.027 | 0.039 | 0.036 | 0.036 | 0.032 | 0.046 | 0.036 | 0.036 | 0.027 |

**Numbers.** WER = (substitutions + deletions + insertions) / reference words, after normalization. Corpus WER
(total errors / total reference words): 0.583 with the intro ignored (orig 0.966, xvector 0.200), 0.709 with it
counted. 12 clips were capped at 1.0 in `wer`; real values are in `wer_uncapped`. The 4 silent clips are kept at
1.0: orig_3090 p036 NFE 6, and p018, p034, p045 NFE 8.

**ASR:** faster-whisper 1.2.1, Whisper "small", int8, CPU, English, beam 5, temperature 0 (deterministic). Small
is less accurate than large-v3, so NFE comparisons are sound but absolute WER is approximate; I can rerun with
large-v3 on a GPU. **Normalization:** Whisper EnglishTextNormalizer plus a few format-only rules (e.g. "Jan" ->
january, "door frame" -> doorframe), applied to both texts; all are listed in `wer_run_info.json`.

Extra columns in `clips.csv`:
- `transcript`: Whisper's raw transcript.
- `cer`: character error rate, capped at 1.0. `wer_uncapped` / `cer_uncapped`: without the cap.
- `wer_version`: which version fills `wer`/`cer` (no_intro).
- `missing_end_words`: reference words after the last correctly heard word (the cut-off measure).
- `heard_ref_words`, `heard_errors`, `wer_heard`: WER over the part of the sentence before the cut (empty if nothing was heard).
- `intro_text`: transcript words set aside as intro.
- `*_full` / `*_no_intro`: wer, cer, substitutions, deletions, insertions, trailing deletions, missing end words per version.
- `ref_words`, `ref_norm`, `hyp_norm`: reference word count and the normalized texts compared.
- `duration_s`, `asr_status`: clip length; "ok" or why the clip wasn't transcribed (silent).
