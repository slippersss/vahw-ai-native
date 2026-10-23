# Bounded host lifecycle instrumentation

Use when a short profile may miss rare admission failures or cannot explain what a completion barrier waits for. Prefer existing logs/counters first. Build probes for the exact installed source; do not apply a historical line-number patch to another revision.

## Evidence contract

| Event | Useful host-owned fields |
| --- | --- |
| Scheduler output | Run/service identity, monotonic and wall timestamps, PID/rank, scheduler sequence, request IDs, scheduled logical tokens, draft reservation, running/waiting IDs and remaining budgets |
| Admission/allocation check | Request state, guard name, required/free/reserved/watermark, local/external computed tokens, new tokens, lookahead, pass/fail |
| Window reclaim | Request/group, processed frontier actually used, physical blocks returned, free before/after |
| Completion processed | Source scheduler sequence, request, processed tokens, termination status, pending access fence |
| Connector lifecycle | Request/remote ID, retention owner, read/ACK received and consumed events, normal versus timeout/abort cleanup |
| Actual free | Request, reason, non-null physical blocks returned or deferred, free before/after and fence |

Use process-local sequence numbers to order events on one host. Wall times locate logs; monotonic clocks are not directly comparable across hosts. Preserve per-process files or a non-interleaving writer. An object address is not a stable request or event ID.

## Keep probes host-only

- Read existing scheduler/allocator metadata and already materialized host results. Do not call device tensor `.item()`, `.cpu()`, stream/device synchronize or a new collective merely to print a value.
- Do not change admission decisions, exception handling, refcounts, request lifetimes, lock ordering or completion semantics. Preserve the original return value and failure path.
- Filter to the question and bound file growth. Emit failures and aggregate counters where possible; full request snapshots can be expensive. A preflight should cover parsing, volume and success/failure branches before a long campaign.
- Record patch/helper contents, source revision and enabled probe settings. A PID file or patch file alone does not prove the live worker loaded it; restart the affected owned services when the experiment requires new code.
- No device synchronization does not mean zero overhead. Compare performance within the same probe state and retain clean benchmark cohorts separately.

## Correlate and stop

Pair events by request, rank and scheduler sequence before considering wall-clock proximity. Log a missing event as unavailable, not as zero delay or a successful release. Sampling can estimate event frequency but cannot prove an exact absence of failures outside its window.

If a failure is followed by a short batch, verify that the rejected request was its waiting head and that the scheduled batch retained the already planned running tail. Trace completion and actual free independently; do not invent a synchronous “ask whether B can release” call caused by C's submission.

On handover, stop only owned workers and preserve partial buffers/logs before removing probes. Keep source restoration separate from device release, and report which source edits remain.
