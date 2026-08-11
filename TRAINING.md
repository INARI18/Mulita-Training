# Training process

How the MulitaMiner embedded-model training was assembled and run. Companion
to the README (layout/commands); this is the record of what was done and why.

Terminology: the pre-training comparison study ran the models **few-shot**
(the tool's prompts carry worked examples; no weight updates), not zero-shot;
"base" rows in the post-training tables refer to that regime.

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
4. Unseen-scanner cut (Tenable) still pending - the distribution-shift test.

Method for (3): normalize names (alphanumeric squeeze), collect all item
Names from the training jsonl, classify each evaluation pair, aggregate
non-vacuous token_f1 per group.

## 6d. Dataset versioning (local, never in git)

Physical copies live side by side under `data/` (gitignored):
`data/dataset-v1` (single-block shape), `data/dataset-v2` (production-chunked,
archived byte-exact from the v2 training), `data/dataset` = the current one.
`build_dataset.py --shape single|chunked|mixed` regenerates any shape;
`mixed` is the v3 recipe. Honest note: `dataset-v1` was REgenerated with the
current gold (log_method filled), so it is shape-faithful but not byte-equal
to what the v1 model actually trained on; the exact historical v1 is
reproducible only by checking out the pre-v2 commit. dataset_report.md in git
records provenance per commit.

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
- [ ] Eval infra ready: tuned-model profiles in the tool, GGUF export script,
      held-out runbook (`scripts/eval_heldout.sh`) - pending first use
- [ ] GGUF q4_k_m export of both
- [x] Tuned qwen2.5 extracted + evaluated on held-outs (partial table in 6b)
- [x] Base qwen2.5 on held-outs, evaluated
- [x] cvss/schema test done: schema stays ON for the champion (see 6b);
      cvss root cause moves to the v2-retrain re-check
- [x] Full tuned-vs-base table (6b; bertscore/nli still pending for closing)
- [x] Dataset v2 + retrain + evaluation: **v2 is the champion** (results in
      6c); GGUF at `outputs/mulita-qwen2.5-1.5b-v2/gguf_gguf/`, served as
      `mulita-qwen2.5-1.5b-v2` (schema ON)
- [ ] v3 training (mixed-shape dataset, union design: every record in both
      shapes, 1 epoch = same 2x exposure as v2; running on the 5080). After
      `done`: register in Ollama -> extract the 8 held-outs -> scp ->
      evaluate -> v3 vs v2 table
- [ ] Collect loss curves for the record (thesis figure): on the box,
      `docker logs <train-*> | grep -E "eval_loss|train_loss"` for
      train-q25 / train-q3 / train-q25-v2 / train-q25-v3, or the full
      history in `outputs/*/checkpoints/*/trainer_state.json`
- [ ] Novel-NVT memorization cut (6e) is now a STANDARD analysis: run it for
      every new candidate (v3 included) alongside the field table
- [ ] Re-score the few-shot study on the trimmed baselines (the corrected
      ruler IS the ruler; no "revised" footnote - no thesis text exists yet).
      DONE: resources/ xlsx trimmed in place via tools/trim_baselines.py
      (MulitaMiner2 c1025ed; 1487 paragraphs across 11 reports, ZAP clean,
      all rows paired). PENDING: batch re-`evaluate` of the SLM copies in
      MulitaMiner2/output_slm_metrics/ with token_f1,rouge_l,bertscore (no
      nli) - Bia wants it on the 5080 (GPU bertscore); needs an eval-capable
      image there (the mulita image ships without the eval group). DeepSeek
      runs need the same re-score for a coherent study table.
      Expect gaps to widen slightly toward good fillers (empty stays 0).
- [ ] DeepSeek ceiling row: deferred (API unavailable). 5 of 8 held-outs can
      be scored for free later (extractions already exist in
      output_experiments; only re-evaluate against the trimmed baselines);
      the 3 campaign OpenVAS held-outs need one small API run
- [ ] Unseen-scanner cut (Tenable) for the tuned models
- [ ] CPU execution cost: serve the winner's GGUF with inference forced to CPU
      (Ollama `num_gpu: 0`) on the dev PC - a GPU-less machine is not needed,
      the measurement is of the CPU-only path (tok/s, minutes/report)
- [x] Primary model DECIDED: **tuned qwen2.5-1.5b**; qwen3 dropped entirely.
      The tuned qwen3 degenerates under constrained decoding (grammar forces
      it off its trained path; cleaner served free-form but still noisier and
      slower than tuned qwen2.5) and is the larger model. Its partial runs
      stay on disk as evidence of the constrained-decoding finding, but it is
      out of the comparison table and gets no further investment.
- [ ] Conditional on the gate: publish the winner (HF model card, or GitHub
      Release / ollama push) - only needed if the no-GPU profile is to be
      usable by third parties; thesis results do not depend on it
