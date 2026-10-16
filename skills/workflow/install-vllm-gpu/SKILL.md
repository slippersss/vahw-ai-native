---
name: install-vllm-gpu
description: Install editable NVIDIA GPU vLLM from a user-selected source repository in a Linux container, reusing compatible PyTorch and commit-matched precompiled extensions for Python development.
---

# Install editable GPU vLLM

> 中文导读：在 NVIDIA GPU 容器中安装源码 editable vLLM；尊重用户是否使用 venv 的选择，复用兼容 PyTorch，记录提交、wheel、依赖变化和实际 CUDA 验证。

Use the repository's remote-work rules. This procedure supports Python development; changes to native kernels require rebuilding their extensions. Consult the checkout's installation documentation and setup.py because wheel selection and native module names change across revisions.

## Preflight and revision

- Confirm the host, container, work directory, Python executable, installed vLLM/PyTorch/CUDA, drivers, GPU visibility, and free space on both the source and package filesystems. If `df` reports zero available bytes, compare statvfs free blocks and available blocks and test a small fsynced write as the actual installation user before declaring the filesystem unwritable. Root may access reserved free blocks; apt's sandbox or available-space check can still reject the same filesystem. Do not remove unrelated data or change filesystem reservations.
- When root writes succeed with enough free blocks but apt rejects available-space checks, authenticated apt indexes plus `apt-get download` into the operational directory and `dpkg -i` can install small prerequisite packages. Use task-local `APT::Sandbox::User=root` only when the sandbox cannot use reserved blocks; retain signature verification. Resolve dependencies explicitly and do not use this path on an actually unwritable filesystem.
- Test network endpoints from the actual container. Keep proxy configuration task-local unless the user explicitly requests persistent settings. Record commands without embedding proxy values in reusable artifacts.
- Clone the requested fork with full history. Record branch, exact SHA, shallow status and working-tree state. Preserve existing user changes. Do not select an older revision merely to fit the image's installed vLLM.
- If the user requests no venv, install with the container's system Python. Otherwise use the agreed environment. Snapshot packages before mutation and keep operational logs adjacent to the source checkout.

## Dependencies and precompiled editable install

1. Inspect the checkout's build requirements and CUDA requirements. Confirm the installed PyTorch satisfies them; constrain its exact installed version while resolving dependencies. If incompatible, resolve the revision/runtime choice before installing mismatched binaries.
2. Use a wheel for the selected commit, CUDA variant and architecture. The wheel metadata's path is relative to its index URL; resolve it correctly. Never silently fall back to an unrelated nightly or another CUDA variant. Validate archive integrity, version and dependency metadata; record URL, SHA256 and commit.
   - Find the wheel through the selected checkout's documented index and its `setup.py` precompiled-wheel selection logic; inspect how that revision resolves fork commits, CUDA variants and platform tags. Do not assume the fork's editable version string is the published wheel filename or construct a URL from an earlier installation.
   - Distinguish an unavailable matching build from a network/proxy failure. If no compatible wheel exists, report the exact revision and missing artifact. Explain the source-build requirements or propose a supported revision/runtime change; preserve the user's requested revision unless they authorize changing it. Do not substitute an arbitrary ancestor wheel merely because it imports.
3. Install missing build tools and resolve runtime requirements using the selected Python. Do not use build isolation if it would install a replacement PyTorch. Inspect installation failures and dependency conflicts rather than disabling their checks.
4. When supported by the checkout, a verified local wheel makes the editable installation reproducible:

   ```bash
   VLLM_USE_PRECOMPILED=1 \
   VLLM_PRECOMPILED_WHEEL_LOCATION=/path/to/verified.whl \
   python3 -m pip install --no-build-isolation --no-deps -e .
   ```

   Use `--no-deps` only after runtime requirements have been resolved. This replaces the packaged vLLM metadata and keeps the source editable. Editable version strings may differ from upstream wheel release labels in a fork; record both and verify the commit rather than rewriting version files.

## Import and FlashInfer pitfalls

- A successful pip install does not prove correct imports. Test outside the repository and from the container's default working directory. A stale `vllm` directory may be selected as a namespace before setuptools' editable finder. If observed, add a narrowly scoped `vllm-source.pth` in the selected Python's purelib directory containing `import sys; sys.path.insert(0, '/absolute/source/root')`. Record this persistent path and update it if the checkout moves; do not delete unrelated source directories.
- FlashInfer Python, cubin and JIT-cache packages must have compatible versions. CUDA local suffixes may be permitted by that release. Do not set `FLASHINFER_DISABLE_VERSION_CHECK` to hide mismatches.
- Install matching optional caches when available. If unavailable, removing incompatible optional cache packages can permit supported JIT compilation when nvcc is present; verify an actual FlashInfer CUDA kernel. This does not prove all model-specific kernels work. Report inaccessible required cubin endpoints and do not circumvent an organizational access block.

## Model-specific startup failures

- If installation checks pass but serving fails, preserve the first worker exception and identify the failing package, its installed source and native artifacts, wheel provenance, GPU compute capability and SM count. Later NCCL/Gloo shutdown errors may be consequences rather than the cause. Do not change model flags or disable warmup to conceal the original failure.
- Observed case: on H20 (78 SMs), one precompiled DeepGEMM build initialized an SM-locality mapping with 39 TPCs and failed an even-TPC assertion during DSV4 startup. The installed DeepGEMM Python/native files matched the wheel; successful imports and RMSNorm checks had not exercised this path. For this symptom, inspect the installed revision's locality initialization and hardware assumptions, then check for a compatible upstream fix or build.
- A narrowly scoped Hopper-only guard around the eager locality-mapping initialization allowed that environment to serve while retaining native initialization. Treat this as a version-specific workaround, not an installation step: establish that the affected mapping is unnecessary on the actual execution path before using such a guard. Preserve the original file, export the patch and hashes, and report the environment as patched. Do not apply the guard automatically to other versions or GPU architectures. Recheck after changing wheels or revisions because editable-install artifacts can be replaced.

## Verify and record

- Assert system Python has `sys.prefix == sys.base_prefix` for a no-venv request.
- Confirm `vllm.__file__` resolves inside the intended checkout, distribution `direct_url.json` declares editable mode, and `pip show vllm` reports the intended editable project location.
- Load the native extension names actually provided by that revision. Run a small vLLM CUDA operation against a torch reference, and a FlashInfer CUDA operation if used. Verify each requested GPU/host separately.
- Check `vllm --help`, `python3 -m pip check`, exact PyTorch version, source status and native artifact fingerprints. Keep stdout, exit codes, source SHA, wheel hash, package snapshots and unresolved limitations. Do not claim model serving or full test-suite validation from these installation checks.
- Retrieve task records locally. Report successful and incomplete hosts independently, explain any remaining blocker, and provide direct commands for using the installed source without an activation step when no venv was requested.
- Report two distinct acceptance levels: **editable installation verified** means the import, metadata, dependency and CUDA-operation checks above passed; **target model serving verified** additionally requires the requested model to finish startup and return a valid single inference response. If the task includes model readiness, use the agreed launch script, preserve startup logs and request/response evidence, and record any compatibility patch. Keep service configuration unchanged during a comparison unless the user requests a change. If weights or free GPUs are unavailable, report model verification as pending rather than claiming serving success; an installation-only task does not authorize extra model benchmarks.
