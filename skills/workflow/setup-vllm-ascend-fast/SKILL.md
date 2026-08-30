---
name: setup-vllm-ascend-fast
description: Bootstrap a local/remote vLLM Ascend workspace from a container image that already provides installed editable repositories under /vllm-workspace, without rebuilding either package.
---

# Set up a fast vLLM Ascend workspace

> 中文导读：用于容器镜像已经在 `/vllm-workspace` 内准备并安装好 vLLM 与 vLLM Ascend 的场景。远程工作目录通过软链接复用镜像源码，补全浅克隆的 vLLM 历史并保留镜像原始 commit；随后在本地克隆官方仓库并切到完全相同的 commit。此流程不重新安装软件。

Use this workflow for the image-based fast path. Use the source-install workflow instead when the container does not already provide usable editable installations and source repositories.

## Resolve and inspect the fast environment

1. Resolve the target machine, container, remote user directory, and requested work-directory name. Do not infer them from an earlier task.
2. Confirm that `/vllm-workspace/vllm` and `/vllm-workspace/vllm-ascend` exist in the container. Inspect their exact commits, branch or detached state, worktree status, and whether the vLLM repository is shallow.
3. Confirm that both distributions are already installed from the image-provided repositories. Their editable-project locations should resolve to `/vllm-workspace/vllm` and `/vllm-workspace/vllm-ascend`, rather than unrelated copies elsewhere in the environment.
4. Treat those installations as prerequisites. Do not uninstall, reinstall, or rebuild either package unless the user explicitly changes the task to source installation.

## Create the remote workspace

Create the requested remote work directory and link the image repositories into it:

```bash
mkdir -p "$REMOTE_WORKDIR"
cd "$REMOTE_WORKDIR"
ln -s /vllm-workspace/vllm vllm
ln -s /vllm-workspace/vllm-ascend vllm-ascend
```

Before creating each link, inspect any existing path. Preserve existing data and stop for direction if it is not already the intended link. Keep logs, helper scripts, and other operational artifacts outside both linked source repositories.

## Complete the image's vLLM clone

The image's vLLM repository may be a depth-one clone with a detached HEAD. Preserve its original commit while making normal branch operations possible:

1. Record the exact original vLLM HEAD before fetching.
2. If the repository is shallow, fetch full history and tags from `origin`.
3. Ensure the origin fetch refspec includes all branches, then fetch and prune remote branch refs:

   ```bash
   git fetch --unshallow --tags origin  # only when the repository is shallow
   git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
   git fetch --prune origin
   ```

4. Locate the remote branch corresponding to the recorded commit. First inspect branches pointing exactly at it, then branches containing it:

   ```bash
   git branch --remotes --points-at "$ORIGINAL_HEAD"
   git branch --remotes --contains "$ORIGINAL_HEAD"
   ```

   Prefer a remote branch whose tip is exactly that commit. If several branches qualify, use revision context such as the image version instead of guessing. Ask the user when the intended branch remains ambiguous.
5. Attach the worktree to a same-named local branch at the recorded commit and configure its upstream. If the remote branch tip has advanced, create the local branch explicitly at `$ORIGINAL_HEAD` before setting its upstream; do not switch to the newer tip. Fetching history must never silently change the image revision.
6. Verify the final HEAD still equals the recorded commit, the expected branch is shown by `git status`, and the worktree is clean.

Do not change the image's vLLM Ascend revision during this fast bootstrap unless the user explicitly asks. The user may manage that remote revision separately; always observe and record its exact current commit for local synchronization.

If network access fails, report the concrete error and ask for the current proxy setup. Proxy values are task-local and must not be persisted as workflow knowledge or source-repository configuration.

## Bootstrap the local workspace from the remote image state

This initial synchronization is a deliberate exception to the usual local-first direction: the selected image defines the starting commits. Once local clones are aligned, return to local-first editing and synchronize local changes to the remote environment before execution.

1. Inspect `workspace/vllm` and `workspace/vllm-ascend` before cloning. Reuse a clean suitable clone when appropriate. If the requested bootstrap starts from an empty local workspace, clear only the explicitly authorized workspace contents and preserve anything outside that boundary.
2. Under the ignored local `workspace/` directory, clone any missing official repositories:

   ```bash
   git -c core.autocrlf=false clone https://github.com/vllm-project/vllm.git vllm
   git -c core.autocrlf=false clone https://github.com/vllm-project/vllm-ascend.git vllm-ascend
   ```

3. Configure both clones to retain LF line endings. On Windows, disable CRLF conversion at clone time as shown above; changing it only after checkout can make an untouched clone appear broadly modified.
4. Check out the exact vLLM commit observed remotely. When the corresponding remote branch is known, create the local branch at that exact commit and configure its upstream; do not assume the current upstream tip still equals the image commit.
5. Fetch and check out the exact vLLM Ascend commit observed remotely. Preserve detached HEAD locally when that matches the remote state and no branch choice was requested.
6. Verify both local worktrees are clean and that each local commit exactly equals its remote counterpart.

Do not copy the symlink targets from the container into the local workspace and do not install the packages locally. Local clones exist for editing; execution uses the already-installed remote image environment.

## Completion criteria

Report the resolved remote paths and, for both repositories, the local and remote commit plus branch or detached state. The fast setup is complete only when:

- the two remote workspace paths are the intended symlinks;
- both remote editable installations resolve to the image-provided repositories;
- vLLM has full usable history while remaining at the image's original commit;
- local and remote commits match exactly;
- all inspected worktrees are clean; and
- neither source repository contains operational artifacts or temporary workflow edits.
