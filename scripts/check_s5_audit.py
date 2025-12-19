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

    # src 被修改，必须同时修改 S5_audit.md
    audit_file = "docs/S5_audit.md"
    audit_changed = any(f == audit_file for f in changed_files)

    if not audit_changed:
        print(f"❌ FATAL: src modified in S5 without updating {audit_file}")
        print("👉 请在本次提交中同时更新 S5 审计日志")
        sys.exit(1)

    print("✅ S5 Audit check passed")

if __name__ == "__main__":
    main()