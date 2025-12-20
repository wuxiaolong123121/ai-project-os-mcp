#!/usr/bin/env python3
"""
依赖检查脚本 - 检查项目依赖是否符合配置中的白名单和黑名单

用于集成到 pre-commit 钩子，发现黑名单依赖直接拒绝提交
"""

import os
import sys
import yaml

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from ai_project_os_mcp.tools.context_tools import analyze_dependencies

def check_dependencies():
    """
    检查项目依赖是否符合配置
    
    Returns:
        int: 0 表示成功，非 0 表示失败
    """
    print("开始检查项目依赖...")
    
    # 加载配置
    config_path = os.path.join(project_root, "config.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 加载配置失败: {str(e)}")
        return 1
    
    # 调用依赖分析工具
    result = analyze_dependencies({}, {})
    
    # 检查违规
    violations = result.get("violations", [])
    if violations:
        print(f"❌ 发现 {len(violations)} 个依赖违规:")
        for violation in violations:
            print(f"   - {violation['type']}: {violation['message']}")
        return 1
    
    print("✅ 所有依赖检查通过")
    return 0

if __name__ == "__main__":
    sys.exit(check_dependencies())
