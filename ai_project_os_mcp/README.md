# AI Project OS MCP SDK

工程级AI行为控制协议SDK，用于将AI自动编程约束进真实软件工程流程。

## 🌟 价值主张

- **AI 无法绕规则**：状态即真理，行为可审计
- **Prompt 不再是唯一约束**：结合代码级约束和流程级约束
- **可接任何 Agent**：Claude、Cursor、Trae、本地Agent等
- **工程级安全**：严格遵循5S工作流，确保AI只在当前冻结阶段行动

## 📦 安装

```bash
pip install ai-project-os-mcp
```

## 🚀 快速开始

```python
from ai_project_os_mcp import MCPServer, tools

# 初始化 MCP Server
server = MCPServer(project_root=".")

# 注册 MCP 工具
server.register_tool(tools.get_stage)
server.register_tool(tools.freeze_stage)
server.register_tool(tools.guard_src)
server.register_tool(tools.submit_audit)

# 启动 MCP Server
server.start()

# 使用工具
stage_result = server.handle_request("get_stage")
print(f"当前阶段: {stage_result}")
```

## 🛠️ 核心功能

### 1. 状态管理

- 权威的 `state.json` 读写
- 确保项目状态的一致性和完整性
- 支持状态验证和版本控制

### 2. 规则引擎

- 5S 工作流规则
- S5 稳定性规则
- 阶段转换验证
- 代码生成限制

### 3. 硬拒绝机制

- 规则违反时的硬拒绝处理
- 详细的违反原因记录
- 违反计数统计

### 4. MCP 工具集

- `get_stage`: 获取当前项目阶段
- `freeze_stage`: 冻结项目到下一个阶段
- `guard_src`: 验证是否允许修改src目录
- `submit_audit`: 提交S5审计记录

### 5. Agent 适配器

- `ClaudeAdapter`: Claude AI 适配器
- `CursorAdapter`: Cursor AI 适配器
- `TraeAdapter`: Trae 多Agent 适配器

## 📁 项目结构

```
ai_project_os_mcp/
├─ core/               # 核心模块
│  ├─ state_manager.py     # state.json 权威读写
│  ├─ rule_engine.py       # 5S + S5 稳定性规则
│  └─ violation.py         # Hard Refusal
├─ tools/              # MCP 工具集
│  ├─ get_stage.py
│  ├─ freeze_stage.py
│  ├─ guard_src.py
│  └─ submit_audit.py
├─ adapters/           # Agent 适配器
│  ├─ claude.py
│  ├─ cursor.py
│  └─ trae.py
└─ server.py           # MCP Server
```

## 🎯 使用场景

### 1. 独立开发者

- 确保AI只在正确的阶段生成代码
- 自动记录所有工程决策
- 提高项目的可维护性

### 2. 团队协作

- 统一的工程流程
- 明确的角色分工
- 可审计的AI行为
- 避免项目失控

### 3. 企业级应用

- 合规的AI开发流程
- 完整的审计链路
- 可控的AI风险
- 可扩展的Agent支持

## 📄 文档

- [MCP 白皮书](./docs/whitepaper.md) - 完整的MCP设计理念和架构
- [API 文档](./docs/api.md) - 详细的API参考
- [示例代码](./examples/) - 各种使用场景的示例

## 🔧 开发

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/ai-project-os/ai-project-os-mcp.git
cd ai-project-os-mcp

# 安装依赖
pip install -e .

# 运行测试
pytest
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT

## 📞 联系方式

- 项目主页：https://github.com/ai-project-os/ai-project-os-mcp
- 邮件：contact@ai-project-os.com
- Twitter：@ai_project_os
