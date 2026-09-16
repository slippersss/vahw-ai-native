# vLLM Ascend token-alignment debugging

> 中文导读：用于排查图模式下 hidden states、positions、RoPE、slot mapping 与 KV 输入的 token 维错位。核心是区分逻辑有效 token 数与物理 padded 长度，并沿两条数据流追到它们在融合算子前首次重新汇合的位置。

## Start from the faulting operator, but trace backward

Record every token-shaped operand at the failing launch, including shape, dtype, execution role, graph mode, and run identity. A fused operator reporting incompatible shapes is the observation point, not necessarily the defect site.

Trace each operand independently to its earliest length decision. In particular, do not treat these as one data flow:

```text
model input length -> embedding -> hidden states -> projection -> KV operand
metadata token count -> positions slice -> RoPE construction -> cos/sin operand
metadata token count -> slot-mapping slice -> cache-index operand
```

The first branch commonly retains the graph-padded leading dimension while the other branches may be sliced by metadata. Compare them where they first reconverge.

## Distinguish logical counts from physical shapes

Build a small provenance table before proposing a fix:

| Quantity | Meaning | Source | Consumer |
|---|---|---|---|
| scheduled or actual tokens | Valid model work | scheduler/input batch | attention ranges, output trimming |
| tokens after padding | Physical graph input shape | graph batch descriptor | input IDs, positions, hidden states |
| metadata input tokens | Intended physical token dimension | model-state metadata construction | RoPE and slot-mapping builders |
| metadata actual tokens | Intended valid-token boundary | scheduler/input batch | query ranges, cache writes, output trimming |

Inspect assignments and consumers instead of trusting names. A field named `num_actual_tokens` may be overloaded upstream, while an Ascend extension may give actual and padded counts separate stable meanings.

Raw buffer shape and consumed view shape are different facts. For example, a positions buffer can have the padded shape while a later `positions[:metadata_count]` view is unpadded. State which stage each observation describes.

## Audit the upstream-to-backend contract

When Ascend overrides an upstream builder or extends its metadata class:

1. Inspect the upstream metadata definition, including TODOs and comments about overloaded fields.
2. Trace the upstream local variable into the constructed common metadata; do not infer semantics from the final field name alone.
3. Inspect fields added by Ascend and their comments.
4. Check whether copied mode conditions still match the new multi-field representation.
5. Inspect every consumer of the added field, especially slices and tensor allocations.

A single upstream count can legitimately change meaning by mode. After a backend splits it into separate logical and physical counts, copying the old branch condition may violate the new field contract even though the code looks equivalent.

## Probe the earliest length decisions

Instrument narrowly and gate temporary probes behind an environment variable. Useful checkpoints are:

- batch construction: actual tokens, padded tokens, request counts, graph mode, positions shape;
- common metadata construction: logical and physical token counts;
- backend metadata construction: positions, RoPE, and slot-mapping shapes;
- immediately before the fused operator: hidden/KV, cos, sin, and cache-index shapes.

For speculative decoding, record whether each observation belongs to the target or draft model. Do not transfer a shape observed in one role to the other.

The probe should answer where the dimensions first diverge. Remove diagnostic-only instrumentation after the causal chain is established unless it is intentionally retained as bounded observability.

## Repair the violated contract

Prefer fixing the earliest incorrect metadata construction when downstream tensors are behaving consistently with their declared fields. Preserve both concepts explicitly:

```text
physical input count = graph-padded model-input length
logical actual count = scheduler's valid-token length
```

Do not suppress an asynchronous device error, relax capture error handling, or crop the larger operand merely to satisfy the final operator. Such changes can hide the mismatch, discard graph rows, or move corruption downstream.

Treat execution modes separately. A graph mode may require padded physical metadata while eager execution remains unpadded. Context-parallel paths may also pad in eager mode; follow their actual input contract rather than applying one rule globally.

## Add regression coverage without repurposing existing tests

Keep existing equal-length tests intact: they may cover a distinct non-padding contract. Add a separate case where logical and physical counts intentionally differ.

At minimum, assert:

- the common metadata retains both counts;
- positions, RoPE tensors, and slot mappings use the physical input length;
- the logical count remains unchanged;
- the backend passes a physical-length positions view into RoPE construction.

When practical, add an operator-boundary assertion that the KV and RoPE token dimensions match. Run the focused test with the repository's supported vLLM revision. If collection fails because dependencies are mismatched, report that as an environment gap; syntax checks and source review are not a pytest pass.

## Report the causal chain

Use a compact stage-specific explanation:

```text
graph input was padded
-> hidden states and projected KV retained the physical length
-> common metadata recorded the logical length as the physical input count
-> the backend sliced positions/RoPE/cache indices too early
-> fused operands reconverged with different token dimensions
```

Separate raw-buffer observations from sliced views, and distinguish the upstream convention from the backend-specific contract that was violated.
