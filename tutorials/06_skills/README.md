# Tutorial 06: Skill — 用 Markdown 扩展 Agent 能力

> **什么时候需要这个？** 某个任务需要"按一套套路组合多个工具"（比如：先采样数据 → 决定图表类型 → matplotlib 画图 → 保存）。你想把这套套路用 Markdown 沉淀下来，让 Agent 按需加载，而不是把它塞进 system prompt 让模型每次重新摸索。

## 本章基于前序章节

- **T03 — `Toolkit` / 内置工具**：Skill 不替代工具，它指导 Agent 如何**组合**已有工具（Bash / Read / Write 等）完成复杂任务。
- **T04 — `ToolGroup`**：Skill 可以挂进任一 ToolGroup，跟随该组激活/停用。

## 你将学到

- Skill 的本质：Markdown 指令集，不是工具
- `SKILL.md` 的结构：frontmatter 元数据 + 详细指令
- `LocalSkillLoader`：从目录加载技能
- `SkillViewer` 工具：Agent 如何读取和使用技能
- Skill 与 ToolGroup 的组合使用

## 前置要求

- 完成 Tutorial 05
- 理解 Toolkit 和 ToolGroup 的基本概念

## 核心概念

### Skill 不是工具

这是理解 Skill 的关键——**Skill 不是工具**。工具有 Schema、可以被 LLM 直接调用；Skill 是一组 Markdown 格式的指令，告诉 Agent *如何组合使用现有工具*来完成特定任务。

```
工具 = 原子操作（读文件、执行命令、查询数据）
技能 = 操作指南（如何组合工具来生成图表、写报告）
```

Agent 通过 `SkillViewer` 工具读取 Skill 的内容，然后按照指令用已有的工具去执行。

### SKILL.md 结构

每个 Skill 是一个目录，其中包含一个 `SKILL.md` 文件：

```
skills/
├── chart_generator/
│   └── SKILL.md
└── report_writer/
    ├── SKILL.md
    └── templates/
        └── report_template.md
```

`SKILL.md` 使用 frontmatter 定义元数据：

```markdown
---
name: chart_generator
description: Generate charts using matplotlib. Supports bar, line, pie.
---

# Chart Generator Skill

详细的使用指令...
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 技能名称，Agent 通过此名称引用 |
| `description` | 是 | 技能描述，展示在系统提示中帮助 Agent 判断何时使用 |

frontmatter 之后的 Markdown 内容是完整的使用指令，只有当 Agent 调用 `SkillViewer` 工具时才会被加载。

### LocalSkillLoader

`LocalSkillLoader` 从本地目录加载 Skill：

```python
from agentscope.skill import LocalSkillLoader

# 加载单个 Skill 目录
loader = LocalSkillLoader(directory="skills/chart_generator")

# 扫描子目录，加载所有 Skill
loader = LocalSkillLoader(directory="skills", scan_subdir=True)
```

| 参数 | 说明 |
|------|------|
| `directory` | Skill 目录路径 |
| `scan_subdir` | 是否扫描子目录（默认 `False`） |

### SkillViewer 工具

当 Toolkit 中注册了 Skill 时，系统自动添加 `SkillViewer` 工具（对 Agent 显示为 `Skill`）。Agent 可以调用它来读取技能的完整指令：

```
Agent 看到系统提示中列出的技能摘要
  ↓
决定使用某个技能
  ↓
调用 SkillViewer("chart_generator") 读取完整指令
  ↓
按照指令使用 Bash/Read/Write 等工具执行
```

系统提示中只包含技能的名称和描述（节省 context），完整指令通过工具调用按需加载。

### Skill 与 ToolGroup

Skill 可以放在任何 ToolGroup 中，随组一起激活/停用：

```python
Toolkit(
    tools=[Read(), Bash()],
    skills_or_loaders=[
        LocalSkillLoader("skills/common", scan_subdir=True),
    ],
    tool_groups=[
        ToolGroup(
            name="visualization",
            description="Chart and visualization tools",
            skills_or_loaders=[
                LocalSkillLoader("skills/chart_generator"),
            ],
        ),
    ],
)
```

- `tools=` / `skills_or_loaders=` 中的技能归入 `basic` 组（始终可用）
- `ToolGroup.skills_or_loaders` 中的技能随组激活/停用

## 示例：给 DataMuse 添加技能

本期创建两个 Skill：

1. **chart_generator** — 指导 Agent 用 matplotlib 生成图表
2. **report_writer** — 指导 Agent 生成结构化的 Markdown 分析报告

Agent 在收到相关任务时，先通过 SkillViewer 读取技能指令，再用 Bash、Read 等工具执行。

## 运行示例

```bash
cd tutorials/06_skills
python main.py
```

## 进一步探索

- 创建自己的 Skill（如 `data_cleaner`），处理数据清洗任务
- 将 Skill 放入不同的 ToolGroup，测试激活/停用行为
- 在 Skill 中引用资源文件（模板、配置），观察 `dir` 字段的作用
- 尝试实时修改 SKILL.md 内容，观察 LocalSkillLoader 的缓存刷新

## 下一期预告

**Tutorial 07: Permission 系统** — 控制 Agent 的行为边界，配置五种权限模式和精细的规则。
