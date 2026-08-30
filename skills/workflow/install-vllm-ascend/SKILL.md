---
name: install-vllm-ascend
description: Install editable vLLM and vLLM Ascend source builds on a remote Ascend environment, including compatible revision selection, temporary dependency edits, and build-failure handling.
---

# Install vLLM Ascend from source

> 中文导读：用于在远程昇腾环境中从源码配套安装 vLLM 与 vLLM Ascend。先确定兼容版本，再卸载旧包并依次安装；安装期依赖修改必须还原，日志和辅助文件不得污染源码仓库。

Use this workflow together with the applicable remote-work rules. Treat local repositories as the editing source and run installation only in the resolved remote environment.

## Select compatible revisions

1. Ensure `vllm-project/vllm` and `vllm-project/vllm-ascend` clones exist in both the local workspace and the resolved remote work directory. Do not install anything into the local environment.
2. Read the user's request for a vLLM Ascend commit, branch, tag, or latest commit. Ask which to use only when it is not already specified.
3. Fetch when needed, check out that vLLM Ascend revision, and record the exact commit used remotely.
4. At that revision, read `.github/vllm-main-verified.commit` and `.github/vllm-release-tag.commit` to obtain the supported vLLM main and release choices.
5. Read the user's request for a main/main2main or release choice. Ask only when it is not already specified. `main commit` and `main2main commit` both mean the commit in `vllm-main-verified.commit`.
6. Check out the selected vLLM commit or tag. Preparatory local and remote heads may naturally differ by a few upstream commits, but the remote installation revisions must be explicit and compatible with the local edits being synchronized.

## Prepare the remote environment

- If the container cannot reach required package or Git hosts, report the concrete network error and ask the user for the current proxy setup. Treat supplied proxy settings as task-local environment data, not reusable knowledge or repository configuration.
- Remove previous editable or packaged installations with:

  ```bash
  python -m pip uninstall -y vllm vllm-ascend
  ```

## Install vLLM

1. Temporarily remove the `torch` entry from `[build-system].requires` in `vllm/pyproject.toml`. Do not remove unrelated torch references that are not installation requests.
2. Install from the vLLM repository with the container's existing torch environment:

   ```bash
   VLLM_TARGET_DEVICE=empty python -m pip install -v --no-build-isolation -e .
   ```

3. If metadata generation reports `No module named 'setuptools_rust'`, install `setuptools-rust` in the active environment and retry the same command. Respond to observed errors rather than preinstalling speculative dependencies.
4. Treat an explicit `Successfully installed ... vllm ...` as sufficient installation success; do not append redundant package inspection. Restore only the temporary `pyproject.toml` edit immediately, without discarding unrelated worktree changes.

Removing torch and using `--no-build-isolation` are paired actions: removing torch prevents an unwanted CUDA dependency download, while disabling isolation lets the build import the torch already supplied by the Ascend environment.

## Install vLLM Ascend

1. Start with normal build isolation from the vLLM Ascend repository:

   ```bash
   python -m pip install -v -e .
   ```

2. Do not add `--no-build-isolation` by default. If the isolated build fails because the configured index cannot provide the required `triton-ascend`, temporarily remove the matching `triton-ascend` requirement from both `pyproject.toml` and `requirements.txt`, which are mirrored dependency declarations, and retry the same command.
3. Before each retry, synchronize the intended edited files and verify that the local and remote contents match; do not run against an assumed remote state.
4. Treat an explicit `Successfully installed ... vllm-ascend ...` as sufficient success. Restore only the temporary dependency edits, without discarding unrelated worktree changes.

## Long-running installation and cleanup

- Run long installs as durable remote jobs and retain start time, target, PID or job identifier, log, exit result, and finish time.
- Store helper scripts, logs, PID files, timestamps, and status files in a dedicated operational directory adjacent to the remote repositories, never inside either source tree.
- Before reporting the workflow complete, ensure temporary installation edits are restored and both local and remote source worktrees contain no unintended changes.
- Required restoration and artifact cleanup are part of installation completion; redundant `pip show`, import, or version inspections after an explicit success message are not.
- Base the final record on observed commands and outcomes. User recollections are useful leads but do not override evidence from the actual run.

## Handle exceptional failures

The base workflow normally succeeds, but treat failures as environment-specific investigations rather than reasons to replace the workflow with a fixed list of workarounds.

- Find the earliest causal error in the log and distinguish network or index access failures, stale caches or build artifacts, unavailable packages or versions, and genuine source or environment incompatibilities.
- Apply the smallest evidence-backed and reversible correction, then retry from the failed step. Preserve the failed attempt's log so the diagnosis remains traceable.
- Check whether an unavailable build dependency is already supplied by the Ascend environment before deciding to download it, remove its temporary build request, or change build isolation.
- Scope cache cleanup to the implicated package or build directory. Do not broadly clear shared caches without evidence and authorization.
- Adapt to errors not listed here using the same principles; these examples are common failure classes, not an exhaustive decision tree.
