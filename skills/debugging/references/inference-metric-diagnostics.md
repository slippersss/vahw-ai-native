# Diagnose inference metric anomalies

> 中文导读：区分统计计算错误、统计对象变化和真实执行退化。沿原始记录到汇总值追溯，再用受控对照验证，避免从单个比值直接推断根因。

## Audit the measurement contract

- Trace event/request → raw record → aggregation → reported value. Verify units, populations, eligibility, denominators, weighting and windows against the implementation.
- Filtering or pruning can change who enters a statistic. Correct arithmetic does not establish a valid comparison. Distinguish proposed, eligible, processed and accepted work where relevant; a zero denominator is undefined.
- Transport chunks, streaming events, tokens and execution iterations are different units. Ratios of differently weighted summaries are cross-checks, not identities. Reuse the benchmark skill's collection definitions rather than duplicating formulas.

## Distinguish accounting from execution

- Preserve raw counts and request/iteration identity. Compare equivalent populations under controlled inputs; aggregate changes can arise from selection or changed trajectories.
- Equal average request rates and concurrency limits do not establish equal load. Audit planned release times and actual request starts; preserve or replay the same arrival sequence for paired comparisons, then reverse execution order when order effects remain plausible.
- For prefix reuse or external KV pooling, distinguish the dataset's shared-prefix fraction from measured cache-hit tokens after block alignment. Compare hit, miss and executed-token deltas before attributing a throughput difference to a model feature.
- Use a focused intervention to distinguish competing explanations. Neither an expected denominator change nor an anomalous ratio proves whether an execution defect exists.
- When latency and throughput disagree, inspect timelines and measurement windows before assigning a component-level cause. Locating an affected phase is distinct from identifying its cause.
- For one-token prefill workloads, inspect the client's native prefill formula alongside full-run input throughput and server scheduled work. A TTFT-derived statistic, cached-input accounting and device execution rate answer different questions; do not substitute one denominator for another.

## Keep probes trustworthy

- Prefer existing records. Bound new instrumentation and preserve identity, buffer lifetime and asynchronous completion semantics; a saved alias may later contain different data.
- Account for synchronization, copies, logging and CPU work. Reusing completion machinery does not make probes free; separate instrumented diagnosis from clean performance claims.
- A long CPU span can contain a deferred completion barrier whose attribution moves between phases when a feature is toggled. Check the corresponding barrier in both paths, avoid summing nested spans, and use event/flow identities to establish dependencies; temporal proximity or a reused object address alone is insufficient.
- Localize with a small reproducer, then validate against the representative workload when authorized. A small passing case does not dismiss a load-dependent issue.
