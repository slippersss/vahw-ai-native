---
name: remote-work
description: Coordinate local-first development on one or more SSH-accessible remote machines, including pre-execution code synchronization and durable monitoring of short or long remote jobs.
---

# Remote work

> 中文导读：用于一台或多台远程机器上的开发与执行。本地代码是事实源；远程执行前同步并验证；长任务脱离连接运行，并支持重新查询、看日志和停止。当前只定义最小工作流，不绑定特定 Agent 或第三方同步组件。

## Principles

- Treat the local project under `workspace/` as the source of truth.
- Address every remote machine explicitly. Never assume that state, code, or results are shared between machines.
- Start with standard SSH, Git, and remote shell capabilities. Add a third-party component only when a demonstrated need justifies it.

## Minimal workflow

1. Resolve the intended target machine or target set and the working directory or container on each target.
2. Before remote execution, synchronize the intended local working-tree state, including relevant uncommitted changes.
3. Verify that each target represents that state before running commands. Do not report remote results against unverified code.
4. Run short commands directly. Run long commands as durable remote jobs that survive a dropped local connection.
5. For every long job, retain a job identifier, target, status, logs, exit result, and artifact location. Support status checks, log inspection, and safe cancellation.
6. Retrieve the required results locally and report partial failures per target when multiple machines are involved.

## Boundaries

- Synchronization is execution-triggered by default; continuous background synchronization is not required.
- Do not store SSH private keys, passwords, tokens, or machine-specific secrets in the repository.
- Do not build session orchestration, distributed scheduling, or conflict resolution until real work demonstrates the need.
