# Tutorial 13: Agent Service — 部署为线上服务

> **什么时候需要这个？** 单脚本跑通后，你要把 Agent 暴露成 HTTP 服务：支持多用户隔离、多 Session 并行、状态持久化、Web/移动端通过 REST + SSE 接入。`create_app()` 把前面所有模块打包成一个 FastAPI 应用。

## 本章基于前序章节

- **T09 — 流式事件**：HTTP `/chat` 通过 SSE 推送的就是 T09 渲染的那套 AgentEvent。
- **T10 — `ContextConfig`**：Session 创建时绑定的 context 配置。
- **T11 — Middleware**：服务端 Agent 同样可以挂中间件做日志/计费/tracing。
- **T12 — Workspace / `WorkspaceManager`**：每个 Session 通过 `WorkspaceManager` 拿到一个隔离的 Workspace。

## 你将学到

- `create_app()` 工厂函数的使用
- 多租户架构：`user_id` 隔离
- Session 模型：Agent 模板 vs 运行时状态
- Credential 集中管理
- SSE 流式通信
- 连接官方示例 Web UI
- REST API 的完整流程

## 前置要求

- 完成 Tutorial 11
- 安装服务依赖：`pip install "agentscope[service,storage]"`
- Redis 服务（用于持久化存储）
- 如需体验 Web UI：Node.js 20+ 与 `pnpm`

## 核心概念

### 从脚本到服务

前面的教程都是单脚本运行的 Agent。在真实部署中，我们需要：

- **多用户**：不同用户的 Agent 相互隔离
- **多会话**：同一用户可以有多个对话
- **持久化**：重启后恢复状态
- **HTTP API**：Web/移动客户端可以接入

### create_app() 工厂函数

```python
from agentscope.app import create_app, RedisStorage, LocalWorkspaceManager

app = create_app(
    storage=RedisStorage(host="localhost", port=6379),
    workspace_manager=LocalWorkspaceManager(basedir="./workspaces"),
)
```

`create_app()` 返回一个 FastAPI 应用，内置以下路由：

| 路由前缀 | 功能 |
|----------|------|
| `/credential` | API Key 管理 |
| `/agent` | Agent 模板管理 |
| `/sessions` | 会话管理 |
| `/chat` | 流式对话 |
| `/schedule` | 定时任务 |

### 多租户架构

每个请求通过 `user_id` Header 标识用户：

```
Client → HTTP Request (X-User-Id: user123) → AgentScope Service
                                                 ↓
                                          user_id 隔离
                                          ├─ Credentials
                                          ├─ Agents
                                          └─ Sessions
```

### Agent 与 Session 的关系

```
Agent（模板）              Session（运行时）
├─ name                   ├─ session_id
├─ system_prompt          ├─ agent_id（关联模板）
├─ context_config         ├─ chat_model_config
└─ react_config           ├─ context（对话历史）
                            └─ state（权限、工具状态）
```

- **Agent** 是模板：定义了 Agent 的配置
- **Session** 是实例：每次对话创建一个 Session，包含独立的上下文和状态
- 同一个 Agent 模板可以创建多个 Session

### 完整 API 流程

```
1. POST /credential/                    ── 创建 API Key
2. POST /agent/                         ── 创建 Agent 模板
3. POST /sessions/                      ── 创建 Session 并绑定模型
4. POST /chat/                          ── 发送消息（SSE 流式返回）
5. GET  /sessions/{id}/messages         ── 查看会话消息
```

### Web UI

AgentScope 2.0 仓库里包含一个配套 Web UI，位于 `examples/web_ui`。它不是 Python extra 的一部分，而是一个独立的前端示例，用来连接上面由 `create_app()` 启动的 Agent Service。

启动 Agent Service 后，在另一个终端运行：

```bash
cd examples/web_ui
pnpm install
pnpm dev
```

打开 Web UI 后，在 setup 页面把服务器地址填为 `http://localhost:8000`，用户名可以填 `demo-user`。后续创建 Credential、Agent、Session 和发送消息，都可以通过界面完成；这和下面的 `curl` 流程调用的是同一组后端 API。

### SSE 流式通信

`POST /chat` 返回 Server-Sent Events 流，每个事件对应一个 AgentEvent：

```
data: {"type": "REPLY_START", "reply_id": "xxx", ...}
data: {"type": "TEXT_BLOCK_DELTA", "delta": "Hello", ...}
data: {"type": "MODEL_CALL_END", "input_tokens": 100, ...}
data: {"type": "REPLY_END", ...}
```

### Workspace 隔离

`WorkspaceManager` 为每个 Session 提供隔离的工作环境：

| 类型 | 说明 |
|------|------|
| `LocalWorkspaceManager` | 本地目录隔离 |
| `DockerWorkspaceManager` | Docker 容器隔离 |
| `E2BWorkspaceManager` | E2B 沙箱隔离 |

### 模型 fallback 与自动重试

服务化之后，模型挂掉/限流就不再是"重跑一次"能解决的事——请求来自真实用户或定时任务，必须**自动**降级或重试。AgentScope 把这套逻辑放在 `ModelConfig` 上：

```python
from agentscope.agent import Agent
from agentscope.agent._config import ModelConfig
from agentscope.credential import DashScopeCredential
from agentscope.model import DashScopeChatModel

primary = DashScopeChatModel(
    credential=DashScopeCredential(api_key=os.environ["DASHSCOPE_API_KEY"]),
    model="qwen-plus",
)
backup = DashScopeChatModel(
    credential=DashScopeCredential(api_key=os.environ["DASHSCOPE_API_KEY"]),
    model="qwen-turbo",  # 便宜、稳定的兜底
)

agent = Agent(
    name="DataMuse",
    system_prompt="...",
    model=primary,
    model_config=ModelConfig(
        max_retries=2,        # 主模型先重试 2 次
        fallback_model=backup, # 还失败就切到 backup（backup 也享受 max_retries）
    ),
)
```

语义：
- `max_retries=0`（默认）→ 调一次就失败，立刻切 fallback
- `max_retries=N` → 主模型连试 N+1 次都不行，再切 fallback；fallback 同样享受 N+1 次额度
- `fallback_model=None`（默认）→ 没有兜底，失败直接抛

什么时候配？
- **对外 API 服务**：用户在等响应，必须有兜底
- **定时任务（T14）**：无人值守失败就只能等下次 cron，必须自动重试 + fallback
- **dev/exploration**：通常不需要——失败让它显式报错，反而能更快定位

## 示例：部署 DataMuse 服务

本期展示如何用 `create_app` 创建一个完整的 Agent 服务，并用三种方式驱动它：`curl`、`client.py`（Python httpx）、Web UI。

Agent 模板只保存名称、系统提示词和运行配置；具体模型在创建 Session 时通过 `chat_model_config` 绑定。**Agent 模板不能挂自定义 Python `ToolBase`** —— 想给服务端 Agent 加能力，只能走 `LocalWorkspaceManager` 的 `default_mcps` / `skill_paths`（本期 `main.py` 已经注入了 T06 的 `report_writer` skill）。

> 默认存储用 `fakeredis` 跑内存模式，**无需启动真实 Redis**。线上环境把 `_make_inmemory_storage()` 换成 `RedisStorage(host=..., port=...)` 即可。

## 运行示例

```bash
# 安装零依赖运行所需的两个小包
pip install fakeredis httpx

# 终端 A：启动服务（默认 8000，无 Redis 依赖）
cd tutorials/13_agent_service
python main.py

# 终端 B：用 Python httpx 走完 5 步 API 流程
cd tutorials/13_agent_service
python client.py
```

`client.py` 会依次：

1. `POST /credential/` — 用环境变量里的 `DASHSCOPE_API_KEY` / `OPENAI_API_KEY` 注册 Credential
2. `POST /agent/` — 创建 DataMuse Agent 模板
3. `POST /sessions/` — 建一个 Session 并绑定模型
4. `POST /chat/` — 流式打印 SSE 事件（`TEXT_BLOCK_DELTA` / `TOOL_CALL_START` / `TOOL_RESULT_END`）
5. `GET /sessions/{id}/messages` — 列出已持久化的对话

如果偏好命令行，仍可用 curl —— `main.py` 的 `print_overview()` 会列出每一步的 endpoint。

如果要用 Web UI 体验同一个服务：

```bash
# 在仓库根目录的另一个终端
cd examples/web_ui
pnpm install
pnpm dev
```

Web UI 首次打开时填入 `http://localhost:8000` 和一个用户名即可。

## 进一步探索

- 挂载到已有的 FastAPI 应用中
- 配置 Docker Workspace 实现更强的隔离
- 自定义认证中间件替换默认的 `X-User-Id` Header
- 使用 `extra_credentials` 注册自定义 Credential 类型

## 下一期预告

**Tutorial 14: Schedule** — 配置定时任务，让 DataMuse 自动生成日报。
