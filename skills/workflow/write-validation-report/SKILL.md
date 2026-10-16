---
name: write-validation-report
description: Write or revise self-contained technical reports for testing, debugging, and feature development, with traceable evidence, consistent figures, portable Markdown, and complete reproduction appendices. Use for reporting existing work, not for running new experiments or publishing automatically.
---

# Write a validation report

> 中文导读：用于测试、调试和特性开发，将已有工作整理成第三方能独立阅读、核对和复现的报告。正文解释问题、方法、证据与结论；完整数据、环境、代码或脚本和操作步骤放附录。默认普通 Markdown 配相对路径附件，不依赖聊天历史或操作者工作目录。

## Primary acceptance criterion: reproduce from the report

Self-contained means **a later reader can reconstruct and verify the reported experiment, failure or feature behavior using the report and its supplied attachments, without asking the original operator, reading the chat, or accessing the original workspace**. Readability alone is insufficient. Put the complete procedure in the report; attachments supply actual code/scripts/data rather than instructions hidden elsewhere. If the user requests one Markdown file, inline the necessary scripts/configuration in its appendices where practical, and identify any essential external data explicitly.

Review reproduction as a fresh reader: obtain the stated prerequisites and exact source/change → configure the environment → prepare inputs → perform the reported action → capture evidence → compare with expected behavior. For serving benchmarks this includes service launch, readiness/cache checks, load generation and metric collection. For debugging, specify failing and fixed states and the expected failure/success signatures; for features, specify setup, use, expected outputs and verification. Include only relevant stages. Every transition must have concrete instructions, an included implementation, or an explicitly documented prerequisite. Do not leave unstated defaults, missing helpers, ambiguous working directories, data sampling, or manual operator knowledge between steps.

Distinguish reproducible procedure from guaranteed numerical repeatability. Document missing historical prerequisites or artifacts as reproduction gaps, not as a completed self-contained reproduction package. Do not invent them to satisfy the format; state which results can be reconstructed and which require additional evidence.

## Establish the scope and evidence

- Adapt the evidence to the task. Testing reports need workload, comparison protocol and measurements; debugging reports need the reproducer, observed failure, causal evidence, fix/workaround and regression validation; feature reports need requirements, resulting behavior, design/interface changes and verification. Reproduce the relevant failure, behavior or measurement rather than forcing every report into a benchmark format. Include exact code revisions and the patch or legitimate source acquisition path when the result depends on a change.
- Resolve the audience, question, evidence set and requested output location. Use existing validated artifacts; writing a report does not authorize new experiments, deployments, publication or Git operations.
- Build a small internal evidence inventory before drafting: trial ID, actual version/configuration, dataset identity, measured values, raw artifact and inclusion/exclusion reason. Keep this operator inventory out of the reader-facing narrative unless useful.
- Separate code/configuration cohorts, repeated executions, diagnostic runs, warmup and failed trials. A copied export or subset is not another experiment. Do not merge different versions or overwrite earlier results merely to produce one smooth curve.
- Inspect sources supporting the main claims, not only an earlier summary. Distinguish native measurements from recalculations, interpolation and hypotheses. Mark unavailable facts explicitly; never fill missing measurements from adjacent runs or recollection.
- For inference performance reports, use the metric definitions and collection guidance in the available `benchmark-vllm-ascend` skill when relevant. This report skill does not redefine those metrics or require that particular benchmark stack.

## Write for a reader outside the session

- State the concrete question and result early. Define necessary abbreviations, baselines, units and experiment labels at first use.
- Write the final logical explanation, not the chronology of the conversation. Replace “the previous run”, “our directory” and “as discussed” with explicit experiment identities and facts.
- A reader must understand the report without opening another report, a chat, a private dashboard or an operator's local paths. Put essential definitions, relevant numbers and comparison conditions directly in the document. References can support attribution without replacing the explanation.
- Make the report portable, not environment-free: retain hardware/software/model identity and settings that affect the result. Replace personal usernames, private addresses, credentials and operator paths with defined deployment variables. Do not remove necessary technical provenance in the name of anonymization.
- Use simple descriptive names such as “验证报告”; do not add “公开技术报告”, promotional titles or unrequested branding.

## Work efficiently without repeated rewrites

1. Inspect the requested evidence set and the existing report style first. Choose canonical evidence records and stable case/trial IDs as the source for prose, tables and figures. For quantitative reports, use one canonical data table and record field mappings instead of transcribing figures by hand. Do not manufacture performance tables for a qualitative debugging or feature report.
2. Resolve reproduction gaps before polishing prose: exact inputs, required scripts/helpers, environment identity, deployment variables and metric collection. Build the minimal appendix and attachment set first; do not discover at delivery that a named script was never included.
3. Draft the question/method/result/conclusion outline around the actual evidence, then generate key tables and figures. Add full-detail appendices from the same records. Reuse existing validated figures or plotting style when compatible instead of redesigning every revision.
4. Perform one integrated numeric/dependency/privacy/rendering pass and fix the actual artifacts. Recheck affected outputs after edits; do not endlessly rerun unchanged checks or create extra wrappers/reports to demonstrate effort.
5. Deliver a compact status: location, contents, verification actually performed and unresolved reproduction gaps. For a later narrow correction, change only the requested scope and check its dependencies; do not rewrite or restyle unrelated reports.

## Organize the document

Use a paper-like structure scaled to the task, without imposing academic ceremony on a small report:

|Section|Reader question it answers|
|---|---|
|Summary|What was tested, what was observed, and within what scope?|
|Introduction|Why this comparison, and what decision does it support?|
|Method|What systems, workload, variables, baseline and measurement rules were used?|
|Results|What do the measured tables and figures show?|
|Discussion and limits|Which explanations are supported, what confounds remain, and what cannot be concluded?|
|Conclusion|Under what conditions does the finding apply, and what practical guidance follows?|
|Appendices|Complete data/definitions, environment/configuration, scripts and reproduction steps|

For debugging, adapt Method/Results to reproduction, investigation, root-cause evidence, change and regression verification; label unconfirmed root causes as hypotheses. For feature development, use requirements, design/implementation, behavior examples and validation. Diagrams may show call paths or interfaces instead of numeric trends. Keep the common evidence/reproduction standard without forcing benchmark-specific sections or metrics.

Keep settings necessary to interpret a result in Method; place exhaustive flags, long scripts and raw-data detail in appendices. Do not force the reader through deployment commands before explaining the experiment. For a short report, combine sections when their distinct purposes remain clear.

## Preserve data and comparison boundaries

- Include numerical tables as well as trend figures when they answer different needs. A screenshot of a table is not a trend visualization. Put compact key comparisons in Results and full trial tables or accompanying machine-readable data in appendices.
- Identify each row by stable trial/cohort labels and include the parameters that can change interpretation. Keep independent runs visible; disclose averaging, selection, exclusions and execution/restart order.
- State the exact baseline and formula for every improvement percentage. Compute with unrounded inputs; round only for display and keep units/precision consistent. Retain negative and inconclusive observations rather than selecting only favorable points.
- Explain statistical weights, denominators, windows and percentile direction where non-obvious. Do not rename a proxy metric as the quantity it approximates or silently replace the agreed primary statistic with a favorable diagnostic.
- For latency matching, show actual latency, residual difference, concurrency and sample count alongside throughput. Target tolerance does not imply equal measured latency. Distinguish selected matching points from all search trials.
- For inference cases, preserve requested TPOT, ITL, output throughput, running distributions, ITL/TPOT and acceptance/per-position data when collected. Put wide secondary fields in companion tables keyed by the same trial ID. Missing data should remain visibly unavailable.
- “Complete” means evidence necessary to inspect the findings is available, not that every raw log must be pasted into the prose. Retain full-resolution machine-readable data and original private archives; explain exclusions without flooding the report with unrelated history.

## Make figures informative and consistent

- Choose axes that answer the question. For performance studies, concurrency–throughput and measured latency–throughput often provide complementary views; occupancy timelines help interpret whether load was sustained.
- Keep method colors, fonts, units, line meanings and legend ordering consistent across related reports. Distinguish independent runs, scans, matching points and estimates with documented markers/line styles.
- Connect measured points only within the intended series. Do not join unrelated trials or imply a monotone interpolation when the actual x-values are non-monotone. Label estimates separately from measurements.
- Choose scales proportionate to the claim. Do not exaggerate small differences with unexplained cropped axes or compress away the effect of interest; use a clearly labeled detail panel when needed. Comparable panels should share scales where appropriate.
- Give each figure a caption stating the load/cohort, axis meaning, symbol meanings and principal observation. Keep numeric tables available so the reader does not need to estimate values from pixels.
- Render/view generated figures and inspect labels, overlap, clipping, legend ambiguity and consistency with tables. Prefer standard plotting tools for scientific/performance figures, not generative images.

## Give bounded, usable conclusions

- Separate observed result, supported interpretation and unresolved cause. A performance difference alone does not prove its kernel, scheduling, proxy or hardware cause.
- Treat the experiment as an illustrative case when deriving qualitative usage guidance. Explain the relevant resource/load tradeoff; do not promote one machine's concurrency, worker count, latency threshold or profile into a universal enabling rule.
- Explain alternative variables that materially affect interpretation, such as dataset/sample count, cache state, graph modes, versions, instrumentation or service restarts. Keep limitations near affected claims, not only in a distant disclaimer.
- Do not equate single measurements with statistical significance, separately executed runs with statistical independence, or an unexplained difference with a confirmed regression. Preserve uncertainty without repeating boilerplate in every paragraph.
- State both favorable and unfavorable operating conditions when supported. A conclusion should help someone decide whether the finding applies, not simply repeat the largest gain.

## Package reproduction simply

Default to one report document and its real dependencies, not HTML downloads, embedded base64 attachments or a framework of launchers. Respect a requested single-file format: include scripts inline in appendices when practical and state honestly if exact input data still requires an attachment.

```text
report/
├── README.md
├── images/       # figures embedded with relative paths
├── data/         # frozen inputs and complete numeric tables when needed
└── scripts/      # actual launch/test/analysis scripts referenced by the report
```

- Create only directories/files that are used. For multiple reports, an outer README is a short index; each report remains independently understandable. Avoid proliferating overlapping reports for every intermediate run.
- Use ordinary Markdown, fenced code and relative image/file links within the deliverable. Do not rely on renderer-specific raw HTML or data-URI downloads. Do not add checksum/manifest machinery unless requested or needed for a concrete integrity requirement.
- Put reproducibility in an appendix with explicit prerequisites, environment identity, named deployment variables, working directory, data construction/reuse rules, service launch, health/warmup, test commands, metric collection and expected output locations. Keep the smallest useful sequence, such as P script, D script and numbered client steps.
- Include exact scripts/configuration discussed in the report, with their imports/helper files and frozen data where distributable. Merely naming a file from the operator workspace is not providing it. If redistribution is restricted, state the prerequisite and a legitimate acquisition procedure instead of pretending the bundle is complete.
- Define the client, service, tokenizer and dataset paths separately. Commands must agree with the included filenames and working-directory assumptions. Clearly mark variables/placeholders that need deployment-specific values.
- Give each reproduction stage a command, required inputs, expected output/success check and next step. Specify restart/reuse behavior and cache/counter boundaries when they affect comparisons. A statement such as “collect metrics” is incomplete when those metrics support a headline result: include the collector/commands, endpoints/rank mapping, time window and reduction method.
- Include configuration differences per compared method, including graph lists, flags and weights, rather than instructing the reader to “change it as before”. Explain input data sampling, repetition/order and post-template lengths; a seed alone is not the fixed workload.
- Include enough analysis instructions to reproduce reported tables/figures from saved outputs. Separate supplied precomputed results from files a reader's test will generate, and explain how to locate and map the latter. Never require access to a hard-coded operator archive to run the supplied analysis.
- Record actual tool/source provenance and modifications. Link authoritative upstream sources for attribution; a link to today's main branch is not an exact historical version or a substitute for the tested files.
- When merging reports, retain independent experiment identities and all relevant observations. Preserve originals privately before removing obsolete deliverables, and verify no retained links depend on them. Change only the requested report(s) or file when scope is narrow.

## Review the deliverable, not just the prose

Before handing over, perform these checks proportionately to the report:

1. **Evidence:** map headline numbers and conclusions to raw artifacts; verify formulas, units, denominators, exclusions, trial counts and same-baseline comparisons. Repeated assertions of review are not additional evidence.
2. **Consistency:** compare abstract, conclusion, tables, figures and scripts. Independent cohorts must not silently change names, settings, aggregation or plotted values.
3. **Portability:** resolve every relative reference, including script imports/config/data dependencies. Check a copied directory or simulate its working-directory assumptions when meaningful; distinguish static validation from an actual service reproduction.
4. **Privacy and provenance:** check prose, commands, CSV/JSON, figure labels/metadata and attachments for private operator details while preserving necessary configuration identity. Public safety does not follow from replacing addresses in prose alone.
5. **Rendering:** inspect Markdown table column counts and escaping, blank lines, fenced blocks, image visibility and figure appearance. Do not claim a visual preview was inspected if only text was parsed. Use UTF-8/LF text files.
6. **Delivery:** report the final directory and what is included, plus material reproduction limits. Do not claim historical absolute performance is fully reproducible when installation artifacts or hardware identity are missing. Do not commit, push or publish without the user's authorization for that action.

Use a fresh-directory rehearsal when practical: copy only the deliverable, ignore the original working directory, and follow the appendix literally. Validate local data generation and analysis with safe offline inputs, and check service/client scripts without launching them unless execution is authorized. If a required file, variable, collector, dependency or step can only be recovered from the original workspace, the report fails the reproduction criterion until supplied or explicitly identified as a gap. Report the rehearsal level accurately: static review, offline execution and end-to-end reproduction are different levels of evidence.
