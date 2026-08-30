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

## Workspace boundary

- Treat `workspace/` as the working area for business projects and task artifacts.
- Keep reusable meta rules, skills, and workflows outside `workspace/` and under version control in this repository.
- Keep operational artifacts separate from business source trees. Store helper scripts, logs, PID files, status files, and temporary files in `workspace/` locally or in a dedicated operator-owned directory adjacent to remote source trees; place them inside a source repository only when they are intentional project deliverables.

## Text files

- Use LF line endings for every text file, including generated files and configuration written by tools. Do not introduce CRLF based on the host platform default.

## Continuous learning

- During real work, notice practices, lessons, and recurring patterns that may be worth preserving.
- Proactively remind the user at a natural checkpoint when something appears reusable.
- Do not promote a one-off observation into a lasting rule or skill without the user's agreement.

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
- Add a body only when the reason or a non-obvious tradeoff needs explanation.
- Use this stable AI identity; do not include the model, provider, or agent name:

  `ai-native <ai-native@no-reply.email>`

- Treat the AI as the primary author of commits it creates.
- Add this trailer to every AI-created commit:

  `Signed-off-by: ai-native <ai-native@no-reply.email>`

- Add the user as co-author:

  `Co-authored-by: slippersss <slippersss@126.com>`

- Separate trailers from the message body with one blank line.
- Apply the AI identity per commit; do not overwrite the user's persistent Git configuration.
- `Signed-off-by` is intentional here: within this workspace it records the AI-native authorship convention and carries its normal DCO attestation implications.
