---
name: ai-native-meta
description: Apply workspace-wide communication, knowledge-promotion, skill-authoring, workspace-boundary, and commit conventions whenever an AI works in this repository.
---

# AI-native meta rules

> 中文导读：这是整个 AI 原生工作区的通用协作 Skill，不涉及具体业务，并在 AI 参与本仓库工作时生效。目前约定沟通方式、业务工作区边界、持续沉淀、Skill 编写方式和 AI 提交身份。

These are workspace-level rules. Keep them separate from business knowledge, project conventions, and task-specific instructions.

## Communication

- Default to concise, natural conversation.
- Lead with the point. If one sentence is enough, do not turn it into several paragraphs.
- Avoid AI-style mini-essays, unnecessary summaries, excessive headings, and low-information repetition.
- Expand only when the user asks for detail or when missing detail would materially affect a decision.
- Treat a specific directive as the scope of the work. Carry out exactly what was asked and report the result; do not widen it into an open-ended investigation or add adjacent steps the user did not request. If a discovery looks important, state it in one or two lines and let the user decide whether to act on it.

## Workspace boundary

- Treat `workspace/` as the working area for business projects and task artifacts.
- Keep reusable meta rules, skills, and workflows outside `workspace/` and under version control in this repository.
- Keep operational artifacts separate from business source trees. Store helper scripts, logs, PID files, status files, and temporary files in `workspace/` locally or in a dedicated operator-owned directory adjacent to remote source trees; place them inside a source repository only when they are intentional project deliverables.

## Remote network preflight

- Default to the `root` SSH user when connecting to a remote machine unless the user explicitly specifies another account or the applicable SSH host configuration selects one. Do not infer the SSH user from a remote working-directory path.
- Whenever a task connects to a remote machine or container, check network access from the actual execution environment before cloning repositories, downloading packages, or starting other network-dependent work. Host connectivity does not prove container connectivity; check each environment that will access the network.
- Remote environments commonly start without a working proxy. If required endpoints are unreachable and no usable proxy is configured, stop the network-dependent step and ask the user for the current task's proxy immediately.
- Treat proxy values as task-local environment data. Do not persist them in repositories, reusable skills, Git configuration, or other lasting configuration unless the user explicitly requests it.
- Do not silently replace the intended remote download or installation workflow with local repository or artifact migration merely because the remote network is unavailable. Use an alternative transfer path only when the user requests or approves it.

## Text files

- Use LF line endings for every text file, including generated files and configuration written by tools. Do not introduce CRLF based on the host platform default.

## Continuous learning

- During real work, notice practices, lessons, and recurring patterns that may be worth preserving.
- The user authorizes autonomous creation and refinement of repository skills from validated practice. Make focused improvements when they will improve future work, and briefly report what changed at a natural checkpoint.
- Preserve evidence boundaries: an unverified hypothesis or a case-specific constant is not a reusable rule. Prefer extending the relevant existing skill over adding overlapping skills; revise or remove guidance when later evidence contradicts it.
- This authorization covers local skill maintenance, not additional remote experiments, deployments, or Git commits and pushes; those retain their task-specific authorization requirements.

## Skill authoring

- Treat the repository's `skills/` tree as the platform-independent source of truth. Agent-specific installed copies or generated adapters are derived artifacts.
- Give every concrete skill a `SKILL.md` with a concise `name`, a discriminating `description`, and only the instructions that materially change agent behavior.
- Keep executable instructions in clear English and add a short Chinese introduction for the user; do not duplicate the full text bilingually.
- Start with one self-contained file. Add scripts, references, assets, or agent adapters only when real usage demonstrates a need.
- Derive skills from confirmed reusable experience. Keep one-off project facts and task notes out of meta skills.
- Preserve the user's intent and authorization boundaries. A skill guides work but does not grant additional permission.

## AI-authored commits

- Keep each commit focused on one coherent change.
- Use an English Conventional Commit subject: `<type>(<optional-scope>): <summary>`.
- Prefer `feat`, `fix`, `test`, `docs`, `refactor`, or `chore`; keep the subject concise and imperative.
- Default to a subject-only message. These repositories are usually simple,
  so the subject should normally describe the change completely.
- Add a body only when the subject cannot explain a necessary reason or a
  non-obvious tradeoff. Never use the body to restate the subject or diff.
- Use this stable AI identity; do not include the model, provider, or agent name:

  `ai-native <ai-native@no-reply.email>`

- Treat the AI as the primary author of commits it creates.
- Add this trailer to every AI-created commit:

  `Signed-off-by: ai-native <ai-native@no-reply.email>`

- Add the user as co-author:

  `Co-authored-by: slippersss <slippersss@126.com>`

- Separate the trailer block from the message body with exactly one blank line.
- Keep all trailer lines contiguous. There must be exactly zero blank lines
  between `Signed-off-by` and `Co-authored-by`, or between any other trailers.
- Order the standard trailers with `Signed-off-by` first and
  `Co-authored-by` immediately after it.
- Apply the AI identity per commit; do not overwrite the user's persistent Git configuration.
- `Signed-off-by` is intentional here: within this workspace it records the AI-native authorship convention and carries its normal DCO attestation implications.
