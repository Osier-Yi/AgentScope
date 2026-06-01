# Tutorial 15: Multi-Agent — 多 Agent 协作

> **什么时候需要这个？** 单 Agent 的工具太多导致上下文撑爆、LLM 选错工具，或者任务可以清晰拆成几个角色（采集 / 分析 / 写报告）。多 Agent 协作让每个 Agent 只关心自己那一摊，用 Python 代码做编排。

## 本章基于前序章节

- **T01 — Agent / `reply` / `reply_stream`**：每个角色都是一个独立 Agent 实例。
- **T03 — 工具系统**：不同角色配不同工具集（Collector 配 `query_sales`，Writer 配 `Bash` 写文件等）。
- **T02 — `Msg`**：Agent 之间通过传递消息接力，`observe()` 用来注入背景但不触发推理。

## 你将学到

- AgentScope 2.0 的多 Agent 设计思路
- `observe()` 方法：无推理的消息注入
- 多 Agent 编排模式：串行、并行、动态路由
- Agent 间的消息传递和结果接力
- 编排逻辑的实现方式

## 前置要求

- 完成 Tutorial 01-14
- 理解 Agent 的 reply、reply_stream、observe API

## 核心概念

### 为什么需要多 Agent？

单个 Agent 虽然能力强大，但在复杂任务中会遇到瓶颈：

- **上下文爆炸**：同时处理数据采集、分析、可视化时，上下文迅速膨胀
- **工具冲突**：太多工具让 LLM 选择困难
- **职责不清**：一个 Agent 同时承担多个角色效率低

多 Agent 的解决方案：每个 Agent 专注一个职责，通过编排逻辑协作。

### AgentScope 的多 Agent 设计

AgentScope 2.0 不提供内置的"编排框架"——它提供**消息传递原语**，让你用 Python 代码实现编排：

```python
# Agent 之间通过消息传递协作
result = await agent_a.reply(user_msg)        # A 处理
await agent_b.observe(result)                  # B 接收 A 的结果（不触发推理）
final = await agent_b.reply(follow_up_msg)    # B 基于上下文推理
```

### observe() vs reply()

| 方法 | 行为 | 用途 |
|------|------|------|
| `reply(msg)` | 接收消息 → 触发推理 → 返回回复 | 需要 Agent 思考和行动 |
| `observe(msg)` | 接收消息 → 仅存入上下文 | 提供背景信息，不触发推理 |

`observe()` 是多 Agent 协作的关键：它让 Agent 获得上下文信息，而不需要立即响应。

### 三种编排模式

#### 1. 串行流水线

```
User → Agent A → Agent B → Agent C → Result
          │          │          │
       采集数据    分析数据    生成报告
```

```python
data = await collector.reply(user_msg)
await analyst.observe(data)
analysis = await analyst.reply(analyze_msg)
await writer.observe(analysis)
report = await writer.reply(write_msg)
```

#### 2. 并行分支

```
                ┌→ Agent B (分析 A) ─┐
User → Agent A ─┤                    ├→ Agent D (汇总)
                └→ Agent C (分析 B) ─┘
```

```python
data = await collector.reply(user_msg)
await analyst_a.observe(data)
await analyst_b.observe(data)
result_a, result_b = await asyncio.gather(
    analyst_a.reply(task_a_msg),
    analyst_b.reply(task_b_msg),
)
await summarizer.observe(result_a)
await summarizer.observe(result_b)
summary = await summarizer.reply(summarize_msg)
```

#### 3. 动态路由

```
User → Router Agent ──┬→ Agent A (简单任务)
                      ├→ Agent B (复杂任务)
                      └→ Agent C (特殊任务)
```

```python
routing = await router.reply(user_msg)
route = parse_route(routing)

if route == "simple":
    result = await simple_agent.reply(user_msg)
elif route == "complex":
    result = await complex_agent.reply(user_msg)
```

## 示例：DataMuse 团队

本期创建三个角色的 DataMuse 团队：

1. **DataCollector** — 数据采集员，配备 Read、Glob、query_sales 工具
2. **DataAnalyst** — 数据分析师，配备 SalesSummary 和 Bash 工具
3. **ReportWriter** — 报告撰写员，配备 Bash 工具（用于写文件）

编排流程：用户提出分析需求 → Collector 采集 → Analyst 分析 → Writer 出报告

## 运行示例

```bash
cd tutorials/14_multi_agent
python main.py
```

## 进一步探索

- 实现并行分析：让 RegionAnalyst 和 CategoryAnalyst 同时工作
- 添加动态路由：根据用户请求复杂度选择不同的处理流程
- 创建一个"审核员" Agent，检查报告质量并决定是否需要重新分析
- 用 Middleware 实现 Agent 间通信的日志追踪

## 系列总结

恭喜完成全部 16 期教程！你已经掌握了 AgentScope 2.0 的核心能力：

| Phase | 内容 |
|-------|------|
| 基础篇 (01-03) | Agent 基础、消息/事件、工具系统 |
| 进阶篇 (04-10) | 工具组、MCP、Skill、权限、人机协作、流式 UI、上下文管理 |
| 工程篇 (11-14) | 中间件、Workspace、服务部署、定时任务 |
| 高级篇 (15-16) | 多 Agent 协作、完整 DataMuse |
