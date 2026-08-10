"""QLoRA SFT on the assembled dataset (Unsloth).

Runs inside the official unsloth/unsloth Docker image (Blackwell-ready) on the
training GPU; not meant for the dev machine. Loss is masked to the assistant
turn only. Saves the LoRA adapter, a merged fp16 model and optionally GGUF Q4.

  python src/train/sft.py --config src/train/configs/qwen3-1.7b.json [--gguf]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--data", type=Path, default=Path("data/dataset"))
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument("--gguf", action="store_true", help="also export GGUF q4_k_m")
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    run_dir = args.out / cfg["name"]

    # unsloth must be imported before trl/transformers to apply its patches
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import train_on_responses_only

    from datasets import load_dataset
    from trl import SFTConfig, SFTTrainer

    model, tokenizer = FastLanguageModel.from_pretrained(
        cfg["base_model"],
        max_seq_length=cfg["max_seq_len"],
        load_in_4bit=True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg["lora_r"],
        lora_alpha=cfg["lora_alpha"],
        lora_dropout=0,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    def to_text(row):
        return {"text": tokenizer.apply_chat_template(
            row["messages"], tokenize=False, add_generation_prompt=False,
            **cfg.get("template_kwargs", {}))}

    data = load_dataset("json", data_files={
        "train": str(args.data / "train.jsonl"),
        "val": str(args.data / "val.jsonl"),
    })
    data = data.map(to_text, remove_columns=["messages"])
    # drop the few giant outliers instead of truncating mid-answer; the eval
    # pass materializes full fp32 logits, so cap val harder (12k-token val
    # examples OOM the 16 GB card at evaluation time)
    eval_cap = min(cfg["max_seq_len"], 8192)
    before = {k: len(d) for k, d in data.items()}
    data["train"] = data["train"].filter(
        lambda r: len(tokenizer(r["text"]).input_ids) <= cfg["max_seq_len"])
    data["val"] = data["val"].filter(
        lambda r: len(tokenizer(r["text"]).input_ids) <= eval_cap)
    for k, cap in (("train", cfg["max_seq_len"]), ("val", eval_cap)):
        if (n := before[k] - len(data[k])):
            print(f"{k}: dropped {n} examples over {cap} tokens")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=data["train"],
        eval_dataset=data["val"],
        args=SFTConfig(
            output_dir=str(run_dir / "checkpoints"),
            dataset_text_field="text",
            max_seq_length=cfg["max_seq_len"],
            per_device_train_batch_size=cfg["batch_size"],
            per_device_eval_batch_size=1,  # full-seq logits at vocab 152k OOM above this
            gradient_accumulation_steps=cfg["grad_accum"],
            num_train_epochs=cfg["epochs"],
            learning_rate=cfg["lr"],
            warmup_ratio=0.05,
            logging_steps=10,
            eval_strategy="epoch",
            save_strategy="epoch",
            bf16=True,
            seed=42,
            report_to="none",
        ),
    )
    # mask the prompt: loss only on the assistant span
    trainer = train_on_responses_only(
        trainer,
        instruction_part="<|im_start|>user\n",
        response_part="<|im_start|>assistant\n",
    )
    trainer.train()

    model.save_pretrained(str(run_dir / "adapter"))
    tokenizer.save_pretrained(str(run_dir / "adapter"))
    model.save_pretrained_merged(str(run_dir / "merged"), tokenizer,
                                 save_method="merged_16bit")
    if args.gguf:
        model.save_pretrained_gguf(str(run_dir / "gguf"), tokenizer,
                                   quantization_method="q4_k_m")
    print(f"done: {run_dir}")


if __name__ == "__main__":
    main()
