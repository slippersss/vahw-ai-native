---
name: vllm-ascend-pre-pr
description: Check or fix vLLM Ascend formatting, lint, and pre-PR quality when the user asks to "检查格式", check formatting, format code, run lint, pre-commit, or prepare a PR, without unnecessary GitHub hook bootstrap.
---

# vLLM Ascend pre-PR checks

> 中文导读：用于提交 vLLM Ascend PR 前执行仓库对应的检查。新容器默认跳过 pre-commit 从 GitHub 初始化全部 hook 的阶段，按改动类型直接运行检查；已有缓存时可以运行 pre-commit，但不能把部分检查通过说成完整通过。

Use the checkout's `.pre-commit-config.yaml` as the source of truth. Inspect it before selecting hooks because hook IDs and versions can change.

## Format-check requests

When the user asks to check formatting, act on the changed files rather than merely reporting the configured line length:

1. Read the formatter version and configuration from the checkout.
2. Run the applicable formatter and linter with fixes enabled when the request permits formatting changes.
3. Inspect the diff manually for needless wrapping or indentation in newly added code. Formatter acceptance alone does not prove that short calls and comments are laid out readably; consolidate them when they fit the configured line length, then rerun the formatter.
4. Finish with non-mutating formatter and lint checks, and report whether tools changed any files.

For ordinary Python changes in this repository, this normally means Ruff check and Ruff format on the changed Python files. Add spelling, repository-local, and tests according to the request and affected files.

## Install pre-commit

Prefer the active Python interpreter and the Huawei internal PyPI mirror in remote Ascend containers:

```bash
python -m pip install \
  --index-url http://mirrors.tools.huawei.com/pypi/simple \
  --trusted-host mirrors.tools.huawei.com \
  pre-commit
python -m pre_commit --version
```

Use `python -m pre_commit` rather than assuming the console script is on `PATH`. Do not persist task-specific proxy addresses in the repository or skill; obtain the current proxy when GitHub-hosted hook environments cannot be downloaded.

## Avoid first-run GitHub bootstrap

On its first run, pre-commit clones hook repositories such as Ruff, codespell, typos, and actionlint from GitHub and creates isolated environments. In a fresh remote container, do not trigger this bootstrap merely to check ordinary Python changes. It is slow and commonly fails behind the corporate TLS proxy.

If the required pre-commit hook environments are already cached, run the configured hooks against the changed files:

```bash
python -m pre_commit run --files <changed-files...>
```

If they are not cached, install the relevant Python tools from the internal mirror and invoke them directly. Read their pinned versions and arguments from `.pre-commit-config.yaml`; for the currently configured Python checks, the shape is:

```bash
python -m pip install \
  --index-url http://mirrors.tools.huawei.com/pypi/simple \
  --trusted-host mirrors.tools.huawei.com \
  'ruff==<configured-version>' 'codespell==<configured-version>'
python -m ruff check --fix <python-files...>
python -m ruff format <python-files...>
python -m codespell --toml pyproject.toml <changed-files...>
```

Run `typos` directly only when its binary is already available through the environment's approved package source. Do not initiate GitHub hook bootstrap solely to obtain it. Report exactly which checks ran and which were unavailable.

Use repository-local hook scripts directly when they apply and their dependencies are present. Use `--all-files` only when the user requests a repository-wide check or the change warrants it. Formatters and fixers may modify files; inspect the resulting diff, rerun the checks, and run the relevant tests.

For Python-only changes, the minimum directly relevant external hooks are:

```bash
python -m pre_commit run ruff-check --files <python-files...>
python -m pre_commit run ruff-format --files <python-files...>
python -m pre_commit run codespell --files <python-files...>
python -m pre_commit run typos --files <python-files...>
```

This targeted list applies when the hook environments are already cached. It is not a claim that all configured local hooks passed.

## Handle actionlint certificate failures

`actionlint` validates `.github/workflows/*.yml` and `.yaml`. A corporate HTTPS proxy may cause its first-time environment installation to fail with `CERTIFICATE_VERIFY_FAILED` before any source check runs.

Skip `actionlint` only when all of the following are true:

- No changed file is under `.github/workflows/`.
- The failure is environment installation or certificate verification, not an actionlint finding.
- All hooks relevant to the changed files are still run and their results are reported accurately.

In that case, either omit actionlint from the targeted checks or, when the other hook environments are already cached, retry the aggregate check with:

```bash
SKIP=actionlint python -m pre_commit run --files <changed-files...>
```

If workflow files changed, do not ignore actionlint. Fix the certificate/network environment or run actionlint in another equivalent environment. Never describe a targeted-hook pass as a complete pre-commit pass when another applicable hook did not run.
