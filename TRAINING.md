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

- **Tuned qwen2.5 on held-outs (partial, lexical metrics):** the body-field
  collapse is FIXED - solution 0.05 -> 0.855 (DeepSeek few-shot ceiling was
  0.82), description 0.39 -> 0.755, detection_result 0.14 -> 0.683, impact
  0.794, recall 0.947, retries 55 / unrecovered 22 over 994 findings.
  insight lagged (0.15) - inspect per-scanner. Numbers are cross-set vs the
  few-shot study until base-on-heldout lands.
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

## 6c. Dataset v2 + final retrain (one batch, planned)

All fixes land in ONE dataset regeneration + ONE qwen2.5 retrain (~1h30):

1. Production chunking: pack examples as 1-4 blocks per call with combined
   `{"items":[...]}`, mirroring the tool's chunker (user request; removes the
   train/serve mismatch class entirely).
2. log_method gold parsed from the block's own `Log Method:` section
   (deterministic, like build_references); regenerate held-out baselines.
3. Whatever the cvss/schema test decides (serving flag and/or gold tweak).

Then: GGUF re-export, re-evaluate on held-outs, CPU cost, gate.

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
- [ ] Base qwen2.5 on held-outs (`base-q25` container running on the 5080)
- [x] cvss/schema test done: schema stays ON for the champion (see 6b);
      cvss root cause moves to the v2-retrain re-check
- [ ] Full tuned-vs-base table (after the two above; lexical metrics first,
      bertscore/nli at closing time)
- [ ] Dataset v2 + final retrain (see 6c)
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
