---
name: deploy-ascend-kv-pooling
description: Prepare, launch and verify MemCache DRAM KV pooling for an existing vLLM Ascend environment, including Meta, storage ownership and optional P/D multi-connector integration.
---

# Deploy Ascend KV pooling

> 中文导读：复用已有环境，先明确Meta、存储owner和推理角色，再验证实际外部KV命中；池化数据面与P/D传输分别配置、分别验收。

## Resolve the actual deployment

Record the intended hosts/containers/devices, installed Python/package paths and versions, vLLM/Ascend revisions/diffs, model/tokenizer and working launch command. Preserve the user's topology, quantization, runner, speculative settings and cache policy unless the requested experiment changes them. Prefer a compatible installed environment; deployment is not authorization to upgrade it.

Inventory these roles independently:

| Role | Responsibility |
| --- | --- |
| Meta / configuration store | Control endpoint, registration and metadata; inspect whether the selected release embeds or separately launches dependencies |
| Storage owners | Actual registered DRAM; standalone processes or contributing inference workers according to the selected route |
| Inference clients | Local HBM and pool lookup/load/save via the store connector |
| Optional P/D services and proxy | Direct P-to-D KV transfer and request routing, separate from history reuse |

Do not assume that starting vLLM starts Meta, or that every deployment needs a separate standalone owner. Check existing healthy owned processes and registration before adding duplicates. Identify pool transport and P-to-D transport separately; service TCP health does not prove the device data path.

Read [Configuration and verification](references/configuration-and-verification.md) for templates, launch order and reuse checks. Check the installed release's supported protocol and hardware mapping; do not copy device IDs, hugepage counts, routes or TLS changes from another host. SSD, raw-disk initialization and unverified transport variants require their own requested scope and matching release documentation; this workflow does not implement them.

## Prepare and launch

Create task-owned Meta/local configs and per-role launchers from the installed package templates, with explicit addresses, ports, storage capacities, device masks and logs. Bind control-plane NIC/IP from the intended route, not simply the first interface. Count real storage allocations and host/NUMA reserves; `world_size` is not a DRAM capacity setting.

For P/D, preserve the working transfer connector and compose `AscendStoreConnector` through the installed multi-connector. Inspect connector registration, role semantics, KV group/layout support and layerwise settings on both roles. A colocated `kv_both` example is not a universal P/D role configuration.

When launch is authorized, start Meta/configuration dependencies, then any selected standalone owners, then inference, then the optional proxy. Wait for each dependency's actual readiness and registration. Use durable jobs, `pipefail` for logged shell pipelines, ownership records and first-error logs. A preparation-only request stops at reviewable configs; no additional confirmation is needed for deployment already authorized by the user.

## Verify and hand over

Verify separately: control service ready, expected DRAM owners registered, inference requests succeed, external reuse observed, optional P-to-D transfer succeeds, and requested benchmark accepted. Do not collapse these into “service up.”

Control HBM history and per-DP routing when checking pool hits. Capture compatible before/after counters and actual token hits rather than inferring reuse from a nominal shared-prefix percentage. Restarting Meta or owners can invalidate existing registrations/cache state; coordinate owned dependent services instead of restarting a shared dependency as a casual health check.

Deliver effective configs, commands, versions, per-role logs, capacities, load/cache boundaries and unresolved compatibility. Stop only owned resources when the user ends the task; verify device workers independently of Meta and CPU-only export/copy jobs.

## Provenance and limits

Internalized from the [ascend-memcache-pooling contribution](https://github.com/mindie-agent/awesome-mindie-skills/tree/5bb728bd5421371af2223dd10518010bc798b1ce/skills/ascend-memcache-pooling) and local DRAM/P-D deployment practice. The original [zouyida2052 contribution](https://github.com/zouyida2052/awesome-mindie-skills/tree/f5108884c387175025eecf2e58021828f802a204/skills/ascend-memcache-pooling) is CC0-1.0; Yuli-yx's integration additions are MIT. See [NOTICE](NOTICE) and the retained MIT license. This local skill is a focused synthesis, not a certification of every A3/A5, Host RoCE or SSD recipe in those sources.
