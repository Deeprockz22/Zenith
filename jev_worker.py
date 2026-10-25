#!/usr/bin/env python3
"""Small JSON-lines worker that keeps the optional Jev model out of the daemon."""

import json
import os
import sys
import time
from types import SimpleNamespace


def main():
    from so1 import Choice, Decider

    model_id = os.environ.get("FOCUS_JEV_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
    print(f"[Jev worker] loading {model_id}", file=sys.stderr, flush=True)
    model_kwargs = {"device_map": "auto"}
    dtype = os.environ.get("FOCUS_JEV_DTYPE", "").strip()
    if dtype:
        model_kwargs["dtype"] = dtype
    if os.environ.get("FOCUS_JEV_4BIT", "").lower() in {"1", "true", "yes"}:
        model_kwargs["load_in_4bit"] = True
    elif os.environ.get("FOCUS_JEV_8BIT", "").lower() in {"1", "true", "yes"}:
        model_kwargs["load_in_8bit"] = True
    try:
        decider = Decider.from_pretrained(model_id, backend="hf", **model_kwargs)
    except (ImportError, RuntimeError, TypeError, ValueError) as exc:
        if dtype or "load_in_4bit" in model_kwargs or "load_in_8bit" in model_kwargs:
            print(f"[Jev worker] optimized load failed ({exc}); retrying default dtype", file=sys.stderr)
            decider = Decider.from_pretrained(
                model_id,
                backend="hf",
                device_map="auto",
            )
        else:
            raise
    print("[Jev worker] ready", file=sys.stderr, flush=True)

    for line in sys.stdin:
        try:
            request = json.loads(line)
            questions = [Choice("Type", ["podcast", "lecture", "entertainment", "shorts"])]
            answer = decider.decide(request["state"], questions)[0]
            response = {"choice": answer.choice, "confidence": answer.confidence}
        except Exception as exc:
            response = {"error": str(exc)}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
