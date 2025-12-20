import os
import sys

def setup_pre_commit():
    # 设置 Git pre-commit 钩子，自动触发规则检查
    # 检查是否在 Git 仓库中
    if not os.path.exists(".git"):
        print("❌ 错误：当前目录不是 Git 仓库，请先执行 git init")
        return False
    
    # 创建 pre-commit 钩子文件
    pre_commit_path = os.path.join(".git", "hooks", "pre-commit")
    
    # 使用三引号定义内容，避免转义字符混乱
    pre_commit_content = """#!/bin/sh
echo "🔍 AI Project OS: Running pre-commit guards..."

python scripts/check_stage.py || exit 1
python scripts/guard_src.py || exit 1
python scripts/check_context_refresh.py || exit 1
python scripts/check_s5_audit.py || exit 1
python scripts/check_dependencies.py || exit 1

echo "✅ All AI Project OS checks passed."
"""
    
    try:
        with open(pre_commit_path, "w", encoding="utf-8") as f:
            f.write(pre_commit_content)
        
        # 在 Windows 上，我们可以使用 git bash 或 WSL 来运行 chmod
        # 这里我们添加说明，让用户手动执行
        print(f"✅ pre-commit 钩子文件已创建：{pre_commit_path}")
        print("📋 请在 Git Bash 或 WSL 中运行以下命令以赋予执行权限：")
        print("   chmod +x .git/hooks/pre-commit")
        print("📋 或者在 Windows 上，您可以使用 PowerShell 运行：")
        # 使用单引号包裹，避免内部双引号转义问题
        print('   icacls .git/hooks/pre-commit /grant:r "$env:USERNAME":(RX)')
        return True
    except Exception as e:
        print(f"❌ 创建 pre-commit 钩子失败：{e}")
        return False

if __name__ == "__main__":
    setup_pre_commit()
