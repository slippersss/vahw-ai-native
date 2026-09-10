# vLLM Ascend numerical and cache debugging

> 中文导读：用于并发下的重复 token、NaN/Inf、KV 或 recurrent state 污染。按运行身份、最早坏边界、物理地址、单变量实验逐步收敛；不要把跨轮证据当作一次完整写入追踪。

## Establish the experiment, not just the symptom

Create a case directory under the task workspace. Keep source changes in the business repository and logs, dumps, helpers, backups, and experiment notes in the case directory. Use the existing remote-work workflow when machines are involved.

Record the authoritative code location selected by the user; it may be a remote checkout. Record both vLLM revisions, staged and unstaged changes, relevant untracked files, actual import paths, native build identity, model/tokenizer configs, and effective engine arguments. Distinguish runner generations and main/draft models. Identical paths on several hosts do not establish shared files.

For each run retain:

```text
run ID, parent baseline, source/build/config identity
hypothesis, one intended change, predicted distinguishing result
input IDs or dataset hash/selection, sampling, concurrency, topology
probe/mock/zeroer status, service and client start times
observed result, stop reason, artifact paths, limitation, next experiment
```

Append results after each experiment. Existing reports can contain superseded explanations: read corrections and raw artifacts before promoting a conclusion. Separate startup/import failures, invalid experiments, reproduced numerical failures, and bounded non-reproductions.

## Shorten the cycle while preserving the trigger

- Start with a smoke request, then the smallest load that has actually reproduced. Keep the original workload as the acceptance case. Fixed inputs and greedy decoding help comparisons but do not guarantee deterministic concurrency scheduling.
- Stateful failures need fresh-service controls. Greedy requests following a stochastic failing batch may inherit its corrupted cache; they do not alone exclude earlier sampling-related effects.
- Add a streaming anomaly guard when long generation makes failure detection expensive. Preserve request bodies and normal SSE fields, record the trigger and offending request, cancel owned requests, and verify they drain. A repeated-token threshold is case-specific, not a universal correctness oracle.
- Measure actual outstanding requests and connector limits, not just configured concurrency. Distinguish client concurrency, queued requests, and executing sequences. Retries and warmup requests need separate counts.
- Long silence or queueing is not automatically a hang; compare per-rank progress, running/waiting counts, errors, and resource state.
- Reduce layers, model size, batch, topology, or output length only if the suspected condition survives. Cache grouping depends on layer counts/order, parallel sharding, page sizes, and allocation pressure. A small-model pass can remove the trigger rather than falsify the hypothesis.
- For reduced weights, create an independent directory: symlink unchanged shards, copy configs/indexes/shards before editing them, and never write through symlinks to originals. Check draft capture-layer IDs and loader behavior; filtering an index may not prevent reading unwanted keys from a mixed shard. Reduced or dummy weights test structural invariants, not original task accuracy.
- Mocking a proposer does not necessarily remove draft cache allocation, dummy/capture work, or metadata updates. Enumerate what the mock actually bypasses. A disappearing symptom implicates that intervention, not automatically its arithmetic.
- Treat zeroing, forced synchronization, extra warmups, eager mode, and temporary extra cache allocations as experimental variables. A pass with them enabled does not establish the final fix.

## Localize the earliest bad boundary

Use a narrowing sequence when evidence supports it:

```text
raw response/token IDs -> selected logits/hidden -> layer boundary
-> normalization/attention/recurrent/projection boundary
-> exact live input state and metadata -> writer/address/reader
```

Repeated punctuation, token ID zero, or null serialized logprobs are symptoms, not proof of a specific NaN source. Verify the tokenizer and inspect pre-sampling live logits. Distinguish NaN/+Inf from intentional -Inf masks.

Capture numeric summaries before full tensors: finite/nonfinite counts and bounded ranges for live rows. Account for sequence-parallel shards and gather/reduce-scatter mappings before attributing bad rows to a rank. Cross-rank agreement in an output does not identify the originating rank.

For recurrent operators, finite q/k/v/g/beta does not establish finite inputs: the selected initial state is also an input. Capture accepted counts, cu-seqlens, block tables, selected state slots, and before/after state. Record whether every live selected slot is covered. A guessed slot progression can change with scheduling; incomplete coverage cannot support a finite-state claim.

“State was already bad before this call” does not prove it was bad before the request started, before prefill, or before previous recurrent calls. Trace the same request and slot through allocation, initialization, each write, reuse, and the failing read if writer attribution is required.

## Audit token layout and collective semantics

For periodic bad rows or matching local bad indices across ranks, inspect communication boundaries alongside cache addresses. Compare the observed spacing with the actual padded token count and shard lengths for that failing step. Periodicity is a lead, not proof of SP or a particular writer.

Build a compact mapping at the first bad boundary:

```text
rank | local row | global token | request/token position | live or padding
```

For a confirmed contiguous equal split, global row = rank * shard_length + local row. Do not apply this formula to reordered, packed, or uneven layouts without tracing their mappings. All-reduce requires corresponding elements to represent partial contributions to the same logical token; matching shapes, successful collectives, and identical outputs across ranks do not establish that contract.

Trace token ownership and weight ownership separately through the producer, MLP, and consumer. With token-sharded inputs and TP-sharded weights, a valid implementation may gather tokens before local projections and reduce-scatter the resulting partial sums. Other implementations may replicate weights or provide communication in an enclosing wrapper. Check the selected process group and avoid adding a second reduction. Audit standalone dense, routed experts, and shared experts separately, including inherited reduction defaults and optional alternate weight-sharding groups.

Distinguish creation of a nonfinite padding value from its propagation into live tokens. A demonstrated propagation defect can be repaired without claiming the original padding writer was identified. Conversely, merely clearing padding can hide a communication error that also mixes finite tokens.

For a communication repair, a small multi-rank reference can test distinct finite token inputs, padding nonfinite isolation, and the non-SP path. Compare against the same full-weight computation and make the old path fail for the intended semantic reason. Label lightweight projection or CPU tests as communication validation; retain original-backend validation for the actual quantized implementation.

## Probe graph execution without silently changing it

- Determine compile, capture, replay, or eager failure before choosing instrumentation. Python hooks inside captured forward normally do not run during replay.
- Preallocate bounded device buffers with stable addresses. Use capture-compatible D2D copies inside the graph, and inspect/save them after replay outside capture. Record which capture shape and occurrence populated each buffer.
- Avoid device `.item()`, `.cpu()`, printing device values, and file I/O in capture. If a summary needs a readback, batch it at an explicit graph-external boundary. Even D2D copies can perturb memory or timing: compare symptom reproduction with probes enabled and disabled.
- Preserve source shape, dtype, stride, storage offset, storage base pointer, data pointer, and device format before cloning or making a contiguous CPU copy. Saving values alone can erase the layout defect.
- Select by request identity plus occurrence/step, not just forward-call count: prefill chunks, warmups, and dummy runs all add calls.
- Avoid adding a warmup solely to initialize probes when possible. If required, account for mutations to forward context and metadata; do not reuse mutated context for capture. Mark such a run as instrumented and revalidate without it.
- Bound ranks, layers, steps, tensor rows, device memory, and disk footprint. Stop adding probes once an existing artifact can distinguish the hypotheses.

## Derive byte addresses from the actual view

Build a table with separate columns for checkpoint-config values, runtime spec values, code-derived values, and captured tensor metadata. Never substitute query-head counts for stored KV heads. Distinguish token block size, kernel block size, Mamba state slot count, per-block bytes, and whole-pool bytes.

Trace the exact revision through:

```text
config resolution -> per-layer specs -> grouping selection/fallback
-> allocator descriptors -> shared backing -> reshape/view
-> logical-to-kernel block mapping -> writer/reader indexing
```

For a tensor coordinate, relative byte offset is:

```text
element_size * (storage_offset + sum(index[d] * stride[d]))
```

`storage_offset` and strides are in elements. Adding the storage base gives an address only for that same live allocation. Do not add storage offset twice when starting from `data_ptr`. A host clone's pointer is not the original device pointer.

Do not assume one logical block occupies `[id * page_bytes, (id + 1) * page_bytes)`. A whole-pool structure-of-arrays view can place all conv states first, then all recurrent states, while attention places all K followed by all V. Derive each region using the actual block count. Equal padded page bytes do not imply equal internal strides or boundaries.

For example, when source confirms a whole-pool layout, let N be pool capacity, P its bytes per logical block, C conv bytes per block, R recurrent bytes, and A each GQA K/V block's bytes:

```text
SSM(j) = [N*C + j*R, N*C + (j+1)*R)
V(i)   = [N*(P-A) + i*A, N*(P-A) + (i+1)*A)
```

Compute intersections for distinct legal live IDs; include pool bounds, reserved null IDs, and scheduler ownership. Physical overlap is hazardous when incompatible owners are simultaneously live, not merely because a pointer is shared. Check existing alignment code as well as slicing code: alignment derived from the main model may not hold for a different draft spec.

Use the capacity from each dump separately. Adjacent runs can have different N due to allocation changes. Cross-run pointer evidence plus a corrupt-state dump can support a mechanism but cannot identify a same-run writer.

Raw bit patterns can suggest dtype reinterpretation. Two BF16 NaN patterns occupying a FP32 word are compatible with an overwrite hypothesis, not proof of which operator wrote them. Direct attribution needs matching allocation identity, write indices, payload, and time ordering.

## Replay and intervene

- Capture the complete operator input set, scalar options, selected backend, strided layout, state, and execution mode. Check the wrapper's actual branch before placing hooks.
- Use a deliberate reference, such as a supported CPU FP32 formula, with declared tolerances. Do not cast away the failure or assume a historical fallback is golden.
- Random finite-input operator tests passing only narrow the hypothesis. Production state corruption, real offsets, aliasing, padding, and graph metadata may be absent from that test.
- A byte-layout reproducer proves address overlap for its constructed case. Synthetic NaN writes, especially to reserved block zero, are not production writer traces or complete scheduler reproductions.
- Temporary physical isolation can distinguish sharing-related hypotheses, but extra unbudgeted allocations change capacity and timing. A final solution must obey allocator accounting and scheduler contracts.

## Validate and hand off

Remove probes, extra warmup/synchronization, and experimental mocks before final validation, except explicitly retained baseline changes. Record each retained change; do not call different fix sets a strict one-variable A/B.

Validate the smallest representative reproduction and the original workload/topology within the authorized budget. A time-limited observation with no recurrence is not a completed accuracy evaluation. Logged 100% KV samples do not count distinct reuse cycles. Report completed request counts, cancellation, actual load, and latency limitations separately.

For regression UT placement and branch compatibility, use [vllm-regression-interface-audit.md](vllm-regression-interface-audit.md). Keep task-specific addresses, model paths, run IDs, and numeric evidence in the case archive rather than this reusable procedure.
