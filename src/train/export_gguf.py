"""Export a finished run to GGUF q4_k_m for Ollama/llama.cpp serving.

Loads the saved merged fp16 model and writes outputs/<name>/gguf/. Runs in the
same unsloth/unsloth image as training (needs the GPU box, not the dev machine).

  python src/train/export_gguf.py outputs/mulita-qwen2.5-1.5b
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    run_dir = Path(sys.argv[1])
    merged = run_dir / "merged"
    if not merged.is_dir():
        raise SystemExit(f"{merged} not found; train first")

    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        str(merged), load_in_4bit=False, dtype=None)
    model.save_pretrained_gguf(str(run_dir / "gguf"), tokenizer,
                               quantization_method="q4_k_m")
    print(f"done: {run_dir / 'gguf'}")


if __name__ == "__main__":
    main()
