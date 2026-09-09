# Ascend kernel memory-access faults

> 中文导读：用于算子非法地址访问、部分 rank 异常及图模式下的疑似挂死。结合同步边界与设备日志锁定故障，再用相同数据、不同地址布局的对照验证；精简用例必须保留原故障的触发条件。

## Establish the failing launch

- Distinguish lack of progress from a reported device exception. Build a per-rank timeline around the last successful synchronization and first failure; later communication timeouts can be consequences of one failed rank.
- A Python synchronization stack identifies where the error surfaced. Use matching plog/runtime records to identify the device, stream, task, kernel and failing instruction. When existing probes synchronize successfully before an operator and fail after it, prioritize work submitted within that interval; account for other streams or threads before attributing it to one launch.
- Align records by run and process identity. Do not assume multi-host wall clocks agree. Read the failing step's actual local batch and token counts; client concurrency is not kernel batch size.
- Keep separate failure mechanisms separate. A later fallback run with pre-sampling NaN does not explain an earlier kernel address exception. Inspect the kernel's actual argument types: a token-selection kernel may receive integer IDs and offsets, not logits.

## Audit addresses before expanding numerical probes

Start from the runtime error class, actual argument layout and source indexing. For an invalid-address report, inspect cumulative offsets, first/last lanes, tail masks, strides and storage offsets before adding broad layer-level numeric dumps. Decode packed launch arguments only after confirming their ABI and scalar widths.

In Triton, a value selection around a load does not make the load conditional. For example, `tl.where(i == 0, 0, tl.load(cu + i - 1, mask=valid))` can still read before `cu` at the first valid lane. Put the boundary condition on `tl.load` itself and supply the intended masked value. Audit masked lanes and data-dependent loop bounds separately; do not silently expand a confirmed fix to every neighboring kernel.

Distinguish a tensor's logical start, its backing allocation and the mapped device-memory region. An out-of-bounds tensor read may succeed when the neighboring address remains mapped. Equal values across ranks do not imply equal address accessibility. Graph/eager differences can change allocation order and retained buffers; disappearance in eager mode alone does not prove a graph implementation bug.

## Use a layout-controlled operator experiment

When the suspected fault is a boundary access, preserve the production kernel, relevant argument types and launch parameters, while reducing the data to the smallest triggering case. Use a fresh process for each potentially failing case because a device exception can poison its context.

A useful distinguishing set is:

| Case | Values | Address condition | Purpose |
|---|---|---|---|
| Original kernel | Valid fixed inputs | Suspected access crosses a mapped boundary | Reproduce the device fault |
| Original kernel | Same inputs | Padding makes that address accessible | Test dependence on layout |
| Minimal fix | Same inputs | Original failing boundary condition | Test the correction without hiding the boundary |

The padded case is a diagnostic intervention, not a production fix. Preserve allocator configuration before importing/initializing the device, allocation order, dtype and storage offset. Print and check the resulting address geometry. A first tensor allocation or an aligned address alone does not prove the preceding memory is unmapped; retain the original-kernel failure as the negative control. If the required geometry is absent, report that the trigger was not established rather than counting a pass as evidence against the bug.

Match the independent failure to production using the available error class, kernel identity/hash and instruction symbol or PC offset. The same high-level error code alone is too weak. A faithful negative control plus a narrowly changed positive control provides stronger attribution than repeated full-service runs.

## Keep the delivered reproducer faithful

Prefer calling the actual production kernel when the claim concerns a production fix. If an extracted or simplified kernel is useful, label that validation level and preserve relevant rejection/control flow, masks and dtypes. Do not present a toy kernel as the exact production implementation.

Simplifying a previously validated script creates a new artifact. Recheck allocator setup, allocation order and launch specialization, and rerun both sides when execution is authorized. Syntax checks do not establish that the shorter script still fails before the fix or succeeds after it. If only local preparation is authorized, state that hardware behavior of the new artifact remains unverified.

## Validate in the original execution mode

After the operator control succeeds, restore the backend and graph mode that exposed the problem and run the original workload within scope. Record retained baseline probes or workarounds. Check per-request completion and per-node drain, not just an HTTP success count or absence of the original exception. Keep numerical correctness claims separate from hang resolution.

Use [vllm-regression-interface-audit.md](vllm-regression-interface-audit.md) when integrating tests. Record omitted test fixtures or dependency-driven scope reductions; a focused operator test is not the full end-to-end suite. Keep machine addresses, allocator addresses, error instances and task scripts in the case archive.
