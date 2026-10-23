# Prefill and cache comparisons

> 中文导读：用于长输入、单token输出及池化测试。先固定实际负载、指标公式和缓存状态，再解释吞吐差异。

## Fix the population and arrival process

- Preserve the actual request payloads, order, post-template lengths and output counts. A seed is not a frozen dataset or a frozen arrival schedule.
- Equal average request rates and concurrency limits do not imply equal arrivals. Save planned offsets and actual starts; replay the same offsets for paired methods. A concurrency limiter can delay actual starts differently, so retain both series.
- Distinguish rate-limited traffic from continuously backlogged traffic. A quiet queue cannot expose a capacity-dependent admission failure. Preserve the requested load rather than silently replacing it with a saturation test.
- Keep one primary comparison with unambiguous method/trial names. Separate workload controls, diagnostic runs and capacity interventions. An exported copy is not another trial.

## Define the throughput before comparing it

Read the installed summarizer/calculator source. Preserve its revision and native output. Do not rename every tokens/s value as prefill throughput.

| Quantity | What must be established |
| --- | --- |
| Input token throughput | Which successful input tokens are summed, whether cached tokens count, and the full-run or steady-window denominator |
| Native prefill throughput | Exact client formula and weights; it may use TTFT rather than the wall-clock run duration |
| Executed prefill work | Server-scheduled tokens in the same counter window, separated from cache hits and recomputation |
| TTFT | Client first-response semantics; includes queueing, lookup/load, execution and applicable proxy/transfer stages |
| Output throughput / TPOT | Useful for decoding; a single output token does not support ordinary inter-token TPOT |

Do not substitute `total_input / duration` for a client's native prefill metric. A TTFT-derived metric can move while full-run input throughput does not, and vice versa. Report both with definitions when they answer different questions. Full-run input throughput measures completion speed for that workload; counting externally reused tokens does not make it device compute throughput.

Compare equal successful populations and retain failures, retries and client probe traffic. A reduced duration with fewer completed requests is not an improvement.

## Separate three cache concepts

1. Dataset shared-prefix fraction and number of distinct prefixes.
2. Local HBM prefix caching and its actual cache domain/routing.
3. External KV reuse through the pool, including block alignment and connector lookup rules.

A data-generation switch named prefix cache does not enable server prefix caching. Conversely, disabling local prefix caching does not necessarily disable supported external reuse. Resolve both in the effective service and connector configuration.

Audit actual hit/query/executed-token deltas. Tokenizer/template additions and hybrid-cache alignment can make a nominal prefix percentage materially different from measured hits. Do not convert external hits into assumed shared HBM allocation: per-request destinations may still consume separate HBM blocks.

Warm each intended cache domain with the frozen prefixes and verify coverage. To measure prefix reuse without complete-request reuse, freeze one suffix set for the paired formal runs that differs from warmup. Do not regenerate a different suffix per method. Drain after warmup and put before counters outside warmup traffic.

## Preserve deployment semantics

Record client -> proxy -> P -> transfer -> D, actual role/card/rank mapping and `do_remote_decode`. A pure-P request with remote decode disabled bypasses the normal D read/ACK retention path; it is a separate cohort from full P/D. Output length one does not by itself disable transfer or immediate-release requirements.

Disabling pooling means removing external history reuse while preserving the requested P/D transfer path. Removing the entire multi-connector or D changes more than pooling. A standalone local-prefix-cache diagnostic can be useful, but label it as a mechanism experiment, not a reproduction of pooled throughput.

## Capacity interventions

- Snapshot effective KV bytes, pool blocks, bytes per block, cache groups, model/runtime memory and speculative configuration per rank. Equal utilization fractions are not equal KV capacity; equal KV bytes are not necessarily equal block counts across layouts.
- Prefer a single-variable intervention and a return-to-baseline run with frozen traffic. Keep source/instrumentation and the unaffected role unchanged. Rewarm after restarts under the same policy.
- Compare failure counts and scheduled batch composition as well as throughput. Normal final tails differ from small middle batches while work remains queued.
- An observed recovery after a coarse capacity increase does not identify the minimum sufficient capacity, nor isolate draft computation from weights, KV layout, lookahead and lifecycle effects.
