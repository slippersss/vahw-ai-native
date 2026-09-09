---
name: debugging
description: Diagnose software failures and inference regressions using runtime evidence and source-level data flow. Use for deterministic exceptions, cross-deployment output differences, and load-dependent vLLM Ascend NaN or KV-cache corruption, including graph replay and regression-test interface audits.
---

# Evidence-driven debugging

> 中文导读：统一调试入口，覆盖必现异常、推理对照差异，以及并发下的 NaN、状态缓存污染和图模式问题。按问题加载专项流程，以证据分级、最早分叉点和最小验证实验为核心。

## Choose the debugging mode

- For a deterministic failure with an explicit exception or stack trace, read [references/deterministic-failure.md](references/deterministic-failure.md).
- For successful vLLM requests that differ across backends, devices, versions, quantization modes, or deployments, read [references/vllm-inference-consistency.md](references/vllm-inference-consistency.md). Use its input-equivalence gate before comparing downstream metrics.
- For load-dependent NaN/Inf, repeated-token collapse, recurrent-state corruption, or incompatible shared KV layouts on Ascend, read [references/vllm-ascend-numerical-debugging.md](references/vllm-ascend-numerical-debugging.md). This also covers bounded graph probes and operator replay.
- When converting a fix into a regression test or porting it across vLLM revisions, read [references/vllm-regression-interface-audit.md](references/vllm-regression-interface-audit.md).
- If neither description fits, use the shared principles below without forcing the problem into either specialized workflow. Add a new reference only after a distinct workflow has been validated in real work.

## Maintain an evidence boundary

Classify every material statement as:

- **Observed:** stated directly by logs, configuration, source inspection, runtime state, or captured artifacts.
- **Deduced:** necessarily follows from observed facts and inspected code or contracts.
- **Hypothesized:** plausibly explains the mechanism but still needs a targeted probe.

Do not transfer a fact from one process, role, model, request, or deployment to another without evidence. Prefer effective runtime configuration over launch intent.

Attach a run/revision identity to evidence. A missing probe record is missing evidence, not a finite tensor or a passing execution. When a later audit corrects an earlier claim, explicitly supersede that claim; do not silently combine incompatible observations. Repeated review does not increase empirical confidence: distinguish source review, isolated execution, full tests, and end-to-end validation instead of inventing confidence percentages.

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
