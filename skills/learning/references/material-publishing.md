# Consolidating and publishing learning material

Read this reference when a learning session reaches a useful checkpoint and the user asks to preserve or publish the result.

## Build the document from the validated path

- Write for later study, not as a chat transcript. Remove conversational repetition while preserving corrections that prevent likely misunderstandings.
- Begin with the scope, current progress, learning-level outline, and any source-code or documentation revisions used.
- Organize the body in the final conceptual order. Separate the main line from prerequisite and side-topic sections.
- For each section, include the minimum explanation needed to interpret its diagram, followed by the key conclusion and any important semantic boundary.
- Distinguish general concepts from repository- or version-specific observations.
- End with unfinished levels and the exact next learning entry point.

## Preserve diagrams and source artifacts

- Keep the original session artifact directory unchanged.
- Copy validated assets into the material repository with their descriptive ordered filenames.
- Embed every retained diagram from the Markdown using relative paths. Do not silently omit a source artifact; either include it or state why it is excluded.
- When a diagram was corrected during learning, publish the corrected version and describe the resolved distinction in the surrounding text when it remains pedagogically important.

## Choose a minimal archive layout

Respect an existing repository structure and its instructions. For an empty content-only repository, prefer:

```text
README.md
docs/<topic>/README.md
docs/<topic>/assets/*
```

- Use the root README only as an index.
- Keep the topic document and its assets together.
- Do not copy working-repository skills, agent instructions, cloned source repositories, or temporary artifacts into the archive.

## Verify before publication

- Compare source and copied asset counts and hashes.
- Parse every SVG as XML.
- Resolve every local Markdown image link and report missing targets.
- Check UTF-8 text, LF line endings, and Git whitespace errors.
- Inspect the target repository status and include only the intended material in the commit.

## Commit and push safely

- Publishing permission does not follow automatically from permission to write local material. Commit or push only when the user asks for it.
- Before cloning, fetching, pulling, or pushing, follow the workspace network preflight rules.
- If the archive already contains work, fetch and integrate remote changes before committing; preserve unrelated local changes.
- Use the workspace commit convention and per-commit AI identity without changing the user's persistent Git identity.
- After pushing, verify the branch tracks the expected remote, the local and remote tips match, and the working tree is clean.
