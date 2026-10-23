---
name: benchmark-vllm-ascend
description: Plan and run reproducible vLLM Ascend inference performance comparisons, including P/D deployments, frozen AISBench workloads, concurrency scans, latency matching, acceptance metrics, and evidence-based reports.
---

# Benchmark vLLM Ascend

> 中文导读：从真实的 AV ON/OFF、DSpark/MTP、proxy worker 和数据量实验中提炼。用于固定负载、检查供给链路、扫描并发、配平平均 TPOT、核对统计并归档。示例参数是一次实验的设置，不是通用最优配置；不涉及自动修改模型源码。

## Establish the comparison

- Identify the question: same-concurrency comparison, throughput at a latency target, proxy capacity, or model execution cost. These require different evidence.
- Record the methods, workload, topology, primary metrics, allowed changes, and stopping condition before a long sweep. Follow the user's requested scan before expanding into matching or debugging.
- Separate a single-feature comparison from an end-to-end deployment comparison. Different weights, graph sizes, runner paths, or instrumentation are additional variables even when the labels are only ON/OFF.
- Use existing installation and remote-work skills when needed. This skill does not authorize new deployments, code changes, or additional experiments beyond the task.

## Tools and effective configuration

For executable setup, configuration and result handling for **native AISBench**, **vLLM bench serve**, or **aisbench_auto_tools_prefix**, read [Client execution recipes](references/clients.md). Support all three; use the user's selected entrypoint rather than silently substituting the wrapper for native AISBench or changing clients mid-comparison.

Use the installed tool versions and their actual README/source as the command authority. Do not assume flags are stable across releases.

For prefill-only, prefix-reuse or pooled P/D comparisons, read [Prefill and cache comparisons](references/prefill-and-cache.md). It covers arrival replay, native throughput definitions, all-rank cache coverage and topology equivalence.

Upstream sources:

- [rayn-zzz/aisbench_auto_tools_prefix](https://github.com/rayn-zzz/aisbench_auto_tools_prefix), with its [README](https://github.com/rayn-zzz/aisbench_auto_tools_prefix/blob/main/README.md): the wrapper providing `aisbench_test.py`, `config.py`, dataset generation and prefix-cache test options.
- [AISBench/benchmark](https://github.com/AISBench/benchmark): the underlying AISBench engine; it is a separate repository from the wrapper.

Record the wrapper revision and local modifications when preparing a benchmark. The historical campaign's retained wrapper copy has not been matched to an exact upstream commit; do not present it as an unmodified upstream checkout or assume today's main branch reproduces it.

|Purpose|Tools used in this workflow|What to retain|
|---|---|---|
|Service|`vllm serve`, P/D launch shell scripts|Full arguments, environment, startup logs and effective configuration|
|P/D routing|Repository example proxy with worker support|Exact proxy source, command, backend list and worker count|
|Client|AISBench through `aisbench_auto_tools_prefix/aisbench_test.py`|Wrapper plus dependency files, generated AIS configuration, native results and request records|
|Alternative client|`vllm bench serve`, when requested|Separate client cohort and its metric definitions|
|Health and counters|HTTP health/model endpoints and `/metrics`, e.g. via curl/Python|Before/after snapshots with timestamps and rank labels|
|Load observation|D running/waiting metrics; process CPU and device monitoring as needed|Raw time series, collection interval and measurement window|
|Analysis|Python, CSV/JSON and standard plotting libraries|Raw values, derivation code and figures|

For each node, capture the actual Python executable, imported vLLM/Ascend paths, package versions, repository revisions/diffs where available, image identity, relevant native artifacts, model/tokenizer identity, hardware and runtime versions. An image tag or Git HEAD alone does not prove the code loaded by workers. Mark missing provenance explicitly.

Record DP/TP/PCP/EP, API server counts, P/D connection metadata, max sequences, batched-token limits, KV capacity, memory utilization, cache policy, scheduling, speculative method/length, AV flag, draft eager/graph mode, main graph mode and capture sizes. Save effective startup values rather than only requested flags. Preserve the AV cost table actually used by the measured instance if available; a later restart's profile is a different observation.

Do not transplant TP settings into PCP or replace model families/parsers without checking compatibility. When changing a method, enumerate every required change, including weights and restarts.

## Freeze the workload

1. Choose the source data and tokenizer. Save the exact selected texts and order, not just a seed or source row numbers. Stateful sampling, picked-ID files and regenerated outputs can defeat apparent seed reproducibility.
2. Generate once, then pass the frozen dataset explicitly on every run. If a matching output file exists, validate its contents/parameters before reusing it; do not silently replace it.
3. Record source diversity, expansion/repetition rules, request count N, concurrency C, generation parameters and expected output length. Expanding 32 prefixes into N requests does not create N independent questions.
4. Validate both raw-text and post-chat-template input lengths using the actual tokenizer/template. `16384` raw tokens need not mean `16384` tokens received by the service.
5. Keep output controls fixed, such as temperature, max output length and ignore-EOS behavior. Check actual output counts and failures afterward; a max-token limit alone does not ensure fixed output.

Repeated text, repeated requests and prefix-cache hits are separate properties. Describe the constructed load as a performance workload, not an accuracy evaluation.

When a reusable data generator is needed, expose workload-defining inputs and derive meaningful output names. Validate exact counts, ordering and length semantics, including non-divisible expansion sizes. Reuse only identity-matched files and reject conflicts; verify generation, reuse and conflict behavior before formal use. Do not add a generator when frozen data already suffices.

## Validate the supply chain before interpreting model speed

- Inspect client → proxy → P → transfer → D. Configured concurrency is not actual D running, and resident running requests are not the exact verification shape of each step.
- Check all DP ranks, queueing, P feed, API server capacity, proxy CPU, cache hits, KV pressure, preemption/recompute and graph/eager paths when these can explain the result. Aggregate averages can hide a limiting rank.
- Sweep proxy workers with the same P/D instance and workload when worker count is the intended variable; restart only the proxy, wait for health and drain between runs. Restart the affected services when model, graph or other startup configuration changes.
- Use throughput, latency and D load together to assess feed capacity. A higher worker count or a single CPU sample alone does not prove a bottleneck was removed.
- Treat extra probes as a separate measurement state. No new DP collective does not imply zero overhead: CPU bookkeeping, copies and logging can still affect timing.

## Per-run protocol

Before execution, resolve a concrete run sheet: target/container and working directory per role; P/D service scripts and endpoints; exact proxy and wrapper directories; dataset path; C/N grid; counter and running collectors; output directory; restart/warmup policy; and latency-matching rule. Inspect `aisbench_test.py --help`, its README and generated configuration in the intended environment. Do not assume helper filenames from a past report exist in a new checkout. If a needed collector/helper is absent, prepare and validate it before the formal run rather than promising metrics that will not be collected. The command examples below require an already installed service/client stack; this skill does not bundle that stack or the historical helper scripts.

1. Assign an experiment/cohort and trial ID; snapshot launch and client configuration. Keep diagnostic, warmup, failed and formal trials distinct.
2. Check P/D and proxy health. For a hot-prefix experiment, warm every P cache domain with every frozen prefix, then exercise the full proxy path with short output. Verify the intended routing rather than assuming load balancing visits every rank.
3. Drain P/D running and waiting. Save before counters and start timestamped running sampling. Keep unrelated traffic outside the measurement window or mark the trial contaminated.
4. Run the client with explicit dataset, C, N, input/output lengths and request-rate settings. Retain the wrapper-generated configuration so defaults can be audited.
5. Wait for completion and drain. Save after counters, exit status, native summary, per-request timing, available SSE records, service/client logs and running samples.
6. Verify success/failure totals, actual lengths, cache state and service identity. Preserve invalid trials with an exclusion reason instead of deleting them.

Prewarm again after a restart when cache/profile state changes. Exclude warmup from counter deltas and formal throughput. For long jobs, use durable execution and status/log/PID artifacts; a tool timeout does not mean the remote job failed. Stop only verified task-owned processes and confirm worker/device release on handover.

## Scan first, match afterward

- Use the agreed concurrency grid with the same workload policy for all methods. Keep all points, including poor results and repeated trials.
- Choose N to sustain the intended load without excessive runtime. `N=4C` was a useful campaign convention, not a guarantee that ramp-up and tail effects disappear. Changing C and N together changes both factors.
- At the same C, classify ON relative to OFF:

|Output throughput|AVG TPOT|Interpretation and next action|
|---|---|---|
|Higher|Lower or equal|Dominates this observed point; retain for later matched comparison|
|Higher|Higher|Tradeoff; approximately match latency before claiming a benefit|
|Lower|Lower|Tradeoff; approximately match latency before classifying|
|Lower|Higher or equal|Dominated in this observation; investigate or repeat if the difference may be noise|

- For matching, use the requested statistic, typically AVG TPOT, not P90. Specify whether tolerance means each method is within target ± epsilon or the pairwise gap is at most epsilon. The former does not imply the latter.
- Use scans to choose nearby candidates, then measure new trials. Label interpolation as an estimate, never as a measured matching result. Retain all search trials and actual residual TPOT differences.
- Repeat important comparisons when variation changes the conclusion. Keep independently executed cohorts separate; disclose execution order, service reuse/restarts and aggregation rather than averaging away differences.

## Metric semantics

Check the installed client's implementation before applying formulas. Preserve native results; label independently recomputed diagnostics separately.

- **Output throughput:** distinguish output-only tokens/s from input-plus-output throughput. For a full-run window, a common definition is total output tokens divided by first submission to final completion.
- **AVG TPOT:** typically the request-weighted mean of `(last_output - first_output)/(output_tokens - 1)`. It is not the reciprocal of aggregate throughput. Handle short/failed outputs according to the client's definition.
- **ITL:** establish whether it measures token intervals or streaming-event intervals and how it weights events/requests. One SSE event can contain multiple tokens. Client ITL is not automatically server verification-step time.
- **ITL/TPOT:** retain as a consistency aid, not an exact acceptance length. Different aggregation and streaming behavior can produce discrepancies, even values above spec+1.
- **Acceptance:** subtract before from after counters for the formal window; sum compatible per-rank counts before dividing. Common native length is `1 + accepted_tokens/draft_rounds`; position i is `accepted_at_i/draft_rounds`. Verify the source semantics first. Cumulative per-position ratios are not conditional probabilities given acceptance at the previous position.
- **AV pruning:** native denominators may include positions never verified. Do not call this actual-sent acceptance or infer an execution bug from a lower native ratio alone. Actual-sent diagnostics need sent counts and correctly aligned accepted positions, including zero-sent requests/rounds. Record instrumentation overhead and compare representative workloads after any small reproducer.
- **Running:** retain the rank series and the aggregation/window definition. Report median and requested P60/P70/P80/P90; explicitly say ascending or descending. Descending P80 corresponds to ascending P20. Distinguish sample-weighted from time-weighted statistics.

Collect C, N, success/failure, actual lengths and the primary metric required by the question. For multi-token decoding comparisons, also retain output throughput, AVG TPOT, AVG ITL, ITL/TPOT, running distribution and applicable acceptance counters. For one-token prefill tests, prioritize input throughput, native prefill throughput, TTFT, duration, cache hits and scheduled work; TPOT and ITL may be undefined. Mark unavailable or inapplicable fields explicitly rather than inventing zero values.

### Required result record

Use one machine-readable record per trial plus raw time series/counters. The names below are a suggested schema; map installed-tool fields explicitly rather than requiring these spellings.

|Group|Fields to retain|Source and interpretation|
|---|---|---|
|Identity|experiment_id, trial_id, service_instance_id, method, spec, AV, code/config/dataset identity, warmup/formal/diagnostic status|Run sheet; distinguish restarted services and independently measured cohorts|
|Load|C, N, request_rate, prefix_count, input_raw_tokens, input_chat_tokens, actual_output_tokens, proxy_workers, P/D API counts|Frozen data, effective configuration and native request records|
|Primary|output_tokens_per_s, avg_tpot_ms, avg_itl_ms, itl_over_tpot, successful_requests, failed_requests, formal_window_s|Native client results; retain original precision and units|
|D occupancy|running_mean, running_max, running_median, running_P60/P70/P80/P90_descending, sample_count, sample_interval_s, window definition|Sum compatible D rank gauges per aligned timestamp, then summarize; keep each rank too. Missing rank samples must not silently become zero|
|Acceptance|draft_rounds_delta, draft_tokens_delta, accepted_tokens_delta, accepted_per_position_delta[], native_accept_length, per_position_all_rounds[]|Raw before/after series with labels and reset checks; include actual-sent counters only when collected|
|Supporting|TTFT AVG/P90, TPOT P90, E2EL AVG/P90, QPS, P cache-hit ratio, waiting, preemptions/recompute, proxy CPU|Preserve native definitions; use counter deltas for window rates, not lifetime percentages|
|Timing evidence|request_id, submitted_at, first_output_at, completed_at, output_count; SSE times and event token counts if available|Client clock and units; retain clock offsets when correlating different machines|
|Reproduction|launch scripts/env, generated client config, collector/source versions, log/result paths, exit status, exclusion reason|Keep locally resolvable artifacts; public copies use deployment variables|

Resolve Prometheus series by metric name plus labels, not line position. Discover exact names in the running version. Multiple API endpoints may expose duplicate engine series: deduplicate by engine/rank identity before summing; TP replicas are not automatically independent request populations. A counter decrease or changed engine identity means reset/restart, not negative activity. A cached metric export may lag completion; use bounded repeat snapshots to establish completion or mark the delta incomplete rather than silently using stale values.

For compatible native semantics, cross-check `native_accept_length = 1 + accepted_tokens_delta / draft_rounds_delta`; `per_position_all_rounds[i] = accepted_per_position_delta[i] / draft_rounds_delta`; and `1 + sum(per_position_all_rounds)` against the length. Zero rounds mean undefined, not zero acceptance. Position totals should sum to total accepted tokens only when the implementation counts the same population. Keep raw counts when this invariant fails and investigate label/window/semantic mismatch.

For matched comparisons, include baseline trial ID, target/tolerance definition, actual pairwise TPOT gap and `throughput_gain_pct = 100 * (candidate_tps / baseline_tps - 1)`. Do not round inputs before computing gains or use target TPOT instead of measured TPOT. Provide a compact comparison table with C/N, throughput, TPOT, ITL, ITL/TPOT, running median/P60/P70/P80/P90, acceptance length and per-position ratios; split wide tables by the same trial ID if needed.

## Cost profiles, saturation and tails

- For measured verification cost T(B) in milliseconds, `SPS=1000/T(B)` is verification steps/s at shape B; `B*SPS` is processed positions/s if B counts positions. Neither is final accepted-output throughput, and neither includes draft/end-to-end overhead unless the measured timer does.
- Compare marginal cost over shapes to identify candidate useful pruning ranges. Check actual occupancy and execution paths. A rising T(B), a throughput gain or a fixed TPOT target alone does not prove strict hardware compute-bound operation.
- When throughput changes while average latency looks stable, reconstruct submission, first-output and completion timelines. Compare ramp-up, last submission, completion percentiles and final tail before attributing the change to kernels or acceptance.
- Keep full-run metrics as the primary result when that is the agreed protocol. A steady-state diagnostic must define its time/cohort boundary and denominator explicitly. Selecting only requests that both start and finish inside a window excludes slow boundary-crossing requests and can bias results.
- Completed requests' entire outputs divided by a window duration is not actual in-window token throughput. Without per-event token counts, do not claim an exact token-arrival throughput reconstruction.

## Illustrative configuration and commands

The following is the historical campaign shape, not a turnkey service recipe or portable optimum:

|Setting|Example|
|---|---|
|Topology|1P1D; each node DP16 × TP1, EP, MRV2|
|Servers|P API1, D API16; proxy4 workers|
|P|Prefix caching on, eager; max sequences128; batched tokens4096|
|D|Prefix caching off, async; max sequences128; batched tokens1024; FULL_DECODE_ONLY|
|Methods|DSpark5 AV ON/OFF; separate MTP1 weights and method|
|Graphs|ON maximum512; OFF explicit sizes maximum510; MTP default. This is an additional comparison variable|
|Workload|Frozen GSM8K32, raw input16384, observed chat input16467, output1024, temperature0, ignore-EOS|
|Grid|C=64,128,256,384,512,640,768,896,1024; N=4C|
|Worker probe|2,4,6,8,16 at C1024/N4096, plus N8192 at worker4|

For the `aisbench_auto_tools_prefix` wrapper, configure `HOST_IP/HOST_PORT` for the proxy, `MODEL_NAME`, tokenizer `MODEL_PATH`, installed `WORK_PATH`, writable `OUTPUT_DIR`, and `POD_INFO` for the actual P endpoints. A client's localhost is not necessarily P. Retain the wrapper dependency files, not only its entry script.

With an already generated and validated dataset, run from the wrapper directory:

```bash
C=768
N=$((4*C))
DATASET=/absolute/path/to/frozen_GSM8K_N3072.jsonl
python3 aisbench_test.py --dataset "$DATASET" \
  --input_len 16384 --output_len 1024 --data_num "$N" \
  --concurrency "$C" --request_rate 0 --dataset_type normal
```

Here `normal` consumes the already expanded file; it does not imply no shared prefix. Generating with `--dataset_type prefix_cache --prefix_num 32 --repeat_rate 1.0 --seed 1` is a distinct preparation operation whose exact behavior must be inspected in that wrapper version. Freeze its output before formal reuse.

For the worker-capable proxy used in this campaign, the interface was:

```bash
python3 proxy.py --host "$P_IP" --port 2277 --workers "$WORKERS" \
  --prefiller-hosts "$P_IP" --prefiller-ports 8100 \
  --decoder-hosts "$D_IP" --decoder-ports 8200
```

Do not assume another similarly named proxy implements the same CLI or worker behavior.

## Archive and present

- Retain per-trial configuration, frozen input identity, raw results, generated client configuration, logs, counter snapshots/deltas, load series, timings and exclusion reasons. Preserve the actual tool/proxy/service scripts needed for reproduction.
- Separate execution records from reader-facing material. Keep secrets and personal addresses out of reusable skills and public reports; parameterize network, model and directory paths.
- Structure the report around question, method, results, limits and conclusion; put full configuration, scripts, data definitions and reproduction steps in appendices. Use relative assets so the report directory can move together.
- Plot throughput versus concurrency and throughput versus actual AVG TPOT, with consistent method colors. Show independent cohorts and measured matching points distinctly. Do not connect points across independent runs or hide failed search attempts.
- Check table/figure values against native artifacts and derived-counter formulas. Count trials once: repeated exports, frozen subsets and summaries are not additional experiments.
- State observed facts separately from inferred explanations and unresolved causes. Never convert a case-specific worker count, TPOT threshold or graph capacity into a general recommendation.
