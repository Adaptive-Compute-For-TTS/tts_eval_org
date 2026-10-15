import json, glob, os
from asr import transcribe
from metrics import compute_wer, corpus_wer
prompts = {p["id"]: p for p in json.load(open("prompts/benchmark_prompts_v1.json"))}
rows = []
for f in sorted(glob.glob("runs/human_arush/audio/*.wav")):
    pid = os.path.basename(f)[:-4]
    r = compute_wer(prompts[pid]["text"], transcribe(f)); rows.append(r)
    print(pid, f"{r['wer']:.2f}", "|", r["hyp_norm"])
print(corpus_wer(rows))
