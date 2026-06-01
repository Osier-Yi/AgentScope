# Tutorial 04: Tool Group — 动态工具管理

> **什么时候需要这个？** Agent 的工具一多，所有工具 Schema 都塞进上下文既浪费 token、又让 LLM 选错工具。把工具按"功能域"分组（数据 IO / 分析 / 可视化），让 Agent 按需切换，是工具数量上量后的标配做法。

## 本章基于前序章节

- **T03 — `Toolkit` / `ToolBase` / `FunctionTool`**：本章把 T03 的 `query_sales` 等工具按功能拆进不同 `ToolGroup`。

## 你将学到

- `basic` 保留组的特殊地位
- 如何定义和组织 ToolGroup
- `reset_tools` 元工具的工作原理
- Agent 自动切换工具组的最佳实践

## 前置要求

- 完成 Tutorial 03
- 理解 Toolkit 和 ToolBase 的基本概念

## 核心概念

### 为什么需要 Tool Group？

随着 Agent 配备的工具越来越多，所有工具的 JSON Schema 都会被发送给 LLM。这带来两个问题：

1. **上下文浪费**：大量不相关的工具描述消耗宝贵的 context window
2. **选择困难**：工具太多时 LLM 可能选错工具

ToolGroup 解决了这个问题：将工具按功能域分组，Agent 可以**按需激活/停用**工具组。

### basic 保留组

`basic` 是一个特殊的工具组：
- **始终激活**，不受 `reset_tools` 影响
- 当你直接传入 `tools=` 参数时，这些工具自动归入 `basic` 组
- 适合放入通用工具（Read, Write, Bash 等）

### ToolGroup 定义

```python
from agentscope.tool import ToolGroup

group = ToolGroup(
    name="analysis",
    description="Statistical analysis tools for computing summaries and trends.",
    instructions="Always validate input data before running analysis.",
    tools=[my_analysis_tool],
)
```

| 参数 | 说明 |
|------|------|
| `name` | 组名（`"basic"` 为保留名） |
| `description` | **必填**（basic 除外），Agent 用此决定是否激活 |
| `instructions` | 激活时返回给 Agent 的使用指南 |
| `tools` | 本组包含的工具列表 |
| `mcps` | 本组包含的 MCP 客户端 |
| `skills_or_loaders` | 本组包含的技能 |

### reset_tools 元工具

当 Toolkit 中存在非 basic 工具组时，系统自动注册 `reset_tools` 元工具。Agent 可以调用它来切换工具组：

- 每次调用表示**最终期望状态**（不是增量修改）
- 未设为 `True` 的组会被停用
- 激活时返回该组的 `instructions`
- `basic` 组不受影响

### 设计原则

- **按功能域分组**：数据读写、统计分析、可视化各一组
- **最小激活**：只激活当前任务需要的组
- **instructions 指导**：在组被激活时提供上下文相关的使用指南

## 示例：DataMuse 的三个工具组

本期将 DataMuse 的工具分为三个功能组：
1. **data_io** — 数据读写工具（Read, Glob, query_sales）
2. **analysis** — 统计分析工具（SalesSummary, Bash for Python scripts）
3. **visualization** — 图表生成工具（Bash for matplotlib）

Agent 会根据用户的请求自动切换到合适的工具组。

## 运行示例

```bash
cd tutorials/04_tool_groups
python main.py
```

## 进一步探索

- 将 MCP 客户端放入工具组，观察激活/停用行为
- 创建一个包含 Skill 的工具组
- 增加组数量，观察 Agent 在复杂场景下的组切换决策

## 下一期预告

**Tutorial 05: MCP 集成** — 通过 MCP 协议连接外部工具服务器，让 DataMuse 访问数据库和网页。
