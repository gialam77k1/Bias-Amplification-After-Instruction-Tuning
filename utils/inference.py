from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any


def _lazy_imports():
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    return torch, PeftModel, AutoModelForCausalLM, AutoTokenizer


def list_available_pairs(registry: dict) -> dict[str, list[str]]:
    pairs: dict[str, list[str]] = {}
    for item in registry.get("adapters", []):
        pairs.setdefault(item["base_model"], []).append(item["dataset"])
    return {model: sorted(set(datasets)) for model, datasets in pairs.items()}


def find_adapter_entry(registry: dict, base_model: str, dataset: str) -> dict[str, Any]:
    for item in registry.get("adapters", []):
        if item["base_model"] == base_model and item["dataset"] == dataset:
            return item
    raise ValueError(f"No adapter found for {base_model} + {dataset}")


@lru_cache(maxsize=8)
def load_tokenizer(base_model: str):
    _, _, _, auto_tokenizer = _lazy_imports()
    tokenizer = auto_tokenizer.from_pretrained(base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    return tokenizer


@lru_cache(maxsize=8)
def load_base_model(base_model: str):
    torch, _, auto_model, _ = _lazy_imports()
    model = auto_model.from_pretrained(base_model, dtype=torch.float32)
    model.eval()
    return model


@lru_cache(maxsize=16)
def load_tuned_model(base_model: str, adapter_path: str):
    torch, peft_model, auto_model, _ = _lazy_imports()
    base = auto_model.from_pretrained(base_model, dtype=torch.float32)
    base.eval()
    tuned = peft_model.from_pretrained(base, adapter_path)
    tuned.eval()
    return tuned


def generate_text(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 80,
    temperature: float = 0.8,
    top_p: float = 0.95,
    repetition_penalty: float = 1.05,
) -> str:
    torch, _, _, _ = _lazy_imports()
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    generation_kwargs = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": tokenizer.eos_token_id,
        "repetition_penalty": repetition_penalty,
    }

    if temperature <= 0:
        generation_kwargs["do_sample"] = False
    else:
        generation_kwargs["do_sample"] = True
        generation_kwargs["temperature"] = temperature
        generation_kwargs["top_p"] = top_p

    with torch.no_grad():
        output_ids = model.generate(**inputs, **generation_kwargs)

    decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    if decoded.startswith(prompt):
        return decoded[len(prompt) :].strip() or decoded.strip()
    return decoded.strip()


def run_comparison(
    registry: dict,
    base_model: str,
    dataset: str,
    prompt: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    repetition_penalty: float,
) -> dict[str, Any]:
    entry = find_adapter_entry(registry, base_model, dataset)
    adapter_path = str(Path(entry["adapter_path"]).resolve())

    tokenizer = load_tokenizer(base_model)
    base = load_base_model(base_model)
    tuned = load_tuned_model(base_model, adapter_path)

    base_output = generate_text(
        model=base,
        tokenizer=tokenizer,
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
    )
    tuned_output = generate_text(
        model=tuned,
        tokenizer=tokenizer,
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
    )

    return {
        "adapter_id": entry["adapter_id"],
        "adapter_path": adapter_path,
        "base_model": base_model,
        "dataset": dataset,
        "base_output": base_output,
        "tuned_output": tuned_output,
        "scores": entry.get("scores", {}),
        "delta": entry.get("delta", {}),
    }
