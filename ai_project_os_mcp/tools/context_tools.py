"""
Context Tools - 帮助Agent理解项目上下文
"""

import os
import re
from ai_project_os_mcp.config import config

def read_architecture(state, payload):
    """
    读取项目架构定义
    
    Args:
        state: 当前项目状态
        payload: 工具负载 (未使用)
        
    Returns:
        dict: 架构定义
    """
    # 这里可以从文件读取，或者返回硬编码的架构
    # 假设架构定义在 docs/architecture.md 或 config中
    
    architecture = {
        "layers": ["core", "tools", "adapters", "server"],
        "rules": config.rules,
        "allowed_dirs": ["ai_project_os_mcp", "docs", "examples", "tests", "scripts"]
    }
    
    return {
        "architecture": architecture,
        "source": "config"
    }

def analyze_dependencies(state, payload):
    """
    分析项目依赖关系
    
    Args:
        state: 当前项目状态
        payload: 工具负载 (未使用)
        
    Returns:
        dict: 依赖分析结果
    """
    project_root = config.project_root
    dependencies = {}
    
    # 简单遍历 ai_project_os_mcp 目录
    source_dir = os.path.join(project_root, "ai_project_os_mcp")
    
    if not os.path.exists(source_dir):
        return {"error": "Source directory not found"}
        
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root).replace("\\", "/")
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # 查找 import
                imports = []
                for line in content.splitlines():
                    match = re.match(r"^(?:from|import)\s+([\w\.]+)", line)
                    if match:
                        imports.append(match.group(1))
                
                dependencies[rel_path] = imports
                
    return {
        "dependencies": dependencies
    }
