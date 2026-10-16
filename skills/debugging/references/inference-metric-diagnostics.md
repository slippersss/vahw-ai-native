# Diagnose inference metric anomalies

> 中文导读：区分统计计算错误、统计对象变化和真实执行退化。沿原始记录到汇总值追溯，再用受控对照验证，避免从单个比值直接推断根因。

## Audit the measurement contract

- Trace event/request → raw record → aggregation → reported value. Verify units, populations, eligibility, denominators, weighting and windows against the implementation.
- Filtering or pruning can change who enters a statistic. Correct arithmetic does not establish a valid comparison. Distinguish proposed, eligible, processed and accepted work where relevant; a zero denominator is undefined.
- Transport chunks, streaming events, tokens and execution iterations are different units. Ratios of differently weighted summaries are cross-checks, not identities. Reuse the benchmark skill's collection definitions rather than duplicating formulas.

## Distinguish accounting from execution

- Preserve raw counts and request/iteration identity. Compare equivalent populations under controlled inputs; aggregate changes can arise from selection or changed trajectories.
- Use a focused intervention to distinguish competing explanations. Neither an expected denominator change nor an anomalous ratio proves whether an execution defect exists.
- When latency and throughput disagree, inspect timelines and measurement windows before assigning a component-level cause. Locating an affected phase is distinct from identifying its cause.

## Keep probes trustworthy

- Prefer existing records. Bound new instrumentation and preserve identity, buffer lifetime and asynchronous completion semantics; a saved alias may later contain different data.
- Account for synchronization, copies, logging and CPU work. Reusing completion machinery does not make probes free; separate instrumented diagnosis from clean performance claims.
- Localize with a small reproducer, then validate against the representative workload when authorized. A small passing case does not dismiss a load-dependent issue.
