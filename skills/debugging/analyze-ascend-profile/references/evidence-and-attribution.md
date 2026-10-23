# Evidence and attribution

## Logical work versus physical shape

- Distinguish scheduler tokens, actual kernel query tokens, draft inputs and cross-rank padded shapes. A routing input shaped like DP times a large local block does not prove every rank had that much useful work.
- Confirm each pad's input/output shapes and consumer. Many PadV3 calls implement unrelated alignment. Duration alone cannot identify large DP padding, particularly for asynchronous enqueue events.
- Use complete target-layer sequences to classify a model step. Exclude partial window edges and do not combine attention operators from adjacent steps simply because their shapes match. A model's target and draft layer counts must come from its actual implementation/configuration.
- Count small steps in the middle while a queue exists separately from normal final tails. Both methods can have small steps; the useful question is their cause, frequency and exposed cost.

## Host waits and device dependencies

- `threading.Lock`, future waits and `synchronize` show where the CPU waits, not automatically what the device is executing. Inspect the preceding submissions and corresponding stream completion, copy, event or collective.
- A barrier can be accounted under different target/draft stages when a feature changes. Find its counterpart in both paths; do not call the whole enclosing draft CPU span extra draft compute.
- Follow profiler-supported flow/correlation IDs with process, thread and time scope. Object addresses can be reused and are not unique cross-run dependency IDs. Temporal adjacency is weaker evidence than an explicit dependency.
- Avoid nested-span double counting. Compute interval unions for occupancy, and distinguish device execution, host dispatch gaps, waiting for another stream and waiting for another rank.

## Communication

Identify the process group and source call: DP coordination, TP, EP/MoE routing, draft synchronization, KV transfer or another operation. A long collective kernel may include waiting for a late rank, overlap useful compute or contend for resources; it is not automatically slow transport bandwidth.

With all ranks, compare entry times, exit times, logical work and collective identity. Without matching ranks, report the local wait and possible dependency, not a proven remote cause. Sum-of-kernel durations and the number of collectives alone cannot establish throughput loss.

## Search and evidence record

For each material claim retain:

| Identity | Values |
| --- | --- |
| Origin | Run, role, rank, file, one-based CSV row or zero-based trace event index |
| Timing | Native unit, start/duration, clock/alignment assumption |
| Work | Step/request when known, target/draft, logical tokens and physical shapes |
| Dependency | PID/TID/stream, flow/correlation, source call and tested revision |
| Comparison | Equivalent control slice, observation versus inference, missing ranks/edges |

Example inspection recipe: filter the affected rank and time range, locate the pad with the relevant output shape, then follow its consumer into routing/communication. Show a nearby normal-sized step as a control. Do not tell the reader to scan every event with the same generic name.
