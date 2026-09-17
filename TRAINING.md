# Training process

How the MulitaMiner embedded-model training was assembled and run. Companion
to the README (layout/commands); this is the record of what was done and why.

Terminology: the pre-training comparison study ran the models **few-shot**
(the tool's prompts carry worked examples; no weight updates), not zero-shot;
"base" rows in the post-training tables refer to that regime.

## Environment (reproducibility record)

| Component | Version |
| --- | --- |
| GPU box | Ubuntu 26.04 LTS, kernel 7.0.0-28-generic, shared multi-user host |
| GPU | NVIDIA GeForce RTX 5080, 16 GB VRAM (Blackwell, sm_120) |
| NVIDIA driver | 595.80 (driver-side CUDA 13.2) |
| Training image | `unsloth/unsloth` - Unsloth 2026.5.9, Torch 2.10.0+cu128, CUDA toolkit 12.8, Triton 3.6.0, Python 3.12 |
| Fine-tuning | SFT with QLoRA (Unsloth `FastLanguageModel` + TRL `SFTTrainer`, transformers 4.57.6; recipe in section 5) |
| Serving | Ollama, `ollama/ollama` container, named volume `ollama` -> `/root/.ollama`, `--gpus all`, bound to 127.0.0.1:11434. The container sets no OLLAMA_CONTEXT_LENGTH (an earlier note here claimed 16384; `docker inspect` on 2026-09-13 shows it absent). It does not need to: the tool sends `num_ctx` per request. Identify the runtime by the image tag, not `/api/version`: the v0.32.15 Windows build reports "0.32.5" there. Ran 0.32.15 through 2026-09-13; pinning 0.34.0 for the 6g re-runs. |
| Tool image | `mulita-mulita:latest` (Python 3.11-slim + uv; no eval group) |
| Evaluation | dev PC (Windows 11, Python 3.11 venv) and, for GPU bertscore, the unsloth image with `uv sync --group eval` |

Training never touches Ollama (Unsloth only); Ollama serves every few-shot
and tuned-model evaluation of this phase. Not to be confused with the WTICG
artifact's Ollama 0.30.0 (old repo, separate experiment).

## 1. Gold labels: the scanner's own export, never hand-made

Each scanner contributes (PDF, machine export) pairs; the export is parsed
into targets by a `LabelSource` and paired to the tool's segmented PDF blocks:

| Scanner | Gold source | Pairing key | Verified vs eval xlsx |
| --- | --- | --- | --- |
| OpenVAS | vulnnet campaign CSV (129 reports) | host + NVT name | (July, pairing + containment) |
| Qualys | scan CSV export | host + QID | 100% all fields |
| Nessus | "Vulnerabilities by Host" HTML | host + plugin id | 100% all fields |
| ZAP | XML report | alert name | 100% text fields |

Verification = `verify/source_vs_baseline.py`: every parsed target compared
field-by-field against the xlsx baselines previously derived from the same
exports. Mapping decisions it enforced: Qualys references = CVE ID column
only; ZAP references gain `CWE n`/`WASC n` (skipping `-1`); ZAP instance
`output` <- `otherinfo`; Nessus Synopsis -> description, Description -> insight.

## 2. Train/eval separation (`heldout.json`)

- **Held-out reports** (eval only, scanner-export baselines):
  OpenVAS juice-shop / raesene_bwapp / wordpress_4.9; Qualys scan-b;
  Nessus scan-b; ZAP JuiceShop / bWAPP / JBoss7.
- **Denied stems**: the second campaign bwapp (same-scanner app duplicate),
  Tenable + Acunetix (no machine gold; Tenable is the unseen-scanner cut,
  Acunetix is out of the thesis benchmark), the 3 legacy hand-made OpenVAS
  baselines.
- **Eval-only hosts**: the held-out apps' hosts, denied across ALL scanners,
  so juice-shop and bwapp are never seen in training under any scanner and
  give a clean cross-scanner comparison (OpenVAS held-out + ZAP held-out +
  Tenable unseen on the same app).
- Cross-scanner overlap on other hosts is allowed by design: matched hosts
  carry largely distinct finding sets (different detection databases).
- `resources/` xlsx are frozen as the historical few-shot test set; tuning
  evaluation runs against `data/heldout/` only.

## 3. Input-faithfulness trim

Exports can carry text the PDF never renders (Qualys "QID Detection Logic"
paragraphs, Nessus plugin outputs truncated by the PDF). Training on it
teaches hallucination; scoring against it caps every model below 1.0. So
`trim_target` removes non-contained paragraphs (containment >= 0.80 per
paragraph) from BOTH training labels and held-out baselines. Applied counts:
457 paragraphs in training, 240 (Qualys scan-b) + 67 (Nessus scan-b) in the
held-out baselines.

## 4. Dataset

`build_dataset.py --sources all` -> 6841 examples (train 6187 / val 654),
136 reports: OpenVAS 5459, Qualys 910, Nessus 381, ZAP 89. Each example is
the production-identical conversation: system = the tool's scanner prompt
(snapshotted + hashed), user = one rendered `### BLOCK`, assistant = the gold
`{"items": [...]}`. Provenance lives in `data/dataset/dataset_report.md`
(the only dataset artifact under version control).

## 5. Fine-tuning recipe

- QLoRA 4-bit (Unsloth), r=32 alpha=32, on all attention + MLP projections;
  ~2.3% of weights trained.
- Loss masked to the assistant turn (`train_on_responses_only`).
- Chat template from the base model; qwen3 formatted with
  `enable_thinking: false` (thinking measured counterproductive under
  json_schema decoding in the few-shot study).
- `max_seq_len` 8192; examples over it are dropped (44 train + 3 val), never
  truncated mid-answer.
- 2 epochs, lr 2e-4, effective batch 16, eval per epoch.
- Two finalists from the few-shot study: **qwen3-1.7b** (primary) and
  **qwen2.5-1.5b** (control; also the stronger base on OpenVAS description,
  see the study notes) - the post-training comparison decides.

## 6. Running on the RTX 5080 (Docker-only box)

Official `unsloth/unsloth` image (Blackwell-ready). Flags that matter, each
learned the hard way:

- `--entrypoint python`: the image's default entrypoint boots a
  jupyter/studio stack via supervisord and never runs the given command.
- `--user root`: the image's `unsloth` user cannot write to the mounted repo
  (uid mismatch) - compiled-cache creation fails otherwise.
- `-e PYTORCH_ALLOC_CONF=expandable_segments:True`: reduces fragmentation on
  the 16 GB card.
- Config `batch_size 1 x grad_accum 16` (same effective batch): batch 2
  OOMed on long-sequence batches (fused-loss logits at vocab 152k).
- `per_device_eval_batch_size=1`, eval per epoch: the eval pass OOMed at the
  default batch 8 after 100 clean training steps.

```bash
docker run --gpus all -v ~/mulita-extractor-training:/w -w /w -d --name train-<x> \
  --user root --entrypoint python \
  -e PYTORCH_ALLOC_CONF=expandable_segments:True \
  unsloth/unsloth src/train/sft.py --config src/train/configs/<model>.json
```

Measured on the 5080: ~6s/step, 768 steps, eval pass 651 examples in ~1.5 min
-> ~1h30-2h per model (qwen2.5-1.5b).

## 6b. Findings from the first evaluation round (2026-08-09/10)

- **FINAL tuned-vs-base table (same 8 held-outs, lexical metrics, 1 run):**
  tuned qwen2.5 beats its base on 14 of 17 fields. Headlines: solution
  0.006 -> 0.855 (DeepSeek few-shot ceiling was 0.82), detection_method
  0.019 -> 0.685, references 0.112 -> 0.731, description 0.409 -> 0.755,
  product_detection_result 0.234 -> 0.902, recall 0.860 -> 0.947,
  unrecovered 40 -> 22. Weak/regressed (v2 re-check list): insight 0.15,
  cvss 0.36, instances 0.58 -> 0.42 (ZAP, n=22); log_method ruler-blind.
  Aggregation script: weighted measured_mean over evaluation.json files.
- **Tuned qwen3 degenerates under constrained decoding** (repetition loops,
  6x slower, JSON truncation); clean free-form. Tuned qwen2.5 tolerates the
  grammar. Model dropped (see decision below); partial runs kept as evidence
  (`output_heldout/mulita-qwen3-1.7b{,-schema}` on the box).
- **Schema is REQUIRED for tuned qwen2.5** (opposite of qwen3): the wordpress
  no-schema test failed nearly every first-pass chunk (JSONDecode/Validation)
  where the with-schema run was clean (54/54). Champion serves WITH
  json_schema. The two tuned models have opposite relationships with
  constrained decoding - thesis finding.
- **cvss-null anomaly (tuned q25, OpenVAS, ~55%):** block header shows the
  score, severity extracted right, cvss=null. Training gold had cvss ~100%.
  Grammar-escape hypothesis WEAKENED by the no-schema test (removing the
  grammar made everything worse, not cvss better). Current suspect:
  multi-block chunk dilution (later items losing fields) - which dataset v2's
  production chunking directly addresses. Re-check cvss after the v2 retrain.
- **log_method gold bug:** the campaign CSV has no Log Method column, so
  gold AND held-out baseline say empty while the production prompt says fill;
  the model fills with real block content and scores 0 on 104 measured pairs.
  Ruler-blind field - ignore its scores for now.

## 6c. Dataset v2 + final retrain (one batch, IMPLEMENTED)

All fixes in one dataset regeneration + one qwen2.5 retrain (~1h30):

1. Production chunking: examples are now whole chunks (the tool's own
   `pack` at `max_vulns_per_chunk` / 8000-token budget + `render_chunk`),
   assistant answers every block of the chunk in one `{"items":[...]}`.
   Removes the train/serve mismatch class; suspected cvss-null cause.
2. log_method gold parsed from the block's own `Log Method` section
   (`parse_log_method` in the openvas source); held-out baselines
   regenerated with it.
3. Serving: schema stays ON (decided by the wordpress test).

Config: `src/train/configs/qwen2.5-1.5b-v2.json` (max_seq_len 12288 for the
longer chunk examples; outputs to `outputs/mulita-qwen2.5-1.5b-v2`).
IMPORTANT for the v2 evaluation: baselines changed (log_method filled), so
re-run `evaluate` for the v1/base outputs against the NEW baselines before
comparing - extractions are reusable, scores are not.

**v2 RESULTS (same 8 held-outs, new baselines, lexical metrics, 1 run):**
v2 wins 12 of 18 fields plus coverage/contract and fixes all three v1
pendings - cvss 0.36 -> 0.79 (openvas nulls 55% -> 22%; chunk-dilution
hypothesis confirmed), insight 0.15 -> 0.56, instances 0.42 -> 0.84,
port/protocol ~0.87, detection_method 0.80, severity 0.945, recall 0.965,
unrecovered 19. Cost: prose regressed - description 0.755 -> 0.585, solution
0.855 -> 0.777, detection_result 0.68 -> 0.63, category 0.50 -> 0.35 (still
far above base everywhere). log_method now measurable: 0.404 (v1 0.087 with
its empty-gold training). **CHAMPION: v2.**

**v3 (mixed shapes, union design):** the two training shapes teach
complementary skills (single-block -> prose depth; production chunks ->
multi-item structure). v3 trains on BOTH: every record appears once as a
single-block example and once inside its production chunk (8740 examples =
6841 singles + 1899 chunks); 1 epoch keeps total content exposure equal to
v2's 2 epochs.

Format balance - two different counts, don't confuse them:
- By EXAMPLES, singles are ~78% of the jsonl (a 4-finding report yields 4
  single examples + 1 chunk example). This only governs how often the model
  sits in a 1-block context during training.
- By LEARNING SIGNAL it is exactly 50/50 by construction: loss is masked to
  the assistant answer, and each record's answer is written exactly once in
  each shape - so the gradient mass per format is 1:1 (the chunk example
  carries N answers at once).
If the v3 table shows the balance leaning one way, the ratio (duplicate
chunks / subsample singles) is the next knob; the token math above is the
guide.

**Candidate v4 (noted for Bia, time is not a constraint): mixed dataset, 2
epochs.** Mechanism: v3's mix gave each skill HALF its specialist's dose
(chunk practice 1899 passes vs v2's 3798; single practice 6841 vs v1's
13682). v4 = same mixed dataset x 2 epochs -> every record gets the FULL v1
dose (2 single passes) AND the full v2 dose (2 chunk passes). Overfit risk
rises (4 exposures vs 2), watched by eval_loss across epochs + the novel-NVT
cut. One-command run: config epochs=2 clone of qwen2.5-1.5b-v3.json, ~2h30.
Decide after the v3 table: if v3 degrades contract vs v2, the half-dose
hypothesis is confirmed and v4 is the test.

**Timing corrections and mechanics (measured on the bwapp stress report):**
- Tuned models are slower than base mostly because they EMIT ~3x more output
  tokens (60k base vs ~180k tuned): the base rushes by leaving fields empty.
  Generation time ~ output tokens; retries amplify because each retry
  regenerates long answers. Retry counts themselves are similar (34-42).
- v3's 3340s on bwapp is CONFOUNDED by the shared-box CPU contention window
  (throughput collapsed to 45 tok/s vs 137-155 for v1/v2, with fewer output
  tokens than v1); exclude v3 timing from comparisons - its contract numbers
  remain valid.
- bwapp hurts every version the same way: runs of near-clone findings
  (PHP/Apache version families) packed 4-per-chunk make the model shuffle
  block_ids (v1: 234 dup, v2: 182 unknown in flight); v1/v2 win by
  CONVERGING in retries (3-4 lost), not by being clean first-pass.

**Candidate v5 (id-discipline; only if v4 still trips on clones):** two
assembler-level levers - (1) shuffle block order inside training chunks
(kills the positional "first answer = first id" shortcut, forcing ids to
bind to content); (2) adversarial packing: build some chunks from near-clone
sibling blocks (same NVT family, adjacent versions - the campaign PHP/Apache
reports have such runs), practicing exactly the bwapp failure case.

**v4 RESULTS - CHAMPION (Bia's decision).** Full-dose paid off: best of the
series on 8 fields including the thesis-central body fields - description
0.827 (record, +42% over v2), insight 0.672, detection_result 0.861,
detection_method 0.922, product_detection_result 0.966, references 0.739,
severity 0.962 - with contract back at v2 level (unrecovered 20 vs 19) and
eval_loss still falling across epochs (0.0017 -> 0.00081; no overfit at 4
exposures). Novel-NVT cut, best of the series: solution 0.997 / description
0.930 on never-seen content. Costs, honestly: recall 0.934 vs v2's 0.965
(~31 findings), cvss 0.552 vs 0.791, port/protocol ~0.76, instances 0.658.
v2 remains the coverage/structured-fields runner-up; single-run caveat
applies to small deltas. `category` swings wildly across versions
(0.50 -> 0.35 -> 0.96 -> 0.35) - investigate separately (small-n qualys
field). Served as `mulita-qwen2.5-1.5b-v4` (schema ON); GGUF at
`outputs/mulita-qwen2.5-1.5b-v4/gguf_gguf/`. v5 stays conditional.

**Noted, not implemented (Bia's call): deterministic post-pass for
mechanical fields.** OpenVAS cvss sits verbatim in the block header
("Critical (CVSS: 9.8)") and port/protocol are already captured
deterministically by segmentation into the block context - yet all three are
filled by the LLM today (host is the only pipeline-filled field). A ~20-line
post-pass could guarantee them (~1.0 for every model), mooting the v4 cvss
regression; the trade is that those fields would stop measuring the LLM in
comparative tables. Revisit at tool-polish time; cvss/port/protocol series
numbers stay as the "before the annotator" record.

## 6e. Memorization control (learned vs memorized)

Evidence stack that the champion learned the task rather than the data:

1. eval_loss falls across epochs on every run (no train/val divergence);
   caveat: the val split shares NVTs with train, so this alone is weak.
2. Held-out reports (stems + hosts denied from training) score high.
3. **Novel-NVT cut (the direct memorization test):** held-out v2 pairs split
   by whether the finding's name appeared anywhere in training gold.
   Seen (n=863) vs novel (n=96) token_f1: description 0.583 vs 0.606,
   solution 0.756 vs 0.945, impact 0.770 vs 0.969, insight 0.563 vs 0.518.
   No collapse on never-seen content - the model extracts, it does not
   recite. (Novel scoring higher likely reflects simpler advisory texts in
   that subset; n=96 supports "no collapse", nothing finer.)
   Per-scanner decomposition of the 96 (Bia's challenge): nessus 51 (novel
   desc+sol 0.657), qualys 38 (0.925), zap 4, openvas 3 - the cut spans two
   major formats, NOT nessus-only; but novel-within-OpenVAS is under-tested
   (n=3: the 126 trained campaign reports cover nearly the whole NVT space
   of the held-outs). The Tenable unseen-scanner cut is the strong-form
   answer: there, all findings AND the format are novel.
4. **Unseen-scanner cut - DONE, and it is the strongest result.** v4 on three
   scanners absent from all training (Tenable, Acunetix), vs base and DeepSeek
   (recall / description bertscore / solution bertscore):

   | report (unseen) | base qwen2.5 | v4 | DeepSeek |
   | --- | --- | --- | --- |
   | Tenable bWAPP | 0.974 / 0.57 / 0.75 | 0.987 / **0.94** / 0.79 | 1.00 / 0.93 / 0.78 |
   | Tenable JuiceShop | - | 1.00 / **0.90** / **0.95** | - |
   | Acunetix testaspnet | 0.667 / **0.00** / 0.00 | 1.00 / **1.00** / 0.75 | 1.00 / 1.00 / 0.97 |
   | Acunetix testphp | 0.731 / 0.15 / 0.00 | 0.577 / **0.97** / 0.76 | 0.885 / 0.99 / 0.80 |

   CONTENT generalizes to unseen scanners at ~cloud level (description
   0.90-1.00, solution 0.75-0.95; base collapses, e.g. testaspnet 0.00->1.00).
   The tuning taught the TASK (find section -> copy to field), not the four
   trained scanners. Recall is robust too (JuiceShop 1.00 despite losing
   instance-blocks: Tenable blocks are instances that consolidate by plugin,
   so block loss != finding loss). Gate (plan section 6): the embedded model
   can be default for content fields even out of distribution.

   Robustness fix found here (MulitaMiner2): a heavy Tenable block (25
   instances -> generation toward the output cap -> call > client deadline)
   raised an UNCAUGHT APITimeoutError that crashed the whole run, discarding
   every extracted block (JuiceShop died 3x). Now timeout is a chunk-level
   failure -> retry -> drop that block as unrecovered, report survives (commit
   2ac492e, with a regression test). Second fix: REQUEST_TIMEOUT_S 600 -> 120
   in settings (a local call slower than 120s is degenerate; 0bf2850). Not the
   chunk size - only 2 timeouts in the JuiceShop run; its 93 min was mostly
   legitimate slow generation (95 calls x ~59s on a 1.5B model + heavy blocks).

Method for (3): normalize names (alphanumeric squeeze), collect all item
Names from the training jsonl, classify each evaluation pair, aggregate
non-vacuous token_f1 per group.

## 6d. Dataset versioning (local, never in git)

Physical copies live side by side under `data/` (gitignored):
`data/dataset-v1` (single-block shape), `data/dataset-v2` (production-chunked,
archived byte-exact from the v2 training), `data/dataset` = the current one.
`build_dataset.py --shape single|chunked|mixed` regenerates any shape;
`mixed` is the v3 recipe. v4 has NO dataset of its own: it retrains on
`data/dataset-v3` with epochs=2 (hyperparameter-only change). Honest note: `dataset-v1` was REgenerated with the
current gold (log_method filled), so it is shape-faithful but not byte-equal
to what the v1 model actually trained on; the exact historical v1 is
reproducible only by checking out the pre-v2 commit. dataset_report.md in git
records provenance per commit.

## 6f. Serving backend changes the output (OPEN, 2026-09-13)

Plugging the v4 GGUF into the tool on the dev PC does NOT reproduce the box
numbers. Same model file, same report (`ZAP_JBoss7`), same trimmed baseline.

| Field | box CUDA 08-11 | box CUDA 09-13 | dev PC 0.34.0 Vulkan | dev PC 0.32.15 Vulkan |
| --- | --: | --: | --: | --: |
| recall | 1.000 | 1.000 | 1.000 | 0.857 |
| name / description / severity | 1.0 | 1.0 | 1.0 | 1.0 |
| solution | 1.0 | 1.0 | 0.574 | 0.673 |
| plugin | 1.0 | 1.0 | 0.0 | 0.0 |
| references | 0.821 | 0.964 | **0.0** | **0.0** |
| instances | 0.577 | 0.849 | **0.0** | **0.0** |
| completion tokens | 3855 | 4561 | 1700 | 1263 |
| wall clock | 30.8s | 25.5s | 167.7s | 1555.6s |

**RESOLVED: the cause is the Modelfile TEMPLATE, not the backend.** The
backend hypothesis was wrong and CPU killed it: forcing `num_gpu: 0` on the
dev PC reproduced the same failure (references 0.0, instances 0.0, plugin
0.0), so Vulkan was not the variable - every dev-PC run shared a different
cause.

`ollama show --modelfile` on the box gave it away. The weights are identical
(both manifests point at blob `sha256-610aa2014ab4...`), but the box model was
created with an explicit Go-template `TEMPLATE` block, while a bare `FROM
model.gguf` makes Ollama fall back to the Jinja chat template in the GGUF
metadata. Two template engines, two different final prompts, and a fine-tuned
model degrades on exactly the most fragile part of its output: the structured
fields.

Re-registering the same GGUF with the box's Modelfile, on the same Radeon via
Vulkan, reproduces the box run to the third decimal:

| Field | box CUDA 09-13 | bare FROM (Vulkan) | box TEMPLATE (Vulkan) |
| --- | --: | --: | --: |
| recall | 1.000 | 1.000 | 1.000 |
| solution | 1.0 | 0.574 | 1.000 |
| references | 0.964 | 0.0 | 0.964 |
| instances | 0.849 | 0.0 | 0.849 |
| plugin | 1.0 | 0.0 | 0.571 |
| completion tokens | 4561 | 1700 | 4517 |

**The model is portable across hardware; it is not portable without its
Modelfile.** The serving recipe is now committed at `serving/Modelfile` and
must ship with any published GGUF. `plugin` at 0.571 vs 1.0 is the one
residual, small enough to be run variance on a 7-finding report; worth a
second look if it persists on a bigger one.

Run-to-run variance on the SAME backend is real but small and non-categorical
(CUDA references 0.821 -> 0.964, instances 0.577 -> 0.849 between 08-11 and
09-13), which is the single-run caveat already declared in RESULTADOS.md. A
flat 0.0 on two fields is not that.

Both Vulkan runs empty the same two fields and break on the same chunk; only
the symptom changes with the version (0.34.0 emitted duplicate block ids and
kept 7/7; 0.32.15 timed out three times and dropped block 6, recall 0.857).

**The tool was not the same version either.** The 2026-08-11 reference runs
ran at MulitaMiner2 commit `1977690` (2026-08-11 09:57 -0300; the first
held-out run starts 09:59). At that commit the per-request deadline was 600s
and a timeout was FATAL: `2ac492e` (making it a chunk failure) landed 21:17
that night and `0bf2850` (600s -> 120s) at 00:48 on the 12th. So run B's
recall drop is partly an artifact of today's 120s deadline and would not have
happened under the 2026-08-11 tool. Run A hit no timeout at all, so its empty
`references`/`instances` is NOT timeout-related - that failure stands on its
own and is the one worth chasing.

To replay 2026-08-11 faithfully, check the tool out at `1977690`. To isolate
the backend against the dev-PC runs above, use the same commit they used
(`main` at `9c827d5`; extraction is untouched between it and the runs).

The box's `mulita-mulita:latest` image is itself from that era: its
`settings.py` has no `REQUEST_TIMEOUT_S` at all (the named setting arrives in
`0bf2850`), and its `llm.py` carries the hardcoded `timeout=600.0`. So the box
has always run with a 5x larger deadline than the dev PC, which is why it
never hit the timeouts seen here. Useful property: a box run measures the
backend without the deadline interfering. Running the tool on the box means
the image, not a checkout - `docker run --rm --network host -v
~/mulita-extractor-training:/training mulita-mulita:latest <subcommand>`,
with the training repo mounted at `/training` (globs must be expanded inside
the container, not by the host shell).

The model dumped the reference list into `solution` as prose and left
`references` and `instances` empty. Not sampling noise: `temperature` is 0.0
and `prompt_tokens` is 7216 on both sides, byte-identical prompt, same
segmentation and packing. What differs is generation: 3855 completion tokens
on the box vs 1700 here.

Chunk 2 of that report (a single block) is where it breaks, and it breaks in
both Ollama versions tried on the AMD card, differently each time:

| Runtime | GPU | Chunk 2 |
| --- | --- | --- |
| 0.32.15 container | RTX 5080 (CUDA) | clean, 3 calls, 30.8s total |
| 0.34.0 (installed) | RX 6600 (Vulkan) | `duplicate block_id 6` x3 |
| 0.32.15 (standalone zip) | RX 6600 (Vulkan) | APITimeoutError at 120s |

Two Ollama versions fail on the same chunk on Vulkan and neither fails on
CUDA, so the suspect is the BACKEND, not the version. One report and one
chunk, so this is a lead, not a conclusion. Consistent with 6b's finding that
this model is unusually sensitive to constrained decoding (schema REQUIRED;
the tuned qwen3 degenerated under grammar) - a backend that computes logits
slightly differently hits a model already near that edge.

Measured end-to-end throughput on the same report (includes model load and
prompt processing, not pure generation speed):

| Environment | completion tokens | duration | tok/s |
| --- | --: | --: | --: |
| RTX 5080, CUDA | 3855 | 30.8s | ~125 |
| RX 6600, Vulkan | 1700 | 167.7s | ~10 |

**Consequence for REQUEST_TIMEOUT_S (tool side).** The tool's 120s per-request
deadline (`settings.py`, a degeneracy detector: "a local call slower than this
is a degenerate generation") assumes box-class throughput. At ~125 tok/s the
profile's 8000 `max_output_tokens` take 64s and fit. At ~10 tok/s they take
800s, so the deadline only allows ~1200 output tokens and kills healthy calls.
Any CPU-only measurement will hit this first. The timeout should move to the
model profile (the shape `context_window` and `max_output_tokens` already
have), keeping 120s as the default so GPU profiles keep the detector; a
CPU-serving profile then declares a value derived from its measured tok/s.

**Provenance gap:** `run.json` records the model key but not the serving
runtime or the backend, so there is no way to prove retroactively which
version and which GPU produced the 2026-08-11 numbers.

**Test matrix to settle it** (same PDF, same baseline, one row at a time):

| # | Runtime | Hardware | Isolates |
| --- | --- | --- | --- |
| A | 0.34.0 | RX 6600 Vulkan | done, diverges |
| B | 0.32.15 | RX 6600 Vulkan | done, diverges (differently) |
| C | 0.32.15 | RTX 5080 CUDA | reproduces 2026-08-11? |
| D | latest | RTX 5080 CUDA | version effect on CUDA |
| E | chosen version | CPU only (`num_gpu: 0`) | embeddability, needs the timeout fix first |

C vs B isolates the backend with the version held constant. D vs C isolates
the version with the hardware held constant. E answers the thesis question
that motivated picking a small model.

## 6g. Re-run plan after the template fix (2026-09-13)

Everything measured before `serving/Modelfile` existed is suspect on the dev
PC side (6f). The v4/base held-out numbers from 2026-08-11 stand: the box
model always had the correct TEMPLATE.

**Frozen configuration for every arm below.** Deviating from any line makes
the runs non-comparable:

| Item | Value |
| --- | --- |
| Serving recipe | `serving/Modelfile` (this repo) - `ollama create mulita-qwen2.5-1.5b-v4 -f serving/Modelfile` |
| Weights | `outputs/mulita-qwen2.5-1.5b-v4.gguf`, blob `sha256-610aa2014ab4...` |
| Ollama | pin **0.34.0** (latest as of 2026-09-05) on every machine, same tag |
| Tool | MulitaMiner2 branch `fix/per-profile-request-timeout` (`adacd63` per-profile timeout + `2cc5d60` runtime provenance in run.json) |
| Reports | the 8 in `data/heldout/*/*.pdf`, 1028 blocks total |
| Models | `mulita-qwen2.5-1.5b-v4` and the base `qwen2.5-1.5b` |
| Command | `./scripts/eval_heldout.sh extract <key>` then `evaluate <out_root>` |

DeepSeek does NOT re-run: the 2026-09-13 pass covers all 8 with recall 0.994,
cost $0.4723. Its only gap is provenance (it ran before `2cc5d60`).

**Arms:**

| # | Hardware | Status | Time (8 reports) |
| --- | --- | --- | --: |
| 1 | RTX 5080, CUDA (box) | **DONE 2026-09-13**, base + v4 | 42 min each (measured) |
| 2 | RX 6600, Vulkan (dev PC) | deferred, Bia runs later | ~3.2h (4.6x box on ZAP_JBoss7) |
| 3 | CPU only (dev PC) | deferred, MEASURE FIRST | unknown |

Timing note: 42 min per model measured on 2026-09-13, against 1.8h
projected from the 2026-08-11 durations. The August figures were inflated,
most likely by contention on the shared box (6c already records one such
window). Use the September numbers for planning.

**Arm 1 results.** Conformance passed on the box before scoring (all five
checks, plugin 1.000). All 16 runs carry `runtime: {server_version 0.34.0,
processor 100% GPU}` - the first runs in this project with provenance.

v4 reproduced itself across a month AND an Ollama major change (0.32.15 ->
0.34.0), same Modelfile:

| Field | 2026-08-11 | 2026-09-13 | delta |
| --- | --: | --: | --: |
| description | 0.827 | 0.827 | -0.000 |
| solution | 0.810 | 0.828 | +0.018 |
| insight | 0.672 | 0.655 | -0.017 |
| impact | 0.784 | 0.773 | -0.011 |
| detection_result | 0.861 | 0.853 | -0.007 |
| references | 0.739 | 0.748 | +0.009 |
| severity | 0.962 | 0.964 | +0.001 |
| instances | 0.658 | 0.737 | +0.079 |
| plugin | 0.898 | 0.848 | -0.050 |
| recall | 0.934 | 0.942 | +0.008 |

Seven of nine fields within +/-0.02, but see 6h: with run-to-run noise now
measured at exactly zero, the two that did move (`instances` +0.079, `plugin`
-0.050) are real effects of the runtime change, not sampling. The rule stays
**"serve it with the Modelfile"** - omitting it destroyed three fields (6f),
an order of magnitude worse - but "changing the runtime moved nothing" was too
strong and is corrected in 6h.

**Cloud ceiling, finally on the same 8 reports.** Regenerate with
`python3 scripts/compare_models.py output_heldout/{qwen2.5-1.5b,mulita-qwen2.5-1.5b-v4,deepseek}`.
token_f1 except where noted; every mean carries its fill rate in parentheses.

Provenance of the columns, so the table travels with it:

| | base and v4 | DeepSeek |
| --- | --- | --- |
| Date | 2026-09-13 | 2026-09-13 |
| Machine | RTX 5080 box (Ubuntu 26.04, driver 595.80, CUDA 13.2) | DeepSeek API |
| Runtime | Ollama **0.34.0**, `ollama/ollama` container, 100% GPU | `deepseek-v4-flash` profile |
| Serving recipe | `serving/Modelfile` (weights blob `sha256-610aa2014ab4...`) | n/a |
| Tool | MulitaMiner2 `fix/per-profile-request-timeout` | same, but extracted before `2cc5d60` |
| Provenance in run.json | yes, `runtime` block on all 16 runs | date and profile key only |
| Conformance | passed before scoring, all 5 checks | n/a |

Reports: the 8 in `data/heldout/*/*.pdf`, 994 baseline findings. One run per
model per report, so small deltas are indicative, not tested.

| Field | base | v4 | DeepSeek |
| --- | --: | --: | --: |
| description | 0.503 (0.62) | 0.827 (0.87) | 0.931 (1.00) |
| solution | 0.004 (0.01) | **0.828** (0.66) | 0.736 (0.94) |
| insight | 0.000 (0.00) | 0.655 (0.57) | 0.999 (0.86) |
| impact | 0.477 (0.31) | **0.773** (0.30) | 0.745 (0.52) |
| detection_result | 0.300 (0.37) | 0.853 (0.84) | 0.986 (0.97) |
| references (set_f1) | 0.144 (0.23) | 0.748 (0.49) | 0.837 (0.63) |
| severity (exact) | 0.803 (1.00) | 0.964 (1.00) | 1.000 (1.00) |
| instances (structural) | 0.596 (1.00) | 0.737 (0.91) | 0.958 (1.00) |
| plugin (exact) | 0.811 (0.97) | 0.848 (0.95) | 1.000 (1.00) |
| RECALL | 0.853 | 0.942 | 0.994 |

Read it as: where v4 answers, it matches the cloud on the body fields
(`solution` 0.828 vs 0.736, `impact` 0.773 vs 0.745) - it just answers less
often (0.66 and 0.30 fill against 0.94 and 0.52). Claiming v4 beats the cloud
on those without the fill rate beside it would be claiming credit for
omission. `insight` is the one honest gap: worse on both axes, 0.655 at 0.57
fill against 0.999 at 0.86.

DeepSeek's column is the 2026-09-13 API pass (8/8, $0.4723). It predates
`2cc5d60`, so it carries the date and the profile key but no runtime block -
declare that asymmetry rather than implying parity.

Arm 3 caveat: measure one mid-size report (`openvas_wordpress_4.9`, 54
blocks, 482s on the box) and project before committing to all 8. It also
needs a profile declaring a large `request_timeout_s` (the reason `adacd63`
exists); at CPU throughput the default 120s kills healthy calls.

Box note: its `mulita-mulita:latest` image predates all of this (no
`REQUEST_TIMEOUT_S`, no runtime block). Rebuild it from the branch above, or
arm 1 produces no provenance and repeats the 2026-08-11 mistake.

**Reporting change to apply before writing any table (from the DeepSeek
comparison):** every field mean ships with its `fill_rate_extraction`. v4
scores `solution` 0.810 but fills it in only 64% of findings, against
DeepSeek's 0.736 at 94% fill - the means are over different denominators and
are not comparable alone. Empty is a legal value (even DeepSeek fills
`impact` only 52% of the time), so emptiness is never an error per record;
only deviation from a known reference is a signal. That is what the
conformance check below is for.

**Conformance check: BUILT** (`scripts/conformance.sh` +
`serving/conformance.json`). Extracts `ZAP_JBoss7`, scores it, compares
against recorded floors, exits non-zero on failure. ~25s on CUDA. Run it
after registering the model, after changing Ollama, and on any new machine.

Verified against both cases on 2026-09-13: the correctly-served model passes
all five checks, the same weights with a bare `FROM` fail four of five. The
one that PASSES on the broken model is `recall` (1.000), which is exactly why
this failure is invisible without it - the headline metric is the one that
notices nothing.

The floors are deliberately loose and `conformance.json` records the
observations they came from (good runs vs bad runs, per check), so the
numbers stay auditable instead of becoming magic constants. It detects a
collapse to zero, not a small regression: two CUDA runs a month apart moved
`references` 0.821 -> 0.964, so an exact-match check would false-alarm.

## 6h. Extraction is deterministic; the runtime is what moves it (2026-09-16)

Two campaigns, one conclusion: **given a fixed environment, this pipeline
produces byte-identical output.** There is no run-to-run noise to average out.

**Warm regime, 80 runs.** `mulitaminer experiment data/heldout --models
mulita-qwen2.5-1.5b-v4 --runs 10` on the box: 10 passes over the 8 held-outs,
6h51 continuous, 24514s active. For every report, all 10 `results.json` share
ONE md5. Durations differ slightly between passes (Nessus 285.42 / 283.56 /
283.53 / 283.58 ...), which is what proves they were 10 real executions and
not cached replays. No idle window above 60s in the whole campaign, so the
5-minute keep_alive never fired and the model stayed resident throughout.

**Cold regime, 5 passes.** `ollama stop` before each, on
`openvas_wordpress_4.9` (54 blocks): all five `results.json` at md5
`284f6111941808cdfe2624afc789c945`. Unloading and reloading the model changes
nothing.

**It is not a caching artifact.** The server log shows `prompt eval time =
73.97 ms / 2046 tokens` with `cached n_tokens = 4`: the whole prompt was
recomputed, essentially nothing reused from the prompt cache (observed on a
sample of tasks, not all ~3600 calls). The model redoes the arithmetic and
lands on the same answer.

**So the 2026-08-11 -> 2026-09-13 deltas are attributable.** Weights identical
(blob `sha256-610aa2014ab4...`), Modelfile identical (box model ID
`e7a4eff77f9b` unchanged across the container swap), hardware identical. The
tool changed by six commits, all inert for extraction: `0bf2850` lowered the
deadline 600s -> 120s but NO call in either campaign came within range (0
timeout warnings on both sides), `9c827d5` only centralised values that were
already 3 and 0.7, and the rest is comments, display, or provenance written
after extraction. What is left is **Ollama 0.32.15 -> 0.34.0**, which accounts
for `instances` +0.079 and `plugin` -0.050.

**Consequences:**

- The RESULTADOS.md limitation "one run per model, no confidence intervals"
  should be replaced, not softened. There is nothing to put an interval
  around. The honest statement is that extraction is deterministic given a
  fixed environment, and that the environment must therefore be declared.
- Single-run comparisons **within one environment** are exact. The v2 vs v4
  gap measured on 2026-08-11 (`cvss` 0.790 vs 0.568, `instances` 0.840 vs
  0.658) is real, not noise. Re-running v2 is still worth 42 minutes, but for
  a different reason: to compare both under the CURRENT runtime, since 0.34.0
  moved `instances` for v4.
- The failure modes are deterministic too. All five cold passes dropped the
  same `block_id 15` duplicate and the same block 16. The near-clone block_id
  confusion is systematic model behaviour, not luck, which is what makes the
  v5 id-discipline idea (6c) an addressable defect.
- Within a fixed environment an exact-match conformance check would work. The
  loose floors in `serving/conformance.json` stay right, because the check
  must survive a runtime upgrade.

## 6i. Why v4 omits: fill-rate analysis (2026-09-17)

Field means hid this because they are computed only over pairs the model
answered. Comparing `fill_rate_extraction` against `fill_rate_baseline` from
the same evaluation.json (same denominator, 8 held-outs, 2026-09-13 runs):

| Field | gold | v4 | DeepSeek | v4 vs gold |
| --- | --: | --: | --: | --: |
| description | 99% | 87% | 100% | -13 |
| solution | 79% | 66% | 94% | -13 |
| insight | 86% | 57% | 86% | **-28** |
| impact | 38% | 30% | 52% | -8 |
| detection_result | 97% | 84% | 97% | -13 |
| references | 61% | 49% | 63% | -12 |
| instances | 100% | 91% | 100% | -9 |
| cvss | 58% | 31% | 59% | **-26** |
| port | 83% | 67% | 86% | -16 |

**DeepSeek tracks the gold almost exactly** on every field (100 vs 99, 86 vs
86, 97 vs 97, 63 vs 61, 100 vs 100). That is the reference behaviour. **v4
under-fills every single field**, by 8 to 28 points. The omission is uniform,
which suggests one mechanism rather than nine field-specific problems.

(An earlier draft of this analysis compared the model against the TRAINING
gold fill rates in `dataset_report.md` and concluded the model was faithfully
reproducing its training distribution. That comparison was wrong: different
report set, different denominator. The table above is the correct one.)

**Where the omission lives.** Joining `results.json` with the baseline xlsx
for `references`, per report:

| Report | omitted | gold has | rate |
| --- | --: | --: | --: |
| openvas_raesene_bwapp (246 blocks) | 94 | 187 | 50% |
| openvas_wordpress_4.9 (54 blocks) | 22 | 35 | 63% |
| Qualys_VulnLab_scan-b (419 blocks) | 3 | 198 | 2% |
| Nessus_VulnLab_scan-b (268 blocks) | 0 | 120 | 0% |
| openvas_bkimminich_juice-shop (18 blocks) | 0 | 12 | 0% |
| the 3 ZAP | 0 | 22 | 0% |

Not a weakness of the field: a weakness on **large OpenVAS reports**. The
small OpenVAS report omits nothing; Qualys, at 419 blocks, omits 2%. And the
model almost never fabricates: 2 invented references in 936 pairs.

**Hypothesis (untested): multi-block chunk dilution.** OpenVAS packs 4
findings per chunk, the most of any scanner, and the two failing reports are
the large ones. This is the same mechanism 6b suspected for the cvss-null
anomaly, and `cvss` is the second-worst field here (-26). If later items in a
chunk lose fields, both are one defect.

**It could not be tested with the artifacts on hand:** `block_id` does not
survive consolidation into `results.json`, so a record cannot be mapped back
to its position inside its chunk. The test is a `--debug` run (which dumps
chunk composition) on `openvas_wordpress_4.9`, about 4 minutes, then checking
whether the omission rate rises with position in the chunk. If it does, the
v5 lever is the packing, not the epochs.

**cvss and port are not pipeline-filled today.** `extraction.py:53` forces
only `host` from the block (`model_validate({**data, "host": block.host})`);
everything else comes from the LLM, including `port` and `protocol`, which
segmentation already captured into the block context and renders into the
prompt. The model is being asked to echo back data the pipeline already
holds, and fills `cvss` in 31% of cases against a gold of 58%.

## 7. Status

- [x] Multi-scanner data engine + verification (qualys/nessus/zap 100% vs xlsx)
- [x] heldout.json contract + eval-only apps
- [x] Input-faithfulness trim (labels + baselines)
- [x] Dataset built: 6841 examples, 4 scanners
- [x] Held-out baselines generated for all 4 scanners (`data/heldout/`)
- [x] SFT script + configs; OOM issues resolved (batch, eval batch)
- [x] qwen2.5-1.5b training run complete (`outputs/mulita-qwen2.5-1.5b`)
- [x] qwen3-1.7b training run (`outputs/mulita-qwen3-1.7b`; eval_loss 0.0038
      -> 0.0027 across epochs, no overfit signal)
- [x] Eval infra: tuned-model profiles, GGUF export script, held-out runbook
- [x] GGUF q4_k_m exports (v1..v4 under `outputs/*/gguf_gguf/`)
- [x] Tuned qwen2.5 extracted + evaluated on held-outs (partial table in 6b)
- [x] Base qwen2.5 on held-outs, evaluated
- [x] cvss/schema test done: schema stays ON for the champion (see 6b);
      cvss root cause moves to the v2-retrain re-check
- [x] Full tuned-vs-base table (6b) + SEMANTIC LAYER CLOSED: bertscore
      computed on GPU for the whole study (10 models, trimmed ruler) and the
      tuned series; rankings and conclusions unchanged everywhere (lexical
      and semantic within ~0.02 across the series; deepseek solution
      0.82 -> 0.78 with the fair ruler). v4 final: description 0.85
      bertscore vs deepseek 0.94.
- [x] Dataset v2 + retrain + evaluation (results in
      6c); GGUF at `outputs/mulita-qwen2.5-1.5b-v2/gguf_gguf/`, served as
      `mulita-qwen2.5-1.5b-v2` (schema ON)
- [x] v3 trained + evaluated (half-dose, see 6c)
- [x] v4 trained + evaluated: **v4 is the CHAMPION** (Bia; results in 6c)
- [ ] Collect loss curves for the record (thesis figure): on the box,
      `docker logs <train-*> | grep -E "eval_loss|train_loss"` for
      train-q25 / train-q3 / train-q25-v2 / train-q25-v3, or the full
      history in `outputs/*/checkpoints/*/trainer_state.json`
- [ ] Novel-NVT memorization cut (6e) is now a STANDARD analysis: run it for
      every new candidate (v3 included) alongside the field table
- [x] Few-shot study re-scored on the trimmed baselines with bertscore
      (GPU batch, Ollama-box; deepseek included after uploading its local
      extractions). Ranking unchanged vs the old ruler; conclusions hold.
- [x] DeepSeek ceiling row: DONE 2026-09-13, all 8 held-outs, recall 0.994,
      $0.4723 total. The old note here was wrong about which reports were
      missing (OpenVAS existed, the 3 ZAP did not, and the Qualys run had
      died mid-way leaving only a run.log)
- [ ] Unseen-scanner cut (Tenable) for the tuned models
- [ ] CPU execution cost: serve the winner's GGUF with inference forced to CPU
      (Ollama `num_gpu: 0`) on the dev PC - a GPU-less machine is not needed,
      the measurement is of the CPU-only path (tok/s, minutes/report).
      BLOCKED on the REQUEST_TIMEOUT_S fix (see 6f): at CPU throughput the
      tool's 120s per-request deadline kills healthy calls, so the run would
      measure the timeout, not the model
- [x] Serving-backend divergence (6f): RESOLVED, it was the Modelfile
      TEMPLATE, not the backend; recipe committed at `serving/Modelfile`
- [x] Re-run arm 1 (RTX 5080, CUDA) per 6g, base + v4, 8 held-outs
- [ ] Re-run arm 2 (RX 6600, Vulkan) per 6g - Bia, later
- [ ] Re-run arm 3 (CPU only) per 6g - measure one report first
- [ ] Rebuild the box's tool image from `fix/per-profile-request-timeout`
      so the re-runs record provenance
- [ ] Deterministic post-pass for cvss/port/protocol (tool side). Confirmed in
      6i: `extraction.py:53` forces only `host` from the block
      (`model_validate({**data, "host": block.host})`), so the LLM is asked to
      echo back `port` and `protocol` that segmentation already captured and
      renders into the prompt, and `cvss` that sits verbatim in the block
      header. It fills cvss in 31% of findings against a gold of 58%. A
      ~20-line pass guarantees these for every model; the trade is that they
      stop measuring the LLM in comparative tables, so keep the v1-v4 series
      as the before-the-annotator record
- [x] Report field means WITH fill_rate_extraction everywhere: the
      evaluate summary table (MulitaMiner2 `1469e4a`) and
      `scripts/compare_models.py`
- [x] Conformance check built and verified both ways (6g)
- [x] Primary model DECIDED: **tuned qwen2.5-1.5b**; qwen3 dropped entirely.
      The tuned qwen3 degenerates under constrained decoding (grammar forces
      it off its trained path; cleaner served free-form but still noisier and
      slower than tuned qwen2.5) and is the larger model. Its partial runs
      stay on disk as evidence of the constrained-decoding finding, but it is
      out of the comparison table and gets no further investment.
- [ ] Conditional on the gate: publish the winner (HF model card, or GitHub
      Release / ollama push) - only needed if the no-GPU profile is to be
      usable by third parties; thesis results do not depend on it
