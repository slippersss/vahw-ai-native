# Configuration and verification

## Inspect the installed release

Use the actual interpreter and preserve output:

```bash
python3 -m pip show memcache-hybrid memfabric-hybrid vllm vllm-ascend
python3 -c 'from pathlib import Path; import memcache_hybrid; print(Path(memcache_hybrid.__file__).resolve().parent / "config")'
```

An import can fail before a service launches due to missing native dependencies. Inspect the first loader error and the actual extension's dependencies (`ldd` where applicable). Use matching existing libraries in the task launcher when justified; do not globally replace system OpenSSL or unrelated packages. A host import working does not prove a container import works.

Copy the installed `mmc-meta.conf` and `mmc-local.conf` into the task directory. Inspect accepted keys in that release. The following known key names describe the roles, not a complete cross-version config:

| Config | Keys and meaning |
| --- | --- |
| Meta | `ock.mmc.meta_service_url`, `ock.mmc.meta_service.config_store_url`, `ock.mmc.meta_service.metrics_url`: distinct reachable/bind endpoints |
| Local participants | `ock.mmc.meta_service_url`, `ock.mmc.local_service.config_store_url`: agree with the selected Meta deployment |
| Membership | `ock.mmc.local_service.world_size`: supported membership ceiling, not model DP/TP or registered storage size |
| Storage | `ock.mmc.local_service.dram.size`, `ock.mmc.local_service.max.dram.size`: actual contribution versus release-specific reservation |
| Pool data plane | `ock.mmc.local_service.protocol`: selected supported transport, not the P/D connector protocol |

Resolve alignment, units and reservation rules from the installed templates. Compute registered capacity by summing actual owners' aligned contributions, not multiplying a maximum reservation by an intended rank count. Budget model/runtime host memory, transport staging, OS reserve and any hugepage/NUMA constraints separately.

The upstream standalone SDMA route uses separate owners and zero-DRAM inference clients; a contributing-worker route has different ownership. Select the installed supported arrangement rather than combining half of each. Do not change kernel modules, routes, devices or global memory settings just because a recipe mentions them.

## Meta and owners

For releases exposing the Python entrypoint, a task-owned Meta launcher contains:

```bash
set -o pipefail
export MMC_META_CONFIG_PATH="$DEPLOY_DIR/mmc-meta.conf"
python3 -c 'from memcache_hybrid import MetaService; MetaService.main()' 2>&1 | tee "$DEPLOY_DIR/meta.log"
```

Verify `MetaService` and the template in the installed version before executing. Keep process identity and listen/registration evidence. If a config-store process must be separately launched in that version, use its installed documented entrypoint; do not invent a universal command from a different release.

Where the selected standalone-owner route exposes `DistributedObjectStore`, its owner initializes on the allocated visible device, verifies the returned result and remains alive. The exact `init` arguments and return contract are release-dependent. Owner initialization/registration must finish before inference loads consume the intended resources. A client-only launcher with no owner contributes no pool capacity.

## Inference and P/D composition

Set `MMC_LOCAL_CONFIG_PATH` per participant. Preserve the working library paths; prepend only required task-owned directories. Inspect the installed `AscendStoreConnector` for accepted `backend=memcache`, layerwise, lookup and namespace fields.

For P/D, inspect all children of `MultiConnector`: transfer role, engine/rank IDs, DP/TP metadata, KV ports and completion ownership. Pooling does not replace direct P-to-D transfer. Local prefix caching, external lookup and `do_remote_decode` are independent choices; enabling one does not imply the others. Keep compatible hashing/model/layout among participants or use a supported separate namespace for incompatible representations.

Two containers on one machine are not automatically isolated pool deployments. Check shared Meta/config paths, namespaces, ports, device ownership and DRAM budgets before concurrent ON/OFF tests. Reuse shared services only when their state and interference are compatible with the comparison.

## Readiness and reuse checks

1. Verify Meta/config endpoints and owner registration/capacity, then inference health and a successful request.
2. Preserve a frozen prefix set and warm every intended cache domain/rank. Repeat the prefixes with different frozen suffixes to distinguish prefix reuse from entire-request reuse.
3. Capture before/after HBM query/hit, external query/hit and scheduled-token counters over the same interval for all relevant ranks. Account for local HBM reuse before attributing reuse to the external pool. Use supported targeted resets only after inspecting their scope; a whole-pool reset is not an HBM-only reset.
4. For P/D, verify remote receive/read completion and successful routed response separately from pool history hits.
5. Retain native AISBench results for performance acceptance, including duration, actual inputs/outputs, failures and primary metric. A custom diagnostic client is a separate metric cohort.

Combined reuse can be `(HBM hit tokens + external hit tokens) / HBM query tokens` only when the counters have compatible populations and external queries correspond to local misses. Do not add percentages with conditional denominators or mix cumulative and interval counters. Service-ready logs alone do not prove reuse or throughput.
