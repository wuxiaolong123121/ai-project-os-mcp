import subprocess 
import sys 
import json 
import os 

def get_changed_files():
    # 获取本次提交中变更的文件
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.splitlines()

def has_context_refresh():
    # 检查提交内容中是否包含 [Context Refresh]
    result = subprocess.run(
        ["git", "diff", "--cached"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return "[Context Refresh]" in result.stdout

def main():
    # 读取项目状态
    if not os.path.exists("state.json"):
        print("❌ state.json not found")
        sys.exit(1)

    with open("state.json", "r", encoding="utf-8") as f:
        state = json.load(f)

    stage = state.get("stage")

    # 只在 S5 阶段强制
    if stage != "S5":
        sys.exit(0)

    changed_files = get_changed_files()

    # 是否涉及 src 目录
    touched_src = any(f.startswith("src/") for f in changed_files)

    if not touched_src:
        sys.exit(0)

    # src 被修改，必须有 Context Refresh
    if not has_context_refresh():
        print("❌ FATAL: src modified in S5 without [Context Refresh]")
        print("👉 请在本次提交中添加 Context Refresh 声明")
        sys.exit(1)

    print("✅ Context Refresh check passed")

if __name__ == "__main__":
    main()