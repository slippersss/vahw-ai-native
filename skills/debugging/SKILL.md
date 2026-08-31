---
name: debugging
description: Diagnose deterministic software failures with an explicit stack trace and, when available, a known-good version or configuration. Use for reproducible regressions where source-level control flow and runtime state can be reconstructed; do not use as a generic testing or incident-response checklist.
---

# Evidence-driven debugging

> 中文导读：适用于“稳定复现、有明确报错栈、可读源码、最好还有正常版本可对比”的问题。核心是先证明发生了什么，再解释为什么发生，并找到新旧版本最早的路径分叉点。

## Establish the failure boundary

- Record the exact failing expression, runtime object type, missing or invalid value, and the first relevant application frame.
- Identify which execution context produced the stack: main model or auxiliary model, producer or consumer, parent or worker process, eager or compiled path. Do not transfer facts between contexts without evidence.
- Separate the primary exception from shutdown, watchdog, communication, and resource-cleanup errors that follow it.
- With multiple logs or distributed roles, build a small role and timeline map before reading deeply: process or rank, role, effective configuration, first abnormal timestamp, first application exception, and later propagated failures. Treat repeated rank-local copies of the same stack as one failure signature.
- Prefer configuration reported after argument parsing over the launch command when they differ. Record role-specific differences separately instead of treating all workers as identically configured.

## Reconstruct necessary runtime facts

Work backward from the failing line. For every enclosing branch, write the condition that must have been true for execution to reach it. Trace the failing value to all of its producers and eliminate producers whose output shape, type, or state conflicts with the observed failure.

Maintain three evidence levels:

- **Observed:** stated directly by the stack, logs, configuration, or inspected runtime object.
- **Deduced:** necessarily follows from observed facts and the inspected source.
- **Hypothesized:** explains the mechanism but still needs runtime instrumentation, metadata, or an operator contract.

Never present a hypothesis as a directly observed fact. When one log line proves only one component's state, do not generalize it to adjacent components.

## Trace both control flow and data flow

Write an unbroken chain from path selection to failure, including intermediate type or representation changes. Verify each arrow against a source line or runtime fact.

Treat related states as independent until proven coupled. For example, an activation carrying a scale does not imply that the next layer's weight is quantized or has a weight scale. Check both sides of an operation and the compatibility assumption between them.

When an operator's return semantics are not visible in Python, infer only what downstream execution proves, then label the remaining semantic explanation as a hypothesis until confirmed by documentation, a minimal probe, or instrumentation.

## Compare against a known-good baseline

Use the same input, execution role, and effective configuration when possible. Find the earliest control-flow or data-representation divergence, rather than reviewing the entire diff first.

1. Extract the bad version's path admission condition.
2. Extract the known-good version's corresponding condition.
3. Substitute the actual runtime configuration into both.
4. Identify the first condition or transformation that produces different behavior.
5. Use blame or commit history only after the divergent code is known, to establish when and why it changed.

Distinguish these conclusions:

- The new path was entered unintentionally.
- The new path was intentionally enabled but downstream handling is incomplete.
- The baseline avoids the bug only because its stricter admission condition makes the faulty code unreachable.

## Close the smallest evidence gap

Before claiming root cause, list what remains unproven. Prefer targeted runtime logging or inspection over downloading or executing an entire system. Useful probes often include:

- selected strategy or preprocessing enum;
- concrete method and layer types;
- dtype, shape, and tuple-versus-tensor state;
- presence of scale or metadata attributes;
- the exact condition that admitted the path.

Stop once the failure chain, first regression divergence, and remaining uncertainty are explicit. Do not propose a concrete conversion, dequantization, or fix until the relevant operator and data-format contract is known.

## Report the result

Lead with a compact causal chain:

```text
runtime fact
-> admitted path
-> representation change
-> invalid compatibility assumption
-> failing expression
```

Then provide the source lines for the admission condition, value producer, branch decision, and failing expression. State separately:

- what is proven;
- what is strongly inferred;
- what one minimal probe would confirm.

For regressions, explain whether the known-good version actually contains a fix or merely cannot reach the defective path.
