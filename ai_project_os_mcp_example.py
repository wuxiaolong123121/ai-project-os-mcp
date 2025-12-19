"""
AI Project OS MCP SDK 使用示例
"""

from ai_project_os_mcp import MCPServer, tools

# 初始化 MCP Server
server = MCPServer(project_root=".")

# 注册 MCP 工具
server.register_tool(tools.get_stage)
server.register_tool(tools.freeze_stage)
server.register_tool(tools.guard_src)
server.register_tool(tools.submit_audit)

# 启动 MCP Server
start_result = server.start()
print(f"MCP Server 启动结果: {start_result}")

# 示例：获取当前阶段
stage_result = server.handle_request("get_stage")
print(f"当前阶段: {stage_result}")

# 示例：冻结到 S2 阶段
freeze_result = server.handle_request("freeze_stage", {
    "target_stage": "S2"
})
print(f"冻结到 S2 结果: {freeze_result}")

# 示例：检查是否可以修改 src 目录
guard_result = server.handle_request("guard_src", {
    "intent": "write"
})
print(f"src 目录访问权限: {guard_result}")

# 停止 MCP Server
stop_result = server.stop()
print(f"MCP Server 停止结果: {stop_result}")
