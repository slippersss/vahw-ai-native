---
name: debugging
description: Diagnose reproducible software failures and controlled behavioral differences using runtime evidence and source-level control or data flow. Use for deterministic regressions with an exception or stack trace, and for successful vLLM inference deployments whose outputs or metrics diverge; do not use as a generic testing or incident-response checklist.
---

# Evidence-driven debugging

> 中文导读：这是可复现问题的统一调试入口。先区分“必现异常”和“vLLM 对照结果不一致”，再加载对应流程；所有场景都以证据分级、最早分叉点和最小验证实验为核心。

## Choose the debugging mode

- For a deterministic failure with an explicit exception or stack trace, read [references/deterministic-failure.md](references/deterministic-failure.md).
- For successful vLLM requests that differ across backends, devices, versions, quantization modes, or deployments, read [references/vllm-inference-consistency.md](references/vllm-inference-consistency.md). Use its input-equivalence gate before comparing downstream metrics.
- If neither description fits, use the shared principles below without forcing the problem into either specialized workflow. Add a new reference only after a distinct workflow has been validated in real work.

## Maintain an evidence boundary

Classify every material statement as:

- **Observed:** stated directly by logs, configuration, source inspection, runtime state, or captured artifacts.
- **Deduced:** necessarily follows from observed facts and inspected code or contracts.
- **Hypothesized:** plausibly explains the mechanism but still needs a targeted probe.

Do not transfer a fact from one process, role, model, request, or deployment to another without evidence. Prefer effective runtime configuration over launch intent.

## Find the earliest divergence

Reproduce with the smallest representative case and, when available, a known-good baseline. Compare equivalent inputs and execution roles, then trace control flow and data flow until the first observable mismatch. Treat later errors and metric differences as consequences until shown otherwise.

Close the smallest remaining evidence gap with a focused log, runtime inspection, source comparison, or controlled intervention. Do not run a broader experiment when a narrower probe can distinguish the current hypotheses.

## Report the result

Lead with a compact causal chain:

```text
effective runtime fact
-> selected path or representation
-> first observed divergence
-> downstream failure or metric impact
```

State separately what is proven, what remains likely, and the smallest next probe that would confirm or reject it.
