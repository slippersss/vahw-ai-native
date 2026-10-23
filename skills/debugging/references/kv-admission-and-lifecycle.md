# KV admission, capacity and release lifecycle

> 中文导读：把“小尾巴、padding、延迟释放”的定性怀疑落到分配检查、物理块和事件顺序；区分单次门槛、整轮推演与实测验证。

## Locate the admission decision

Trace the tested scheduler's running-request loop, waiting admission, allocation call and break/preemption behavior. Distinguish full-sequence admission, current-step allocation, watermark and reserved-block checks. A waiting request can fail after running requests have already been placed in the scheduler output; failure need not cancel those requests.

Record the exact guard operands. When the implementation uses `required = allocation + watermark` and `available = free - reserved`, check those values in the same process and instant. A “KV failure” claim requires a return branch or equivalent evidence, not simply a short batch. Full-sequence checks can occur before window reclamation; do not assume all guards see identical free counts.

Separate normal drain tails from small middle batches with a nonempty queue. Pair a failed admission and the subsequent small scheduler output by request, PID/rank and order. A nearby failure from another rank is not the cause of this batch.

## Separate allocated, completed and reclaimed progress

For each request distinguish:

- `a`: allocated/scheduled extent, including applicable lookahead.
- `p`: execution progress whose completion result the scheduler has processed.
- `u`: progress through which the actual window-reclamation operation has run.

Usually `u <= p <= a`; do not replace all three with an optimistically advanced `num_computed_tokens`. Audit increments at scheduling and decrements/updates at completion. Processing an intermediate result may not itself reclaim that request's sliding-window blocks.

Inspect engine scheduling order, batch-queue depth and request access fences. A new batch can be scheduled before an older batch's result is handled even if the device has already finished it. Do not infer a specific async-scheduling flag or fixed two-step delay merely from this behavior. Include any retained in-flight attention windows and copy-on-write blocks.

## Treat completion and transfer as separate conditions

Map actual events rather than assuming “prefill submitted means freed”:

```text
last chunk scheduled -> result handled -> request termination processed
                                      -> connector retention decision
remote read complete -> ACK consumed --+
in-flight access safe ----------------+-> blocks become reusable
```

Some events overlap; this is a dependency graph, not an additive time formula. Inspect which connector owns retention, how a multi-connector combines completion, and where ACKs are polled. A notification can arrive on a thread before the scheduler consumes it. Transfer parameters exposed only in a completed response cannot cause an ACK before that response exists. Timeout/abort cleanup is a separate path; do not equate it with successful read completion.

Pure P with remote decode disabled removes the normal D-read retention path only if the tested connector's condition says so. It does not remove in-flight result handling or access fences. No-pooling still may have asynchronous scheduling overlap; conversely a pooling comparison must preserve the requested direct P-to-D transfer.

## Count physical blocks

- Read the actual cache groups, logical block sizes, physical pool layout and bytes per pool block from the tested revisions/configuration. Hybrid compressed attention and state groups need separate calculations.
- Block tables may contain many null placeholders. Do not sum table lengths as physical occupancy. Use non-null live blocks/refcounts; shared blocks count once. Account for pinned, deferred, copy-on-write and other non-reusable blocks explicitly.
- Startup “KV token capacity” or max concurrency at one configured maximum length is not necessarily linear for another length in a hybrid layout. Dividing that token count by a shorter prompt is not a sufficient-capacity proof.
- Equal memory utilization does not mean equal KV bytes. Equal bytes does not mean equal block counts across speculative layouts. Inspect weights, activation/runtime reserve, pool block stride and speculative cache groups separately.

For a verified independent-allocation layout with one full or ordinary sliding-window allocation per group, a useful state formula is:

```text
full group:    ceil(a / b)
window group:  max(0, ceil(a / b) - floor(max(0, u - W + 1) / b))
```

Derive `b`, `W`, retained-token extensions and group-specific extents from source. This formula does not automatically cover shared local prefixes, CoW, chunked-local attention, admission caps, Mamba or arbitrary hybrid managers. External hits are not proof of shared HBM blocks. The optional [kv_capacity_bound.py](../scripts/kv_capacity_bound.py) evaluates explicitly supplied independent full/sliding states and rejects other declared layouts; it is not a scheduler simulator.

Supply the proposed new request's extent as one of the check's requests when evaluating total capacity. Add only genuinely unmodeled occupancy to `other_unavailable_blocks`; do not add `pool-free` on top of requests already counted. Keep guard reserves separate and map the script's full/sliding formula to the actual guard before using its total. The same block stride must apply to all modeled pool blocks.

Minimal synthetic input, unrelated to any particular model:

```json
{
  "block_bytes": 1024,
  "independent_allocations": true,
  "null_blocks": 1,
  "pool_blocks": 9,
  "groups": [
    {"name": "full", "block_tokens": 4},
    {"name": "window", "block_tokens": 4, "window_tokens": 4}
  ],
  "checks": [{
    "label": "before reclaim",
    "requests": [{"id": "a", "allocation_end": 16, "reclaim_frontier": 8}],
    "reserved_blocks": 2
  }]
}
```

Save it as an absolute `case.json` path and run `python /absolute/path/to/skills/debugging/scripts/kv_capacity_bound.py /absolute/path/to/case.json` from any directory. Expected peak is 10 blocks (full4 + window3 + null1 + reserve2), margin -1. Replace these synthetic states with source-verified ones before drawing a deployment conclusion; requests using different per-group extents are outside this helper's shared-extent schema.

## Derive the right capacity claim

1. **One actual check:** hold the current unavailable set fixed, add the actual new requirement and guard reserves. This explains the observed failure; it is not the minimum for the entire run.
2. **Fixed-trajectory earliest-release bound:** use exact event ordering and the earliest legal completion/ACK consumption to determine blocks that must still be held. Zero network time does not move a scheduler polling point. State which schedule is fixed; changing capacity or earlier admission can change that schedule.
3. **Whole-run conditional budget:** simulate a no-failure trajectory under explicit lengths, hits, arrivals, per-rank routing, batch/draft budgets, in-flight depth and release assumptions. At every guard take the peak of unavailable plus incremental demand/reserves. Include both admission and current-step checks.
4. **Guarantee:** bound retention/ACK lag or held-request count and arrival bursts, or use admission/backpressure reservations. A release-delay lower bound supplies an optimistic model, not a worst-case capacity guarantee. Average arrival rate times average delay is not a burst bound. Finite workloads can have a conservative all-resident bound even without a useful latency bound.

When tails grow, derive the recurrence from both token and input budgets, including per-request draft slots and boundary rules. A larger tail can leave a smaller new-request chunk; it need not increase capacity monotonically. Do not extrapolate a recurrence beyond request exhaustion, an empty queue, alignment changes or an additional split.

Quantify before using the word root cause: reconcile group occupancy with `pool - free`, show the failing arithmetic, then explain batch frequency and exposed work. A small block deficit can reject an entire admission, so performance loss need not scale with missing bytes. Predicting exact throughput additionally requires step costs, overlap and cross-rank imbalance, not just a capacity threshold.

## Establish causality and preserve limits

Use fixed workload/source/instrumentation and a single-variable capacity increase followed by return to baseline when authorized. Compare allocation failures, queued small batches, scheduled work, cache hits and clean throughput. A coarse successful increase is not a measured minimum. A no-pool or draft-mock experiment isolates a mechanism only to the extent its other contracts remain unchanged.

Do not call normal connector retention a leak or physical memory fragmentation. Distinguish extra draft computation, weight footprint, KV layout, lookahead, admission policy and lifecycle overlap until contribution-specific evidence separates them.

For a full-run host probe, read [Host lifecycle instrumentation](host-lifecycle-instrumentation.md). Keep case-specific source patches, numeric constants and raw logs in the experiment workspace; promote the accounting method rather than one model's thresholds.
