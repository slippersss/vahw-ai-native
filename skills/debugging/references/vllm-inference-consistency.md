# vLLM inference consistency debugging

> 中文导读：用于排查 vLLM、vLLM Ascend 或其他推理部署之间“请求成功但结果不同”的问题。核心原则是先证明模型收到的最终 token 和响应解析语义一致，再讨论量化、算子与硬件差异。

## Establish a comparable experiment

Treat equality of dataset rows and client JSON as necessary but insufficient. Record an experiment manifest for every target containing:

- source revision, model and tokenizer identity, model config, quantization, dtype, and KV-cache dtype;
- launch command and effective server configuration after parsing;
- request body after client defaults are applied;
- chat template, default template kwargs, reasoning and tool parsers, and relevant environment variables;
- dataset content hash, selected row IDs, order, concurrency, and retry policy.

Keep the same request IDs across targets. Under concurrency, completion order is not request order: join records by a stable request ID or dataset index before computing per-request deltas, and verify that IDs are unique and the joined sets are equal. Save the full request and raw response per request, including `content`, `reasoning_content`, finish reason, usage, errors, and timing. Do not compare aggregate metrics until both sides have the same successful request set.

## Require a preflight input-equivalence check

Before a multi-request benchmark, run one shared sample through each complete serving frontend and capture, in priority order:

1. the final prompt token IDs presented to the engine;
2. a stable hash and length of those IDs;
3. the rendered prompt when it can be retained safely;
4. the effective chat-template kwargs and parser mode;
5. the leading and trailing token IDs for localized comparison.

The primary invariant is:

```text
prompt_token_ids_A == prompt_token_ids_B
```

If it fails, stop the performance or acceptance comparison and find the earliest preprocessing divergence. Do not attribute downstream differences to quantization, kernels, or hardware while model inputs differ.

When prompts are sensitive and cannot be exported, compare length, hash, and an operator-reviewed local diff rather than copying their contents elsewhere.

## Localize the first divergence by layer

Work from semantics toward numerics:

1. **Dataset:** exact row content, order, truncation, and selection.
2. **Request:** sampling values, seed, limits, stop conditions, tools, and reasoning controls.
3. **Frontend:** applied defaults, chat template, system text, special tokens, and tokenization.
4. **Parser:** reasoning/content splitting, tool parsing, streaming assembly, truncation, and usage accounting.
5. **Engine:** scheduler, prefix cache, speculative decoding, KV-cache policy, and batching.
6. **Numerics:** checkpoint, quantization, dtype, kernels, distributed topology, and device behavior.

Find the earliest layer with an observable mismatch. Later mismatches are consequences until shown otherwise.

Compare source-level defaults as part of the public behavior. A missing request field is not equivalent across implementations unless both resolve it identically. For behavior-changing options such as thinking, sampling, template selection, or parser mode, prefer explicit values in a cross-backend test.

After identifying a candidate default or branch, perform a controlled intervention: explicitly set only that behavior on both targets and repeat the one-sample preflight. Treat disappearance of the prompt-token or parser-state mismatch as causal confirmation; if it remains, continue looking for an earlier divergence.

## Use mismatch signatures as evidence

- A constant prompt-token offset across unrelated samples strongly indicates fixed template text, a system prompt, tools, or special tokens.
- A proportional or length-dependent prompt difference suggests truncation, normalization, or tokenizer behavior.
- Equal input IDs with an immediate generation divergence moves suspicion toward checkpoint identity, logits processing, quantization, kernels, or nondeterminism.
- Equal generated token IDs but different API fields indicates response parsing or serialization.
- Empty `content` with nonzero completion usage, especially at `max_tokens`, suggests hidden reasoning, an unclosed reasoning span, tool parsing, or parser state—not an empty generation.
- Similar speculative acceptance rates do not prove semantic equivalence; different prompts can still yield similar aggregate acceptance.

A suggestive signature narrows the next probe but is not root-cause proof by itself.

## Escalate to numerical analysis only after equivalence

Once prompt token IDs and response semantics match, compare progressively:

- greedy decoding with explicit sampling parameters and a single request;
- the first differing generated token position;
- target and draft token IDs for speculative decoding;
- per-position acceptance counts and rates, plus expected accepted length computed as `1 + sum(per-position acceptance probabilities)` when that is the agreed metric;
- logits or top candidates near the first divergence when the serving stack can expose them;
- checkpoint tensor metadata, quantization scheme and granularity, activation dtype, KV-cache dtype, kernel/backend, and parallel topology.

`temperature=0` reduces sampling variability but does not guarantee cross-device bitwise determinism. Small numeric differences can change an argmax when candidates are close and then cause autoregressive divergence. Describe such effects as numerical sensitivity unless the first differing decision and its inputs have been observed.

## Scale only after the gate passes

Use one request to establish input and parser equivalence, a small fixed set to characterize the divergence, and the full dataset only for stable statistics. Preserve every run's manifest and per-request artifacts so results remain attributable after services or scripts change.
