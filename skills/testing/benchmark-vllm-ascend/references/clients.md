# Client execution recipes

> 中文导读：三个入口分别配置、执行和留存结果。先检查目标环境版本及 help；示例不是跨版本保证，也不替代正式实验前的短请求检查。

## Shared preparation

- Resolve the installed executable/import path, revision, endpoint, served model name, tokenizer, frozen prompts, output limit, concurrency C, request count N, request rate, streaming and sampling settings.
- Read the installed `ais_bench --help`, `vllm bench serve --help`, or `python3 aisbench_test.py --help` plus the matching source/README. Pin versions; do not upgrade a prepared environment merely to obtain a flag.
- Use a short request to validate endpoint/model, generation settings and saved-result schema before a long run, within the authorized testing scope. Keep that request outside formal counter windows.
- Preserve raw summaries and request records. Retain retry/failure behavior and warmup/probe behavior: clients can issue requests beyond N or count retries differently.
- Request-rate conventions differ: the historical wrapper used 0 for unrestricted dispatch, while vLLM bench uses `inf`. Verify native AISBench semantics for its version rather than copying either value blindly.

## 1. Native AISBench

Source: [AISBench/benchmark](https://github.com/AISBench/benchmark). See the official [performance guide](https://github.com/AISBench/benchmark/blob/master/docs/source_en/base_tutorials/scenes_intro/performance_benchmark.md) and [custom dataset guide](https://github.com/AISBench/benchmark/blob/master/docs/source_en/advanced_tutorials/custom_dataset.md), preferably at the installed revision.

1. Locate installed model and dataset configuration files; use the version's config listing/search facilities or inspect the imported package tree. The executable is `ais_bench`, not `ais-bench`.
2. Create task-owned copies of the model and dataset configs, or use a supported combined configuration file. Avoid editing shared package defaults. Resolve model class, endpoint URL/host/port, served model, tokenizer path, API key, concurrency (`batch_size` in the historical service config), request rate, `max_out_len`, retry and generation kwargs. Streaming chat used `vllm_api_stream_chat` in this campaign.
3. Point the dataset config/loader at the frozen JSONL, map the actual `question`/`answer` columns and prompt template, and set the exact sample range/order. Do not accidentally use the demo's few-shot prompt or full dataset when N was requested. Native AISBench is config-driven: the wrapper's `--input_len`, `--data_num`, etc. are not automatically native flags.
4. Run performance mode with the resolved config aliases; these aliases must already exist in that installation:

```bash
ais_bench --models "$MODEL_CONFIG_NAME" --datasets "$DATASET_CONFIG_NAME" \
  --mode perf --summarizer default_perf --work-dir "$RESULT_DIR" --debug
```

When an external warmup has already been performed, add `--num-warmups 0` only if the installed CLI supports it and it has the intended meaning. `--debug` was the historical single-process client mode; record execution mode rather than silently changing process parallelism. A version supporting combined configs can instead use `ais_bench /absolute/path/to/task_config.py --mode perf ...` with its documented syntax.

5. Preserve the resolved configuration, console logs, native summary/CSV and inference/performance detail artifacts under `RESULT_DIR`; locate their actual paths from the current tool output. Verify selected request count, successes/failures, actual lengths and measurement window before extracting TPS/TPOT/ITL. Do not depend on one hard-coded result subdirectory across versions.

## 2. vLLM bench serve

Sources: [CLI reference](https://docs.vllm.ai/en/stable/cli/bench/serve/) and [upstream benchmark implementation](https://github.com/vllm-project/vllm/tree/main/vllm/benchmarks). Use `bench serve` for an existing HTTP service, including a P/D proxy. `bench throughput` is an offline benchmark and does not measure the same serving path.

For frozen data, inspect the installed custom dataset loader. The local implementation inspected for this skill accepts JSONL rows like:

```json
{"prompt":"the exact frozen question text","output_tokens":1024}
```

Convert `question` to `prompt` without retokenizing, truncating or regenerating the text, retaining order and N. Check loader shuffling/sampling, chat-template application and output-length precedence. The format is version-specific; do not pass a GSM8K `question`/`answer` file straight to an incompatible loader.

The inspected custom loader **shuffles by default and locally applies the chat template by default**. With an `openai-chat` backend that wraps the prompt in a user message, local rendering can put an already rendered conversation inside another chat template. For raw question text going to `/v1/chat/completions`, use supported `--skip-chat-template --disable-shuffle` options to preserve raw content/order and let the server render once. Verify the request and server-reported input length; client prompt-length accounting with skipped local rendering may exclude server-added tokens. If these switches are absent in another version, resolve its equivalent behavior before claiming workload equivalence.

After confirming these options in the installed help, a streaming chat example is:

```bash
vllm bench serve --backend openai-chat \
  --base-url "$BASE_URL" --endpoint /v1/chat/completions \
  --model "$SERVED_MODEL" --tokenizer "$TOKENIZER_PATH" \
  --dataset-name custom --dataset-path "$CUSTOM_JSONL" \
  --skip-chat-template --disable-shuffle \
  --custom-output-len 1024 --num-prompts "$N" \
  --max-concurrency "$C" --request-rate inf \
  --temperature 0 --ignore-eos \
  --save-result --save-detailed \
  --result-dir "$RESULT_DIR" --result-filename result.json
```

Check the version's backend compatibility with ignore-EOS/extra payload fields; inspect the actual sent request where necessary. Do not enable `--no-stream` for an ITL experiment. Preserve native JSON, detailed per-request arrays and console output. Some versions lack SSE event token counts even with detailed saving; do not infer those counts from timestamps alone.

For an explicitly synthetic length test, use the supported random dataset options (`--dataset-name random --random-input-len ... --random-output-len ... --random-range-ratio 0`). This changes prompt content/cache/acceptance behavior and is not a replacement for the frozen GSM8K/GPQA workload. Verify resulting post-template lengths.

Account for client readiness probes/warmups in the metric window; inspect their behavior in the installed source. Report native means/percentiles and output-only throughput. Keep these runs separate from AISBench until prompt payloads, lengths, event handling and metric weights have been checked for equivalence.

In the inspected implementation, the initial real request is conditional on `ready_check_timeout_sec > 0`; the inspected CLI default is 0, so its log message about an initial test does not itself prove a request was sent. Other releases may differ. If external health checks/warmup have completed, supported `--ready-check-timeout-sec 0 --num-warmups 0` options avoid those particular extra requests; inspect other optional profiling/probe requests too. Otherwise collect before counters after client warmup through an appropriate boundary hook, or label server counter deltas as including extra traffic. A before snapshot taken before launching the client is not automatically aligned with its timed benchmark window.

The inspected chat backend sends `max_completion_tokens`, whereas older tools/proxies may expect `max_tokens`. Confirm the actual P/D proxy honors the received limit on both legs; a successful HTTP status does not prove an output-length setting was applied. The base URL should be the service/proxy root when the endpoint already contains `/v1/...`, avoiding a duplicated `/v1` path. Use a unique trial result directory to avoid overwriting `result.json`.

## 3. aisbench_auto_tools_prefix wrapper

Source and instructions: [rayn-zzz/aisbench_auto_tools_prefix](https://github.com/rayn-zzz/aisbench_auto_tools_prefix) / [README](https://github.com/rayn-zzz/aisbench_auto_tools_prefix/blob/main/README.md). This is a separate project that prepares datasets/configs and invokes AISBench; it is not the native CLI.

1. Preserve the wrapper revision/local modifications and its dependency files (`config.py`, API template, data generation/picker and result helpers). It requires an installed AISBench environment.
2. Configure `DATASET_PATH`, `WORK_PATH`, `MODEL_NAME`, tokenizer `MODEL_PATH`, proxy `HOST_IP/HOST_PORT` or URL, writable `OUTPUT_DIR`, and `POD_INFO` for actual P metrics endpoints. Verify what directory `WORK_PATH` means in that revision. Keep credentials task-local.
3. Inspect the generated model config: concurrency, request rate, output limit, streaming type, temperature, ignore-EOS, retries and summarizer. The historical wrapper writes configs and dataset links inside the AISBench tree and clears some logs per invocation; avoid concurrent wrapper runs sharing those files. Archive generated files/results before the next trial.
4. To generate a prefix workload, the historical interface was:

```bash
python3 aisbench_test.py --input_len 16384 --output_len 1024 \
  --data_num 4096 --concurrency 1024 --request_rate 0 \
  --dataset_type prefix_cache --prefix_num 32 --repeat_rate 1.0 --seed 1
```

This entrypoint may **generate and immediately test**, not merely generate. For data-only preparation, inspect and use the revision's generation function/script separately; do not run this command solely to create files when service testing is not authorized. Inspect picked-ID state and freeze the actual generated dataset. Check built-in `--prefix_test`/`--dp` warmup behavior against the real routing topology before relying on it for all-rank cache coverage.

5. For repeatable formal tests, explicitly consume the already expanded absolute dataset path:

```bash
python3 aisbench_test.py --dataset "$FROZEN_JSONL" \
  --input_len 16384 --output_len 1024 --data_num "$N" \
  --concurrency "$C" --request_rate 0 --dataset_type normal
```

Check whether a provided dataset bypasses generation/length processing in that revision. `normal` here does not remove common prefixes. Keep exact file row count and requested N aligned; do not assume oversampling/truncation behavior.

In the retained wrapper, an explicit `--dataset` bypasses construction and links the file into AISBench's GSM8K dataset location; `--data_num` is not itself forwarded as a native sample-count limit. Count the input rows and inspect the dataset reader's actual range; verify native completed count equals intended N. Likewise `--input_len` does not retokenize or truncate an explicitly supplied file in this path.

6. Save wrapper logs/CSV **and** underlying AISBench generated config/native results/request records. The wrapper summary is not a substitute for raw artifacts. Inspect log output to retain the exact `ais_bench` command it launched. Changing `DEFAULT_PERFORMANCE_TEST` to a steady-stage summarizer changes the statistic and must be a declared experiment choice, not a cosmetic setting.

The retained wrapper launches an `ais_bench ... | tee ...` shell pipeline without establishing pipefail inside that subprocess. Its zero exit status may therefore reflect `tee`, not AISBench success. An outer shell's pipefail does not automatically fix a nested `/bin/sh` subprocess. Require a complete native summary, expected request totals and failure checks; preserve the first causal error when absent. If exit propagation must be repaired, make that helper change explicit and validate a deliberately failing local command before relying on the status.

## Cross-client comparison gate

Before comparing clients, check the same frozen prompt order/subset, rendered messages, tokenizer, output controls, retries, C/N, arrival policy, cache warmup and service state. Preserve each tool's native figures and explicitly map meanings. Different ITL/SSE or averaging semantics can remain even with identical requests. If equivalence is unverified, label the result as a client comparison rather than evidence of a model performance change.
