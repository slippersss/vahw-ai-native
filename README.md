# VAHW AI Native

这是一个面向 AI 协作的 meta 仓库。`VA` 代表 vLLM Ascend，它是当前主要业务方向；本仓库本身用于沉淀跨任务、跨项目和跨 Agent 的规则、Skills 与工作流。

## Structure

```text
skills/
├── ai-native-meta/   # 工作区级元规则
├── feature/          # 特性开发经验与能力
├── debugging/        # 问题定位经验与能力
├── testing/          # 测试经验与能力
└── workflow/         # 跨任务工作流

misc/                 # 非主流程、供用户手动运行的实用工具
workspace/            # 实际业务工作区，不由 meta 仓库跟踪
```

当前已有：

- [`ai-native-meta`](skills/ai-native-meta/SKILL.md)：沟通、沉淀、Skill 编写和提交约定。
- [`learning`](skills/learning/SKILL.md)：渐进式技术学习、精确图示、阶段材料整理与资料仓发布流程。
- [`debugging`](skills/debugging/SKILL.md)：证据驱动定位，包含推理一致性、Ascend 数值与 KV cache 污染、图模式探针，以及跨版本回归 UT 接口核对。
- [`remote-work`](skills/workflow/remote-work/SKILL.md)：多远程机器、执行前同步和长任务管理的最小工作流。
- [`install-vllm-ascend`](skills/workflow/install-vllm-ascend/SKILL.md)：远程环境中选择兼容版本并从源码安装 vLLM 与 vLLM Ascend。
- [`setup-vllm-ascend-fast`](skills/workflow/setup-vllm-ascend-fast/SKILL.md)：基于预装镜像快速建立远程软链接工作区、补全 vLLM 历史并对齐本地代码。
- [`install-aisbench`](skills/workflow/install-aisbench/SKILL.md)：在远程昇腾环境中按惯用 tag 源码安装 AISBench benchmark。

手动工具：

- [`download-vllm-ascend-image.sh`](misc/download-vllm-ascend-image.sh)：在容器内通过 tag 或 digest 下载 vLLM Ascend 镜像并导出 Docker tar。

具体经验从真实工作中逐步沉淀；一次性项目事实不直接升级为 meta 规则。
