---
name: profile-vllm-ascend
description: Collect a bounded vLLM Ascend serving profile during a representative workload window, with explicit role/rank coverage and verified exports.
---

# Profile vLLM Ascend serving

> 中文导读：采集真实请求中间的稳定窗口，明确P/D与各rank覆盖，区分停止采集、导出完成和卡资源释放。

## Prepare the window

Inspect the installed vLLM/Ascend/torch_npu profiler interfaces. Configure a task-owned output root and the requested stack/shape settings before launching or reusing a service. Record effective configuration and code revisions. Preserve the model, graph mode, cache settings and topology being diagnosed.

For a release accepting the inspected JSON interface, add the following fragment to the existing service launcher, replacing the path with a writable container-visible directory:

```bash
--profiler-config '{"profiler":"torch","torch_profiler_dir":"/absolute/task/profile","torch_profiler_with_stack":true,"torch_profiler_record_shapes":true}'
```

Confirm the installed profiler schema accepts these keys; older integrations differ. Shape recording is useful for padding attribution, and stack/shape collection costs belong to the diagnostic cohort. Do not restart an active measured service merely to add this fragment without fitting the requested experiment.

Define the role and expected rank/worker outputs; API processes, DP ranks and devices are not interchangeable counts. Resolve whether one API's profile call fans out to all required workers. Do not assume the benchmark proxy forwards profiler endpoints or call the same engine twice through aliases.

Choose a window by the phenomenon: sustained running/waiting work, a scheduled progress boundary, or an explicit request cohort. For a middle-window request, start the ordinary benchmark first, observe that the intended load/cache state exists, then start profiling while it continues. Starting profiling before a separate short request wave is a different experiment. A fixed sleep without load evidence is not proof of a stable window.

Retain a clean performance run separately from the profiled diagnostic. Trace overhead, stacks and export work can change scheduling and throughput.

## Control and close

The included [profile_control.py](scripts/profile_control.py) sends one action to an already running, explicitly selected service root. Set `SKILL_DIR` to this skill's absolute directory and `RESULT_DIR` to an existing, unique task output directory; commands work from any current directory:

```bash
python "$SKILL_DIR/scripts/profile_control.py" --base-url "$P_API_ROOT" --action start_profile --output "$RESULT_DIR/start.json"
# Existing benchmark continues; record request progress and per-rank load.
python "$SKILL_DIR/scripts/profile_control.py" --base-url "$P_API_ROOT" --action stop_profile --output "$RESULT_DIR/stop.json"
```

The independent control timeout accommodates profiler setup/finalization. A timeout or connection loss leaves action completion unknown; inspect service logs/state before retrying. Do not start a duplicate capture because the HTTP client timed out. For multiple engines, record each result; if only some start, close the known-started captures within authorization and preserve the partial failure.

`--output` refuses to overwrite an existing result before issuing the HTTP action. Use a fresh result path for a new trial; do not treat this local refusal as evidence that the remote profiler stopped. Reach the root through the intended network route; the helper does not launch an SSH tunnel or bypass environment proxy settings.

Stop within the agreed window even if the benchmark continues. Use an ordinary follow-up request only when the installed implementation requires it for finalization; keep it outside clean benchmark counts. On cancellation or benchmark failure, close an active capture when possible and retain its invalid/partial status.

## Verify evidence and release

- Preserve control timestamps/responses, client progress, start/stop load, service logs and request success counts. HTTP 200 alone does not establish a useful profile.
- Inspect every expected output. Ascend analyzed exports commonly contain `ASCEND_PROFILER_OUTPUT/kernel_details.csv` and `trace_view.json`; use the installed export schema. If only raw profiler data exists, run the installed offline analysis/export procedure and record its status.
- A middle window may miss rare failures. Inspect all ranks and use full-run host admission/lifecycle counters to establish whether the target event occurred. Missing evidence is not evidence of no anomaly.
- Save raw captures, exported tables/traces and rank mapping before cleanup. Distinguish capture stopped, export complete, local copy complete and workers stopped. Offline CPU analysis can often continue after device workers are released; verify which process still owns device resources instead of reserving cards for file transfer.

For long-job ownership and handover use the repository remote-work workflow.

## Provenance

Internalized from the collection contract and control helper in [pisceskkk/vllm-ascend-skills](https://github.com/pisceskkk/vllm-ascend-skills/tree/4e7417c3d88847a17ba6d61d6a9b748ad8e0bbc3/skills/vllm-ascend-profiling-collection), MIT, Copyright 2026 Qi Mao. The local helper adds transport-error records, timestamps and durable response output; the upstream license is retained in `LICENSE`. Middle-window selection and release boundaries incorporate local serving-debugging practice. Endpoint/export behavior remains release-dependent.
