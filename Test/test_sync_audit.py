#!/usr/bin/env python3
"""Exact-diff guard: only approved region and AdBlock patches may differ from upstream."""
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("personal_sync", "scripts/sync.py")
sync = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(sync)

upstream = sync.get_text(sync.UPSTREAM_RAW)
generated = Path("mihomoScript.js").read_text(encoding="utf-8")
sync.audit_generated(upstream, generated)

# Negative controls: unrelated DNS and region-matching edits must be rejected.
for mutated in (
    generated.replace("const commonDnsList = [", "const commonDnsList = []; // unauthorized change\nconst commonDnsList = [", 1),
    generated.replace("(?<![A-Za-z])(?:CA|CAN)(?![A-Za-z])|canada/i", "(?:CA|CAN)|canada/i", 1),
):
    try:
        sync.audit_generated(upstream, mutated)
    except RuntimeError:
        pass
    else:
        raise SystemExit("Audit accepted an unauthorized mutation.")

print("Exact patch-boundary audit passed; unauthorized DNS/Canada mutations were rejected.")
