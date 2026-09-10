# vLLM regression interface audit

> 中文导读：用于将定位结论变成 UT，或跨 main/release 移植补丁。重点检查真实调用入口、版本分支、测试前置条件和修复前后区分能力。

## Pin the code pair

Inspect branch, HEAD, rebase state, and staged/unstaged changes in the exact worktree the user names. Read the supported vLLM revision from that Ascend revision, then inspect the corresponding tag/commit without switching unrelated repositories. Do not carry line numbers or interfaces from a previously inspected branch into a new conclusion.

## Audit the whole call chain

- Check imports, dataclass constructor fields, inherited defaults, `replace()` behavior, post-init assertions, and page-size padding validity.
- Check type registration and MRO fallback for custom MLA specs, `UniformTypeKVCacheSpecs.from_specs()`, and block-count forwarding. Establish which implementation supplies a method: upstream or an Ascend compatibility patch.
- Inspect configuration helpers. Setting a spec to cache mode `none` does not change a helper that still supplies `align`; different paths can coincidentally return the same expected number.
- Check the actual allocator entrypoint and its version/feature guards. A renamed function with a plausible signature can belong to a different model path. Do not force-call it and present the result as integration evidence.
- Treat `shared_by` descriptors and `layers`/offset/stride descriptors as different contracts. Several descriptors may describe one backing allocation; summing their `size` can double-count it. Conversely, separate old-style tensors may require summing sizes. Read the actual consumer before writing geometry assertions.
- A version-specific planner test may need `skipif`; a grouping-only test using shared interfaces generally does not inherit that restriction. Inspect Python decorator attachment after resolving a conflict; keep independent upstream and candidate tests.

## Compare hardware backends through the effective path

When judging whether another backend shares a defect, trace model registration and platform selection, runner input preparation, the selected model and inherited layer defaults, communication wrappers, and applicable compiler rewrites. Absence of an explicit shard operation in one model class does not establish that its inputs are unsharded.

Record effective feature defaults and the guards that enable an optimization. Distinguish token padding from token partitioning, weight sharding from token sharding, and graph capture from compiler transformations. For an SP rewrite, follow both its entry and exit communications to establish the layout seen by the next ordinary layer. Compare logical token identity at the disputed operation rather than class names alone.

Pin conclusions to the inspected revision and configuration. Separate default-path source reasoning, manually enabled optional paths, and hardware execution; do not generalize a source audit into a claim that an entire backend is free of numerical defects.

## Select assertions that detect the regression

Place new cases beside existing tests of the same helper. For a grouping-gate fix, verify that a valid heterogeneous configuration produces groups, required per-group contracts survive, and incompatible attention sizes still fail. Give negative tests a known-valid starting case.

Use real dimensions where they trigger important contracts, but label synthetic layer arrangements as fixtures, not full production topology. A grouping unit test does not prove physical isolation or numerical accuracy. Add allocator assertions only through the appropriate path for the tested revision; preserve per-layer identity as well as region counts.

When execution is available, run the new tests with the fix, then verify the regression case fails when only the fix is removed in an isolated checkout. Preserve unrelated staged changes. Record the failure assertion: an import error or unrelated exception is not a successful negative control.

## State the validation level precisely

Separate:

1. Source/interface review and syntax/lint checks.
2. Extracted-function execution with lightweight objects or stubs.
3. Full pytest with the real dependency versions and test setup.
4. Hardware/operator or original-workload validation.

One level does not establish the next. Never relabel a missing dependency as a test pass or a product failure. If only theory is requested, inspect rather than install dependencies or run services. Repeated requests to double-check should produce a concrete additional check or an explicit remaining gap, not rising confidence percentages.
