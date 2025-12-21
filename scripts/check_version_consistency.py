#!/usr/bin/env python3
"""
版本一致性检查脚本

该脚本用于检查AI Project OS MCP的版本一致性，确保：
1. pyproject.toml 中的版本
2. __init__.py 中的版本
3. mcp-registry.yaml 中的版本
保持一致
"""

import os
import sys
import toml
import yaml


def get_pyproject_version(pyproject_path):
    """从pyproject.toml获取版本号"""
    try:
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            pyproject_data = toml.load(f)
        return pyproject_data['project']['version']
    except Exception as e:
        print(f"ERROR: 无法读取pyproject.toml版本: {e}")
        return None


def get_init_version(init_path):
    """从__init__.py获取版本号"""
    try:
        with open(init_path, 'r', encoding='utf-8') as f:
            init_content = f.read()
        for line in init_content.splitlines():
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
        return None
    except Exception as e:
        print(f"ERROR: 无法读取__init__.py版本: {e}")
        return None


def get_registry_version(registry_path):
    """从mcp-registry.yaml获取版本号"""
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry_data = yaml.safe_load(f)
        return registry_data['version']
    except Exception as e:
        print(f"ERROR: 无法读取mcp-registry.yaml版本: {e}")
        return None


def main():
    """主函数"""
    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # 定义文件路径
    pyproject_path = os.path.join(project_root, 'pyproject.toml')
    init_path = os.path.join(project_root, 'ai_project_os_mcp', '__init__.py')
    registry_path = os.path.join(project_root, 'mcp-registry.yaml')
    
    # 检查文件是否存在
    for file_path in [pyproject_path, init_path, registry_path]:
        if not os.path.exists(file_path):
            print(f"ERROR: 文件不存在: {file_path}")
            return 1
    
    # 获取版本号
    pyproject_version = get_pyproject_version(pyproject_path)
    init_version = get_init_version(init_path)
    registry_version = get_registry_version(registry_path)
    
    if not all([pyproject_version, init_version, registry_version]):
        print("ERROR: 无法获取所有文件的版本号")
        return 1
    
    # 打印版本信息
    print("版本检查结果:")
    print(f"pyproject.toml: {pyproject_version}")
    print(f"__init__.py:     {init_version}")
    print(f"mcp-registry.yaml: {registry_version}")
    print()
    
    # 检查版本一致性
    versions = {
        'pyproject.toml': pyproject_version,
        '__init__.py': init_version,
        'mcp-registry.yaml': registry_version
    }
    
    unique_versions = set(versions.values())
    
    if len(unique_versions) == 1:
        print("✅ 所有文件版本一致")
        return 0
    else:
        print("❌ 版本不一致!")
        for file_name, version in versions.items():
            if version != next(iter(unique_versions)):
                print(f"   {file_name} 版本不匹配: {version}")
        return 1


if __name__ == "__main__":
    sys.exit(main())