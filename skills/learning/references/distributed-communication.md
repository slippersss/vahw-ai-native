# Teaching distributed communication

Read this reference only when a learning session covers ranks, collectives, communication/computation overlap, or distributed timelines.

## Preserve collective semantics

- Distinguish collective participation and call order from per-rank payload size. All ranks can enter the same collective while sending and receiving different amounts of data.
- Label whether repeated blocks are separate collective calls, payload partitions inside one call, transport chunks, or compute batches.
- Do not depict internal chunks as additional collective calls. If call count matters, show it explicitly in a separate lane or annotation.
- State which quantities must match across ranks and which may vary. Avoid examples that silently switch from scalar values to partitionable tensors or data blocks.

## Separate interacting concerns

- Present the normal communication mechanism before performance pathologies.
- Treat communication/computation overlap as a general optimization, not as a load-balancing technique.
- Treat variable-size collectives as a communication contract, not as a load-balancing technique.
- Explain load imbalance separately: its cause, communication and computation consequences, mitigation, and residual tail after mitigation.
- When showing residual imbalance under overlap, distinguish an idle rank that has finished all its work from a compute stream stalled while waiting for its next chunk.

## Draw timelines carefully

- Use separate lanes for communication and computation when teaching overlap.
- Identify whether a lane belongs to a rank, expert, stream, or request.
- Mark synchronization points and the condition that determines completion.
- Label idle regions as local starvation, completed-work waiting, synchronization delay, or another precise cause; do not use “bubble” without saying which one.
