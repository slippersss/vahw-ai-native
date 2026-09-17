---
name: learning
description: Guide an interactive technical learning session when the user wants to build understanding gradually through small explanations, diagrams, code reading, and follow-up questions.
---

# Incremental technical learning

> 中文导读：用于循序渐进的技术学习会话。每次只推进一个可消化的层级，用图和代码建立可检查的心智模型；用户确认或追问后再继续。

Run the session as a dialogue, not a compressed tutorial. Optimize for a mental model the learner can inspect and correct one piece at a time.

## Control the depth

- Organize a broad subject into explicit levels, moving from system role, to component behavior, to software structure, and finally implementation details.
- Explain only the next useful concept. Do not front-load later levels or surrounding knowledge merely because it will eventually matter.
- End each response at a natural checkpoint. Let the user's confirmation or question determine the next step.
- Say clearly when a level is complete, whether the current material is a side topic, and what the next level would cover.
- When the learner reveals a missing prerequisite, pause the main line, teach the minimum prerequisite in a separately named side line, then return to the exact point where the main line stopped.
- Treat repeated confusion as evidence that the explanation or abstraction is wrong, not that the learner needs the same wording again.

## Keep the conceptual structure honest

- Separate these categories explicitly:
  - the normal mechanism or correctness path;
  - a general optimization that can apply independently;
  - a performance pathology or failure mode;
  - a mitigation for that pathology.
- Do not place independent techniques inside a causal chain merely because they interact in practice. State whether the relationship is prerequisite, cause, consequence, mitigation, or only coexistence.
- Before introducing a new page or figure, say how it connects to the current main line. If it belongs to another branch, finish or pause the current branch explicitly.
- Periodically summarize the level structure when several pages have accumulated, and reorder the artifacts if the teaching order has become misleading.

## Make diagrams semantically precise

- Give every substantive level a focused diagram when structure, layout, ownership, timing, or data movement matters. Prefer repository-native SVG for durable learning artifacts; use sequence-style SVGs when following code execution.
- Number main-line figures continuously in presentation order. Give prerequisite and side-topic figures a separate filename/title series.
- Keep the represented object consistent across related examples. Do not silently switch among a scalar, vector, token, request, expert, rank, collective call, or time interval.
- Label what repeated shapes mean: operation count, payload volume, tensor partitions, chunks within one operation, or separate participants.
- Use color, lanes, arrows, and spatial grouping consistently across adjacent figures. Preserve the same abstraction unless the transition itself is being taught.
- If a learner derives the wrong interpretation from a diagram, revise the artifact rather than relying only on corrective prose.
- For distributed collective and chunking diagrams, read [references/distributed-communication.md](references/distributed-communication.md).

## Move from concepts to code

- Establish the concept and input/output contract before opening implementation details.
- When code reading begins, trace one high-level call path first. Show callers, callees, ordering, and important data passed between them; postpone branches and backend-specific kernels.
- Distinguish mathematical semantics, shared software contracts, backend policy, and hardware-specific kernels.
- Use the learner's target repository as the main implementation path. Use upstream or alternate backends as comparison points, not as a second competing main line.
- Link claims to exact local files and lines when discussing repository behavior. Mark general knowledge separately from version-specific evidence.

## Maintain learning artifacts

- Store generated diagrams and session artifacts in the repository's designated workspace area; keep reusable teaching rules in this skill.
- Use descriptive, ordered filenames. When the teaching order changes, rename files and update figure titles together.
- Validate generated SVG as XML after edits.
- Preserve useful domain knowledge only after it has been checked against code or authoritative sources. Put domain-specific material in a separate skill or reference rather than embedding it in this general learning workflow.
