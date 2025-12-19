"""
Verification Tools - 验证项目状态
"""

import subprocess
import os
from ai_project_os_mcp.config import config

def run_tests(state, payload):
    """
    运行项目测试
    
    Args:
        state: 当前项目状态
        payload: 工具负载 (可选包含 test_path)
        
    Returns:
        dict: 测试结果
    """
    test_path = payload.get("test_path", "tests")
    
    # 简单使用 pytest
    try:
        # 确保在项目根目录运行
        cwd = config.project_root
        
        # 构建命令
        cmd = ["pytest", test_path]
        
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60 # 1分钟超时
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
