---
name: develop-feature-with-invariants
description: Design and implement a feature across existing dispatch, configuration, data-layout or execution paths, using before/after call-chain analysis, counterexamples, branch-delta review and evidence-backed validation. Use when a local edit changes shared contracts or interacts with fallbacks and other features.
---

# Develop a feature with explicit invariants

> 中文导读：用于需要跨模块推敲的特性开发。修改前还原实际链路与约定，修改后主动找反例、逐分支核对影响，再用有边界的实验闭环；记录选择理由、风险和遗留项。这个推敲过程由开发者主动完成，不依赖用户逐条追问。

## Start here

Use this file as the entrypoint for feature development. Keep design reasoning, development-time debugging, test design, code review and the development log together here. Standalone bug investigations belong in debugging; independently reusable test and measurement procedures belong in testing. Reuse those tools when needed without moving the feature's reasoning and decisions out of this workflow.

Read the operational skills below only when the current task reaches that stage; a narrow review does not require running the entire workflow.

| Current task | Guidance to use |
| --- | --- |
| Understand the contract, compare designs, review changed branches | Continue with the sections below |
| Synchronize code, choose a remote machine, migrate or manage a run | [Remote work](../../workflow/remote-work/SKILL.md) |
| Check vLLM Ascend formatting and pre-PR requirements | [Pre-PR checks](../../workflow/vllm-ascend-pre-pr/SKILL.md) |
| Compare inference quality, acceptance and performance | [Benchmarking](../../testing/benchmark-vllm-ascend/SKILL.md) |
| Capture a workload window or interpret its trace | [Profile collection](../../testing/profile-vllm-ascend/SKILL.md), then [profile analysis](../../debugging/analyze-ascend-profile/SKILL.md) when needed |
| Deliver a requested validation report and reproduction material | [Validation report](../../workflow/write-validation-report/SKILL.md) |

Keep each operational procedure in its linked skill and bring its evidence back to the feature decision record. These links select relevant guidance; they do not authorize additional experiments, remote changes or publication.

## Establish the contract before editing

- Translate the requested behavior into observable acceptance criteria. Separate correctness, intended optimization and compatibility with existing fallback paths. An optimization succeeding does not prove correctness; preserving outputs alone does not prove the optimization ran.
- Read the actual callers, constructors, dispatch points and consumers at the intended source revisions. Trace one complete path with file/function references before changing a gate. Distinguish construction, weight preparation, allocation, metadata preparation, execution and replay; their order determines which facts are available.
- For each disputed value, identify its producer, owner, lifetime and consumer contract. Distinguish shared runtime configuration, the current layer's model configuration and the active construction context; a capability from its actual selection; and a host estimate from a device value used in computation. Follow conversions, views and copies rather than inferring semantics from a variable name.
- Trace explicit constructor arguments through wrappers, backend factories and impl initialization. An argument consumed by a signature is not automatically forwarded through `**kwargs`. Mark where information stops and when later layer markers become available.
- Inspect a nearby implementation that follows the repository's design. Establish where its apparent equivalence ends: wrappers, forwarded properties, fused operations, cache representation, topology and fallback handling can differ. A similar model or a previously tested PR is a comparison, not proof.
- Record which contracts must remain valid and which behavior the feature intentionally changes. For a defect, locate the first violated invariant. A retained parent or target configuration can be intentional. Before replacing it to repair one predicate, trace effects on dtype, quantization, runner identity, preprocessing and weight preparation.

## Decide through counterexamples

Before selecting an implementation, carry out this loop internally:

1. State the proposed change and the reason it should work.
2. Construct the strongest plausible counterexample reachable in the real code, including the path that does not select the new optimization.
3. Trace that case to its consumer and identify the first incompatible contract, or the earlier dispatch that excludes it.
4. Compare a narrower alternative that preserves established interfaces. Choose on semantic fit and verified coverage, not line count alone.
5. Re-run the reasoning against the resulting patch. Keep the changed invariant, rejected alternative and decisive evidence in the development log.

Do not turn this into prolonged user arbitration. Resolve source-answerable questions independently; involve the user for a real design choice or missing requirement.

During a user-led code review, follow the requested file-by-file or change-by-change pace. Explain the current disputed change before advancing to adjacent changes or experiments. If the user asks to slow down, stop expanding the implementation. Preserve user-designated staged snapshots and keep subsequent edits unstaged when requested. Review pacing does not introduce an additional approval requirement for ordinary authorized development.

If a proposed fix appears to require a new buffer, marker, copy or special case, first trace why the existing mechanism was unavailable. Repair the mistaken eligibility or preparation decision when that restores the intended contract; do not accumulate workarounds around an unproven premise. When a premise changes, revisit dependent decisions and remove obsolete scaffolding.

## Analyze the branch delta

When deleting, delaying or combining a condition, compare the old and new reachable paths, not only the desired example.

- Enumerate each intervening return, mutation and call, in order. For every newly admitted input class, determine whether it returns the same value, reaches the intended new path, or now reaches another consumer with stricter assumptions.
- Read the predicate body rather than inferring protections from its name. Distinguish an actual object's property from a global classification used by the guard. Test both: the current object really has the excluded property; another object supplies that classification while the current object does not.
- Establish exclusions from concrete dispatch code, including alternative selectors and subclass paths. An implementation type can prove a route only under the normal construction contract; document forced/custom backend exceptions when relevant. When a guard's purpose is disputed, inspect blame and the introducing change at each call site: an impl guard and a shared allocator guard can protect different contracts. Removal at one site does not justify global removal; attribute author intent only when supported by the source or discussion.
- Check downstream dependents of the new selection: allocation and reshape must agree on layout; readers and writers must agree on dtype, strides, views and backing storage; preparation and replay must agree on metadata and lifetimes.
- Trace fallback separately. Distinguish selection-time rejection from execution-time failure; a failed kernel need not fall back. A backend family label may be too coarse to decide whether a host value or synchronization is required.
- Before adding a new flag, check whether existing arguments, selected backend types or impl inheritance already establish the required property. If selection must be shared, reuse the actual authoritative selection at a stable lifecycle point. Check initialization order, repeated setup, empty collections and mixed groups. In particular, `all(...)` on no groups cannot establish that an optimization was selected. Do not invent a second architecture name for a sub-mode merely to redirect unrelated branches.
- Build a compact affected-case table when useful: input class, old path, new path, consumer requirement, evidence and remaining gap. Cover relevant interactions, not a speculative Cartesian product of all features.

## Debug during development

- Tie an unexpected result back to the changed invariant and the before/after paths. Reproduce against the appropriate baseline with equivalent inputs before attributing the failure to the feature.
- When debugging with probes, verify the final callable after platform patches and model initialization. A factory can replace the function instrumented at import time; inspect its resolved global/closure binding and the final consumer hook. Require bounded live probe output before claiming the path was observed. A successful API request alone does not prove the probe ran.
- Investigate an apparent regression before dismissing it as variation: repeat the same state, inspect per-request/per-position or time-window evidence, and control relevant scheduling or numerical variables. A deterministic seed does not prove cross-batch numerical invariance. Record what has been isolated and what remains a hypothesis.
- Keep temporary diagnostic patches separate from fixed-revision comparisons. Record and restore them before final validation; evidence from an instrumented variant must identify that variant.

## Validate the changed contract

- Test the new behavior and meaningful fallback or boundary cases introduced by the branch delta. For a defect fixed during development, include a regression test that fails before the fix. Avoid testing incidental formatting or copying implementation logic into assertions.
- Separate production changes from test-fixture repair. If a test bypasses constructors, determine whether a missing field is a stale fixture or a production initialization defect before adding attributes. Keep unrelated failures out of scope.
- Run formatting and relevant tests on the actual final tree. If broader tests fail, compare the same failing nodes against the appropriate baseline before claiming they are pre-existing. Report remaining failures explicitly; “no new failure” is not “all tests pass.”
- When assessing existing E2E, nightly or weekly coverage, resolve the actual workflow, matrix and case configuration before tracing their inputs through the patch. Distinguish entering a changed function from taking a changed branch. Record which cases exercise the new behavior, preserve the old fallback, or miss the feature entirely; names and similar models do not establish coverage. Read the actual assertions and thresholds: an aggregate metric cannot replace a per-position or per-rank requirement. Static exclusion and CPU tests do not establish hardware E2E success.
- Use runtime evidence to confirm the intended path and its fallback behavior where authorized. Record actual imports, source state and effective configuration; a synchronized Git checkout does not establish that an already running process loaded it. Use the linked remote-work procedure for synchronization and owned-process handling.
- Keep correctness, acceptance/quality, latency/throughput and profiling measurements distinct. Freeze workload and sampling controls before comparisons. Keep counter windows and metric denominators consistent; do not mix warmup, tails, incomplete trials or different cohorts. Use the linked benchmark/profile procedures for these mechanics.
- After rebase, verify patch equivalence and the resulting source state, then perform proportionate validation on the new base. Historical results do not become measurements of the rebased version.

## Leave a usable decision record

Maintain the project development log as part of the feature, rather than reconstructing it from chat afterward. Keep the current decision easy to find and clearly mark superseded approaches.

Keep a dated current-state summary at the front, with the verified revision, completed evidence and still-open risks. Refresh it when later validation resolves a concern or changes its scope; appending a result at the end does not correct a stale summary. Retain historical failures with their original revision and configuration, and distinguish an open cause from a defect reproduced on the final code.

For each material change, retain:

- Problem and invariant; exact affected file/function and source identity.
- Before/after behavior, the decisive call or branch chain, and why the chosen change fits the existing design.
- Rejected alternatives and the concrete contract or counterexample that rejected them.
- Validation evidence, workload/configuration identity and the scope it actually proves.
- Risks ordered by consequence: unresolved correctness or configuration ownership first, then feature interactions and unsupported hardware/topologies, then performance and maintenance limits. Separate a confirmed defect, an untested boundary and a resolved concern.
- Pending work, temporary patches, environment changes and restoration/resource state. Close stale “running” statements when authoritative evidence is available; preserve failed trials with their exclusion reason.

At handover, use the linked validation-report procedure when a report is requested. Preserve reproducible inputs and scripts, distinguish historical and current results, and state unresolved limits. Promote only validated, reusable reasoning into skills; model names, commit IDs, operator restrictions and one-off experiment numbers belong in project records.
