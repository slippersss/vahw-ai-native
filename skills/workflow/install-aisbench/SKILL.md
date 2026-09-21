---
name: install-aisbench
description: Install the AISBench benchmark suite from source in a remote Ascend environment, including the standard revision choice.
---

# Install AISBench benchmark

> 中文导读：在远程昇腾环境中从源码安装 AISBench benchmark。默认使用用户惯用的 0508 tag，`pip install -v -e .` 即可。

Use this workflow together with the applicable remote-work rules. pip traffic requires the task proxy; treat proxy values as task-local environment data.

## Select the revision

1. Clone into the resolved remote work directory:

   ```bash
   git clone https://github.com/AISBench/benchmark.git benchmark
   ```

   The Gitee mirror `https://gitee.com/aisbench/benchmark.git` serves the same project when GitHub is unreachable.

2. The user's standing preference is the `v3.1-<YYYYMMDD>-master` tag series, defaulting to `v3.1-20260508-master`. List candidates with `git tag -l '*<MMDD>*'`; each date prefix so far has exactly one match.
3. Check out the tag as a detached HEAD and record the exact commit.

## Install

```bash
python -m pip install -v -e .
```

Plain build isolation works; do not add `--no-build-isolation`.

pip normalises `ais-bench-benchmark` and `ais_bench_benchmark` to the same distribution name, so this replaces an existing packaged install rather than coexisting with it.

## Verify

- `import ais_bench` resolves into the cloned source tree, not into site-packages.
- The `ais_bench` console script is on `PATH`. There is no `ais-bench` script.

Store logs, helper scripts, and PID files in the task's operational directory adjacent to the source tree, never inside it.
