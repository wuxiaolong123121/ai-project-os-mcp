#!/usr/bin/env python3
"""
测试架构检查功能
"""

from ai_project_os_mcp.core.architecture_linter import ArchitectureLinter

# 创建架构检查器实例
linter = ArchitectureLinter()

# 检查架构
project_root = "."
result = linter.check_architecture(project_root)

# 输出结果
print("\n架构检查结果:")
print(f"Schema Version: {result['schema_version']}")
print(f"扫描模块数: {result['scanned_modules']}")
print(f"允许的边数: {len(result['allowed_edges'])}")
print(f"违规数: {len(result['violations'])}")

if result['violations']:
    print("\n违规详情:")
    for i, violation in enumerate(result['violations'], 1):
        print(f"{i}. {violation['rule_violated']}: {violation['message']}")
        print(f"   Source: {violation['source']}")
        print(f"   Target: {violation['target']}")
else:
    print("\n✅ 没有发现架构违规")

print("\n允许的边:")
for edge in result['allowed_edges']:
    print(f"   {edge['source']} → {edge['target']}")
