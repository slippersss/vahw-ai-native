---
name: analyze-ascend-profile
description: Analyze Ascend serving traces and kernel exports across ranks, separating logical work, padding, device execution, communication and host waits with source-linked evidence.
---

# Analyze Ascend serving profiles

> 中文导读：从rank、step、层与kernel逐层定位，保留原始行号和事件索引；用设备依赖核对CPU等待，避免单凭duration或padding下结论。

## Establish comparable evidence

Identify the run, role, rank/device/PID mapping, code/configuration, cache state, workload and capture window. Keep clean benchmark statistics separate from profiled-run statistics. Missing ranks and truncated first/last layers limit attribution; do not synthesize them from another run.

Inventory kernel details, trace events and available communication tables before choosing a parser. Normalize timestamps/units without losing source file, CSV row or original event index. Retain PID/TID, stream, correlation/flow IDs, operator arguments, shapes and durations. Do not ship a parser's inferred labels as native profiler fields.

For exact attribution and reviewable findings, read [Evidence and attribution](references/evidence-and-attribution.md).

## Work from coarse to fine

1. Segment complete model steps and target/draft work using actual markers and source contracts. Verify repeated layer sequences; do not infer every step from one common operator name.
2. Group equivalent execution states: scheduled logical tokens, target/draft role, cache/load state and padded physical shapes. Compare like groups before averages.
3. Align ranks by a verified step/collective identity and then inspect timeline overlap. Wall-clock proximity alone does not establish a matching distributed step.
4. Explain differences in counts and critical-path occupancy before assigning a slow kernel. Separate useful compute, padding, transfer/collectives and host dispatch/idle intervals.
5. Follow the earliest divergence into the tested source revision. Close a specific evidence gap with bounded host counters or a controlled intervention rather than treating a visually prominent span as the cause.

If small middle batches coexist with waiting work, use the [KV admission and lifecycle reference](../references/kv-admission-and-lifecycle.md). For collecting missing evidence use [Profile vLLM Ascend](../../testing/profile-vllm-ascend/SKILL.md).

## Large traces and parallel processing

The standard-library [trace_events.py](scripts/trace_events.py) streams array or `traceEvents` object exports, including `.gz`, and preserves the original zero-based event index. Set `SKILL_DIR` to this skill's absolute directory; no particular current directory is required:

```bash
python "$SKILL_DIR/scripts/trace_events.py" /path/to/trace_view.json.gz --contains synchronize --limit 20
```

This emits filtered JSONL for inspection, not a diagnosis. A limit stops reading early and therefore does not validate the remaining document. Full iteration validates structure and rejects truncation. Memory scales with read buffer plus the largest individual JSON value; a huge non-event metadata value may still be large.

For acceleration, parallelize independent rank/files with a bounded process pool, reducing each to compact rows or summaries. Set workers from measured RAM per worker and CPU availability. Do not load several whole traces into parent and children, split JSON at arbitrary byte offsets, or send millions of event objects through process queues. Decompression/file reads can benefit from threads; Python-heavy decoding/classification generally needs processes for CPU parallelism. Use the simplest measured improvement.

## Deliver findings that can be inspected

Give the exact file and row/event index, logical/padded shapes, timestamps and units, related dependency IDs, equivalent control and missing evidence. Include a narrow search recipe: operator plus rank/step/time/shape, not just “search PadV3” or a duration threshold.

Label observations, deductions and hypotheses. Distinguish kernel-duration sums from unions of occupied intervals and from end-to-end critical-path time. Do not claim a throughput regression is quantitatively explained until the affected frequency and exposed time are reconciled with the benchmark window.

## Provenance

The normalize/segment/classify/cross-rank workflow is internalized from [pisceskkk/vllm-ascend-skills](https://github.com/pisceskkk/vllm-ascend-skills/tree/4e7417c3d88847a17ba6d61d6a9b748ad8e0bbc3/skills/ascend-profiling-analysis), MIT, Copyright 2026 Qi Mao; its license is retained in `LICENSE`. The local stream reader and serving-specific attribution guidance were developed from local profiling practice. No external classifier/model-signature database is required by this skill, and an unverified signature must not become a classification rule.
