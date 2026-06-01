# AgentScope 2.0 Tutorial Series

> **DataMuse** — 一个从零到上线的智能数据分析助手

本教程系列以一个**数据分析助手 DataMuse** 为贯穿示例，从最简单的对话 Agent 逐步演进为具备工具调用、权限控制、人机协作、流式 UI、上下文管理、中间件、服务部署、定时任务和多 Agent 协作能力的完整应用。

## 目标受众

有 LLM API 调用经验的**中级开发者**，了解 Agent 基本概念，想系统学习 AgentScope 2.0。

## 前置要求

- Python 3.12
- `pip install agentscope`
- 至少一个 LLM API Key（DashScope / OpenAI / Ollama）

## 教程列表

### Phase 1: 基础篇

| # | 主题 | 你将学到 |
|---|------|----------|
| [01](01_hello_agentscope/) | **Hello AgentScope** | 核心四要素、reply vs reply_stream、切换模型 |
| [02](02_message_and_event/) | **Message & Event** | 消息结构、事件生命周期、append_event 重建消息 |
| [03](03_tools/) | **Tool 系统** | 内置工具、FunctionTool、自定义 ToolBase |

### Phase 2: 进阶篇

| # | 主题 | 你将学到 |
|---|------|----------|
| [04](04_tool_groups/) | **Tool Group** | 工具分组、动态切换、reset_tools 元工具 |
| [05](05_mcp_integration/) | **MCP 集成** | MCP 协议、Stdio/HTTP 连接、与本地工具混合使用 |
| [06](06_skills/) | **Skill** | Markdown 技能定义、SkillViewer、技能加载 |
| [07](07_permissions/) | **Permission 系统** | 五种模式、规则配置、危险路径保护 |
| [08](08_human_in_the_loop/) | **Human-in-the-Loop** | 用户确认、外部执行、渐进式信任 |
| [09](09_streaming_ui/) | **流式 UI** | 事件分发、Token 追踪、终端 UI |
| [10](10_context_management/) | **Context 管理** | 上下文压缩、工具结果截断、Offloader |

### Phase 3: 工程篇

| # | 主题 | 你将学到 |
|---|------|----------|
| [11](11_middleware/) | **Middleware** | 5 个 Hook、洋葱模型、TracingMiddleware、计费/日志 |
| [12](12_workspace/) | **Workspace** | LocalWorkspace、Docker/E2B 隔离、Offloader、MCP/Skill 管理 |
| [13](13_agent_service/) | **Agent Service** | FastAPI 服务、多租户、Session、Credential、Web UI、**模型 fallback / 自动重试** |
| [14](14_scheduling/) | **Schedule** | Cron 定时任务、Stateful/Stateless 模式 |

### Phase 4: 高级篇

| # | 主题 | 你将学到 |
|---|------|----------|
| [15](15_multi_agent/) | **Multi-Agent** | 多 Agent 编排、observe()、串行/并行/动态路由 |
| [16](16_complete_datamuse/) | **Complete DataMuse** | 串联工具、权限、事件、上下文、中间件和 Workspace，搭建完整 Data Agent |

## 示例数据

所有教程共用同一份电商销售数据集 `data/sales_data.csv`（1000 行），包含：

```
order_id, date, product, category, quantity, unit_price, discount, total, region, payment_method, customer_tier
```

生成方式：

```bash
cd tutorials/data
python generate_sales_data.py
```

## 快速开始

```bash
# 准备环境
conda create -n agentscope-tutorial-py312 python=3.12 -y
conda activate agentscope-tutorial-py312
pip install agentscope

# 设置 API Key
export DASHSCOPE_API_KEY="your-key"

# 运行第一个教程
cd tutorials/01_hello_agentscope
python main.py
```

## 最终整合

如果你想先看完整应用的样子，可以直接运行 [16_complete_datamuse](16_complete_datamuse/)：

```bash
# 如果还没有准备环境，先执行：
conda create -n agentscope-tutorial-py312 python=3.12 -y
conda activate agentscope-tutorial-py312
pip install agentscope
export DASHSCOPE_API_KEY="your-key"

cd tutorials/16_complete_datamuse
python main.py
```

它会把前面章节中的关键模块收束成一个最小可用的 DataMuse：读取销售数据、做维度拆解、在写报告前触发确认，并把 Markdown 报告保存到本地 workspace。
