# VAHW AI Native

这是一个面向 AI 协作的 meta 仓库。`VA` 代表 vLLM Ascend，它是当前主要业务方向；本仓库本身用于沉淀跨任务、跨项目和跨 Agent 的规则、Skills 与工作流。

## Structure

```text
skills/
├── ai-native-meta/   # 工作区级元规则
├── feature/          # 特性开发经验与能力
├── debugging/        # 问题定位经验与能力
├── testing/          # 测试经验与能力
└── workflow/         # 安装、环境准备与远程执行等操作流程

misc/                 # 非主流程、供用户手动运行的实用工具
workspace/            # 实际业务工作区，不由 meta 仓库跟踪
```

当前已有：

- [`ai-native-meta`](skills/ai-native-meta/SKILL.md)：沟通、沉淀、Skill 编写和提交约定。
- [`learning`](skills/learning/SKILL.md)：渐进式技术学习、精确图示、阶段材料整理与资料仓发布流程。
- [`debugging`](skills/debugging/SKILL.md)：证据驱动定位，包含KV分配与释放时序、容量量化、推理一致性、Ascend数值与缓存污染、图模式探针和跨版本回归接口核对。
- [`benchmark-vllm-ascend`](skills/testing/benchmark-vllm-ascend/SKILL.md)：推理性能测试，包含 AISBench、vLLM bench、前缀数据工具、并发扫描、TPOT 配平与指标核对。
- [`write-validation-report`](skills/workflow/write-validation-report/SKILL.md)：用于测试、调试和特性开发的自包含技术报告，覆盖证据与图表、客观结论、复现附录及 Markdown 目录交付。
- [`remote-work`](skills/workflow/remote-work/SKILL.md)：多远程机器、执行前同步和长任务管理的最小工作流。
- [`install-vllm-ascend`](skills/workflow/install-vllm-ascend/SKILL.md)：远程环境中选择兼容版本并从源码安装 vLLM 与 vLLM Ascend。
- [`install-vllm-gpu`](skills/workflow/install-vllm-gpu/SKILL.md)：在 NVIDIA GPU 容器中安装 editable vLLM，覆盖预编译扩展、依赖兼容、启动排障和分层验收。
- [`setup-vllm-ascend-fast`](skills/workflow/setup-vllm-ascend-fast/SKILL.md)：基于预装镜像快速建立远程软链接工作区、补全 vLLM 历史并对齐本地代码。
- [`install-aisbench`](skills/workflow/install-aisbench/SKILL.md)：在远程昇腾环境中按惯用 tag 源码安装 AISBench benchmark。

手动工具：

- [`download-vllm-ascend-image.sh`](misc/download-vllm-ascend-image.sh)：在容器内通过 tag 或 digest 下载 vLLM Ascend 镜像并导出 Docker tar。

具体经验从真实工作中逐步沉淀；一次性项目事实不直接升级为 meta 规则。

- [`profile-vllm-ascend`](skills/testing/profile-vllm-ascend/SKILL.md)：真实负载中间窗口采集、完整rank覆盖、HTTP控制与导出/资源释放核验。
- [`analyze-ascend-profile`](skills/debugging/analyze-ascend-profile/SKILL.md)：跨rank、step、层和kernel分析，包含大trace流式读取、padding与异步等待归因。
- [`deploy-ascend-kv-pooling`](skills/workflow/deploy-ascend-kv-pooling/SKILL.md)：已有环境下的MemCache DRAM池化部署，包含Meta、存储owner、P/D组合和实际外部命中验证。
