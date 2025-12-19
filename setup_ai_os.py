import os
import json
import sys
import datetime
import subprocess

# --- 项目配置 ---
PROJECT_NAME = "ai-project-os-vibe-edition"
DIRS = [
    "prompts",
    "docs",
    "src",
    "logs",
    "scripts",
    "vibe",
    "examples"
]

# --- 核心文件定义 ---
FILES = {}

# 1. 5S 母 Prompt
FILES[os.path.join("prompts", "mother_prompt.md")] = """# AI 项目「母 Prompt」· 5S 自动流程总控版 (Vibe 增强)

你现在扮演的是一个【可交付软件项目执行系统】，遵循工程纪律高于一切。

## 【绝对铁律】
1. 严格按 **5S 流程** 执行：S1 -> S2 -> S3 -> S4 -> S5。
2. 上一阶段未冻结，不得进入下一阶段。
3. S5 阶段前禁止生成任何业务代码到 `src/`。
4. 决策权归用户，执行权归你。

## 【5S 流程】
- **S1 Scope**: 定义“做什么/不做什么”，输出 `docs/S1_scope.md`。
- **S2 Spec**: 需求规格化，输出 `docs/S2_spec.md`。
- **S3 Structure**: 架构冻结（UI/Workflow/Domain/Infra），输出 `docs/S3_structure.md`。
- **S4 Schedule**: 任务原子化分解，输出 `docs/S4_tasks.md`。
- **S5 Ship**: 实现与审计，输出代码及 `docs/S5_audit.md`。

## 【Vibe 集成（受控）】
你仅可在以下情况下参考 vibe/ 目录内容：
- 当前阶段已冻结
- 不影响既有 S1/S2/S3 决策
- 仅用于表达、示例或可读性优化

任何试图用 Vibe 绕过冻结阶段的行为，视为违规。
"""

# 2. S5 代码规则
FILES[os.path.join("prompts", "s5_code_rules.md")] = """# S5 阶段代码强约束规则

## 1. 记忆重载 (Context Refresh)
每项子任务开始前必须声明：
[Context Refresh]
- Sub-task ID: 
- Layer: 
- Forbidden Constraints: 

## 2. 变更熔断 (Change Fuse)
发现架构不足以支撑实现时，必须停止并请求回滚 S3，禁止 Dirty Hack。

## 3. 伪 TDD
写代码前必须在注释中声明正确性断言。
"""

# 3. Vibe 整合规则
FILES[os.path.join("prompts", "vibe_usage_rules.md")] = """# Vibe Coding x 5S 工程协作规范

## 1. 权责总表
- 项目目标/架构/任务拆分：5S 体系主导。
- 代码表达/交互/灵感：Vibe Coding 辅助。

## 2. 核心冲突解决
当“感觉（Vibe）”与“结构（Structure）”冲突时，架构铁律拥有最高裁决权。禁止为了追求简洁而破坏 Domain 层的纯粹性。

## 3. 降级原则（Mandatory）
Vibe Coding 仅可用于：
- S2 文案润色
- S4 任务描述清晰化
- S5 代码可读性与命名优化

禁止用于：
- Scope 决策
- 架构设计
- 绕过冻结阶段
"""

# 4. 自动化脚本 - 阶段检查
FILES[os.path.join("scripts", "check_stage.py")] = """import json
import sys

VALID_STAGES = ["S1", "S2", "S3", "S4", "S5"]

def check():
    with open("state.json", "r", encoding="utf-8") as f:
        state = json.load(f)
    
    stage = state.get("stage")
    if stage not in VALID_STAGES:
        print(f"❌ Invalid stage value: {stage}")
        sys.exit(1)
    
    print(f"Current Stage: {stage}")
    return stage

if __name__ == "__main__":
    check()
"""

# 5. 自动化脚本 - 冻结工具
FILES[os.path.join("scripts", "freeze_stage.py")] = """import json 
import sys 
import datetime 

VALID_STAGES = ["S1", "S2", "S3", "S4", "S5"] 

if len(sys.argv) != 2:
    print("Usage: python freeze_stage.py S[1-5]")
    sys.exit(1)

next_stage = sys.argv[1]

if next_stage not in VALID_STAGES:
    print(f"❌ Invalid stage: {next_stage}")
    sys.exit(1)

with open("state.json", "r", encoding="utf-8") as f:
    state = json.load(f)

current_stage = state.get("stage")

if VALID_STAGES.index(next_stage) < VALID_STAGES.index(current_stage):
    print(f"❌ Cannot rollback stage via freeze. Current: {current_stage}")
    sys.exit(1)

if VALID_STAGES.index(next_stage) > VALID_STAGES.index(current_stage) + 1:
    print(f"❌ Cannot skip stages. Current: {current_stage}, Target: {next_stage}")
    sys.exit(1)

state["stage"] = next_stage
state["frozen"] = True
state["last_updated"] = datetime.datetime.now().isoformat()

with open("state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print(f"🔒 Stage successfully frozen at {next_stage}")
"""

# 6. 自动化脚本 - 目录保护
FILES[os.path.join("scripts", "guard_src.py")] = """import json 
import os 
import sys 

with open("state.json", "r", encoding="utf-8") as f:
    state = json.load(f) 

stage = state.get("stage") 
locked = state.get("locked", False) 

if stage != "S5" and os.path.exists("src") and os.listdir("src"):
    print("❌ FATAL: Business code detected in 'src' before S5 stage.")
    sys.exit(1) 

if stage == "S5" and locked:
    print("❌ FATAL: src is locked after S5 audit freeze.")
    sys.exit(1)
"""

# 7. 自动化脚本 - Context Refresh 检查
FILES[os.path.join("scripts", "check_context_refresh.py")] = """import subprocess 
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
"""

# 8. 自动化脚本 - S5 Audit 检查
FILES[os.path.join("scripts", "check_s5_audit.py")] = """import subprocess 
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
"""

# 8. 自动化脚本 - 设置 pre-commit 钩子
FILES[os.path.join("scripts", "setup_pre_commit.py")] = """import os
import sys

def setup_pre_commit():
    # 设置 Git pre-commit 钩子，自动触发规则检查
    # 检查是否在 Git 仓库中
    if not os.path.exists(".git"):
        print("❌ 错误：当前目录不是 Git 仓库，请先执行 git init")
        return False
    
    # 创建 pre-commit 钩子文件
    pre_commit_path = os.path.join(".git", "hooks", "pre-commit")
    pre_commit_content = "#!/bin/sh
echo \"🔍 AI Project OS: Running pre-commit guards...\"\n\npython scripts/check_stage.py || exit 1\npython scripts/guard_src.py || exit 1\npython scripts/check_context_refresh.py || exit 1\npython scripts/check_s5_audit.py || exit 1\n\necho \"✅ All AI Project OS checks passed.\"\n"
    
    try:
        with open(pre_commit_path, "w", encoding="utf-8") as f:
            f.write(pre_commit_content)
        
        # 在 Windows 上，我们可以使用 git bash 或 WSL 来运行 chmod
        # 这里我们添加说明，让用户手动执行
        print(f"✅ pre-commit 钩子文件已创建：{pre_commit_path}")
        print("📋 请在 Git Bash 或 WSL 中运行以下命令以赋予执行权限：")
        print("   chmod +x .git/hooks/pre-commit")
        print("📋 或者在 Windows 上，您可以使用 PowerShell 运行：")
        print("   icacls .git/hooks/pre-commit /grant:r \"$env:USERNAME\":(RX)")
        return True
    except Exception as e:
        print(f"❌ 创建 pre-commit 钩子失败：{e}")
        return False

if __name__ == "__main__":
    setup_pre_commit()
"""

# 9. GitHub CI 配置文件
FILES[os.path.join(".github", "workflows", "ai-guard.yml")] = """name: AI Project OS Guard

on:
  push:
  pull_request:

jobs:
  guard:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Run stage check
        run: python scripts/check_stage.py

      - name: Run src guard
        run: python scripts/guard_src.py

      - name: Run context refresh check
        run: python scripts/check_context_refresh.py

      - name: Run S5 audit check
        run: python scripts/check_s5_audit.py
"""

# 10. 初始 S5 Audit 文件
FILES["docs/S5_audit.md"] = """# S5 Audit Log

## 初始状态
- 项目刚进入 S1 阶段，尚未开始 S5 实现
- 审计日志将在 S5 阶段开始后记录

## 审计规则
> **No Audit, No Ship.**

S5 阶段修改 `src/` 目录时，必须同时更新此文件：
1. 每条记录对应一个子任务
2. 必须包含 Context Refresh 状态
3. 必须记录修改的文件
4. 必须包含正确性断言
5. 必须确认架构合规性
"""

# 11. 非技术用户示例文档
FILES["examples/example-no-code.md"] = """# Example：0 技术用户如何用 AI Project OS 从想法到可交付项目 
 
 > 本示例面向 **完全不懂代码的人**。 
 > 你不需要理解编程语言、框架或架构，只需要会做决定。 

 --- 

 ## 一、背景设定（你是谁？） 

 假设你是这样的人： 

 * 不会写代码 
 * 用过 ChatGPT / 豆包 / Claude 
 * 有一个模糊想法，但每次让 AI 写代码都会失控 

 你的目标不是“学习编程”，而是： 

 > **让 AI 在不失控的情况下，帮你交付一个能用的项目。** 

 --- 

 ## 二、你的原始想法（非常模糊也没关系） 

 > 我想要一个工具，能把一段文字整理成结构化文档。 

 注意： 

 * 这不是需求文档 
 * 这甚至不算清楚 
 * **但这已经足够启动 AI Project OS** 

 --- 

 ## 三、你做的第一件事（只做这一件） 

 ### 1️⃣ 初始化项目 

 ```bash 
 git init 
 python setup_ai_os.py 
 python scripts/setup_pre_commit.py 
 ``` 

 你不需要理解这些命令在干什么，只需要知道： 

 * 项目结构已生成 
 * 规则已安装 
 * AI 之后会被“管住” 

 --- 

 ## 四、你如何与 AI 对话（关键） 

 你**不会**直接说： 

 > 帮我写代码 

 你**只会做一件事**： 

 👉 把 `prompts/mother_prompt.md` 整份贴给 AI 

 然后对 AI 说一句话： 

 > 我们现在开始 S1，请你等我给 Scope。 

 --- 

 ## 五、S1：你只需要回答 3 个问题（不会写也行） 

 AI 会问你： 

 ### Q1：你想做什么？ 

 你回答： 

 > 把一段混乱的文字，整理成结构清楚的文档。 

 ### Q2：你明确不想做什么？ 

 你回答： 

 > 不做网页 
 > 不做复杂功能 
 > 不接数据库 

 ### Q3：什么情况下你觉得“成功”？ 

 你回答： 

 > 我复制一段文字进去，它能直接给我一份不用重写的文档。 

 ⚠️ 注意： 

 * 没有对错 
 * 不需要专业 
 * **这是决策，不是设计** 

 --- 

 ## 六、AI 会替你做什么？ 

 AI 会根据你的话，生成一个文件： 

 ``` 
 docs/S1_scope.md 
 ``` 

 里面是： 

 * 明确的边界 
 * 明确的“不做事项” 
 * 明确的成功定义 

 你只做一件事： 

 👉 看一眼，判断一句话： 

 > 这是不是我想要的？ 

 如果是，你回复： 

 > 冻结 S1 

 然后运行： 

 ```bash 
 python scripts/freeze_stage.py S1 
 ``` 

 ⚠️ 从这一刻起： 

 > **AI 不能再改 S1，这是工程事实。** 

 --- 

 ## 七、接下来的 S2 / S3 / S4 你在干什么？ 

 ### 你以为你要： 

 * 想清楚需求 
 * 设计系统 
 * 拆任务 

 ### 实际上你只需要： 

 * 判断： 

   * 「这样对吗？」 
   * 「我接不接受？」 

 AI 负责： 

 * 写文档 
 * 提方案 
 * 拆任务 

 你负责： 

 * 点头 or 否定 

 每一阶段都一样： 

 > **AI 提案 → 你判断 → 冻结** 

 --- 

 ## 八、什么时候才会真的写代码？ 

 👉 **只有在 S5**。 

 在此之前： 

 * AI 想写代码 → 会被规则拦截 
 * 不小心写了 → Git 不让提交 

 这一步解决了一个核心问题： 

 > **你再也不会“被迫接收一坨你看不懂的代码”。** 

 --- 

 ## 九、S5 时，你依然不用懂代码 

 在 S5，每一个 AI 子任务必须： 

 * 声明它在干什么（Context Refresh） 
 * 说明什么情况下算“对”（Pseudo-TDD） 
 * 记录到 `docs/S5_audit.md` 

 你只看三件事： 

 1. 它有没有解释自己在干什么 
 2. 它有没有说清楚“对”的标准 
 3. 有没有留下审计记录 

 如果有： 

 > 你接受 

 如果没有： 

 > 提交会被系统拦截 

 --- 

 ## 十、最终你得到的是什么？ 

 你得到的不是： 

 * 一堆神秘代码 

 而是： 

 * 一个你**全过程做过决策**的项目 
 * 一个每一步都有记录的工程 
 * 一个你可以交付、回溯、维护的成果 

 --- 

 ## 十一、一句话总结 

 > **AI Project OS 的作用不是教你写代码，** 
 > **而是让你在不懂代码的情况下，依然能主导一个真实项目。** 

 如果你能做决策，你就能用这个系统。 
"""

# 12. Vibe 目录说明文件
FILES["vibe/README.md"] = """# Vibe Coding 资源说明

## 资源内容

本目录包含 Vibe Coding 相关的参考资源，用于：
- Prompt 表达参考
- 示例阅读
- 文案与代码可读性优化

## 重要说明

⚠️ **降级原则（Mandatory）**

vibe-coding-cn 为自动下载的参考资源，**不具备任何决策、架构或流程控制权**。

### 允许使用场景
- ✅ S2 文案润色
- ✅ S4 任务描述清晰化
- ✅ S5 代码可读性与命名优化

### 禁止使用场景
- ❌ Scope 决策（S1）
- ❌ 需求定义（S2）
- ❌ 架构设计（S3）
- ❌ 绕过冻结阶段
- ❌ 作为母 Prompt

## 资源管理

### 自动下载
vibe-coding-cn 仓库会在项目初始化时自动下载到 `vibe/vibe-coding-cn/` 目录。

### 手动更新
如需手动更新，可以执行：
```bash
cd vibe/vibe-coding-cn
git pull
```

### 手动下载
如果自动下载失败，可以手动执行：
```bash
git clone https://github.com/tukuaiai/vibe-coding-cn.git vibe/vibe-coding-cn
```

## 合规性

所有使用 Vibe Coding 资源的行为必须服从 5S 冻结体系，
当 Vibe 与 5S 冻结产物冲突时，以 5S 冻结产物为准。
"""

# 11. 初始状态
FILES["state.json"] = json.dumps({
    "stage": "S1",
    "frozen": False,
    "last_updated": datetime.datetime.now().isoformat()
}, indent=2)

# 8. README
FILES["README.md"] = """# AI Project OS – Vibe × 5S Engineering (v1.2)

## 🌟 工程级 AI 自动编程治理系统

> 本系统并不要求你会写代码，只要求你愿意按流程做决策。

🎯 这是什么？

这是一个 用于治理 AI 自动编程的工程级操作系统。

目标不是“让 AI 更自由”，
而是 让 AI 在正确的工程边界内把事情一次做对。

🧠 核心理念

决策权永远属于人类

AI 只负责执行被冻结的任务

所有阶段都有物理约束而不是“约定”

🧱 工程结构
.
├─ prompts/        # 工程规则与 Prompt（不可随意修改）
├─ docs/           # 5S 阶段冻结产物（工程事实）
├─ src/            # 仅 S5 阶段可写
├─ scripts/        # 强制约束脚本（流程的“法律”）
├─ vibe/           # Vibe Coding 灵感资产（只读参考，服从 5S 规则）
├─ state.json      # 项目唯一真实状态

🔒 5S 冻结流程

### vibe/ 目录说明：
- 本目录仅用于参考 Prompt 表达与灵感
- 不具备任何流程或决策权
- 永远服从 5S 冻结产物
- 可通过 `git submodule add https://github.com/tukuaiai/vibe-coding-cn.git vibe/vibe-coding-cn` 引入参考资源

🔒 5S 冻结流程
阶段 \t 产物 \t 是否允许写代码
S1 Scope \t 做什么 / 不做什么 \t ❌
S2 Spec \t 可验收需求 \t ❌
S3 Structure \t 架构冻结 \t ❌
S4 Tasks \t 可执行任务 \t ❌
S5 Ship \t 实现 + 审计 \t ✅
🛑 S5 稳定性补丁（Mandatory）

所有 S5 子任务必须：

Context Refresh（显式加载上下文）

Change Fuse（架构不足立即熔断）

Pseudo-TDD（先定义什么叫“对”）

未满足任一条 → 输出无效。

👤 适合谁？

不懂代码，但想主导完整项目的人

用 AI 写代码但项目总是失控的人

想把 vibe coding 升级为工程交付的人

⚠️ 重要说明

S5 冻结不等于项目结束，而是进入稳定维护阶段。

所有 S5 子任务必须包含 [Context Refresh] 标识，否则输出无效。

## 🚀 快速开始（必须）

```bash
# 1. 初始化 Git 仓库
git init

# 2. 运行项目初始化脚本
python setup_ai_os.py

# 3. 安装 pre-commit 钩子（关键：未执行则规则不完整）
python scripts/setup_pre_commit.py
```

⚠️ 重要提示：未执行 `python scripts/setup_pre_commit.py` = 规则不完整，AI 可能会不守规矩。

🔄 自动触发机制

本项目支持两种自动触发规则检查的方式：

1. **本地 Git 提交触发**
   - 已通过 `setup_pre_commit.py` 自动配置
   - 每次 `git commit` 时会自动运行规则检查
   - 违规提交会被直接拦截

2. **GitHub CI 自动触发**
   - 已配置 `.github/workflows/ai-guard.yml` 文件
   - 每次 push 或 PR 时 GitHub 会自动运行规则检查
   - 不合规的代码无法合并到主分支

🎯 自动触发能拦截的违规行为
- S5 之前往 src/ 写代码
- 跳阶段冻结
- S5 锁定后修改代码
- S5 修改 src 未携带 [Context Refresh]
- 其他违反 5S 流程的行为

🔒 S5 锁定机制

S5 阶段完成后，可通过以下方式锁定代码：
- 手动编辑 `state.json` 文件，将 `locked` 字段设为 `true`
- 锁定后，任何对 `src/` 目录的修改都会被自动拦截
- 锁定状态可随时手动解除

🔍 Context Refresh 强制校验

v1.1 新增功能：
- S5 阶段，只要修改 `src/` 目录，提交内容中必须包含 `[Context Refresh]` 声明
- 强制格式：
  ```
  [Context Refresh]
  Sub-task ID: xxx
  Layer: Domain | Workflow | Infra | UI
  Forbidden Constraints: xxx
  ```
- 本地 `git commit` 和 GitHub CI 都会自动检查
- 违规提交会被直接拦截

📋 S5 Audit 强制校验（v1.2 新增）

> **No Audit, No Ship.**

S5 不只是"写完代码"，而是每一个 S5 子任务都必须留下"工程证据"。

- 强制规则：S5 阶段修改 `src/`，必须同时更新 `docs/S5_audit.md`
- 审计文件格式：
  ```md
  # S5 Audit Log

  ## Sub-task: S5-001
  - Context Refresh: ✅
  - Layer: Domain | Workflow | Infra | UI
  - Files Changed:
    - src/domain/user.py
  - Correctness Assertion:
    - Given X, expect Y
  - Architecture Compliance:
    - No violation of S3
  - Reviewer:
    - AI
  - Status: PASSED
  ```
- 检查点：本地 `pre-commit` 和 GitHub CI 双重拦截
- 目的：确保 AI 每一步都留下可审计的工程痕迹

📋 重要说明：
- S5 冻结不等于项目结束，而是进入稳定维护阶段
- 锁定是可选的，但建议在正式交付前执行
- 锁定后仍可通过解除锁定进行必要的维护
- v1.1 adds mandatory Context Refresh enforcement for all S5 code changes. No Context, No Commit.
- v1.2 adds mandatory S5 Audit for all src modifications. No Audit, No Ship.

## ⚠️ 免责声明

本系统不保证代码功能正确性，
仅保证工程流程、决策边界和审计链条的完整性。

本系统的目标是帮助您建立符合工程纪律的 AI 开发流程，
而非替代专业的软件测试和质量保证流程。
- v1.2 adds mandatory S5 Audit for all src modifications. No Audit, No Ship.
"""

def setup_vibe_resources():
    """
    受控下载 vibe-coding-cn 仓库作为只读参考资源
    仅用于 Prompt 表达参考、示例阅读和代码可读性优化
    不具备决策权、架构权和流程控制权
    """
    vibe_dir = os.path.join("vibe", "vibe-coding-cn")
    
    # 检查是否已存在，避免重复下载
    if os.path.exists(vibe_dir):
        print("ℹ️ vibe-coding-cn 已存在，跳过下载")
        return
    
    print("⬇️ 正在下载 vibe-coding-cn (只读参考资源)...")
    os.makedirs("vibe", exist_ok=True)
    
    # 执行 git clone 命令
    repo_url = "https://github.com/tukuaiai/vibe-coding-cn.git"
    cmd = f"git clone {repo_url} {vibe_dir}"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ vibe-coding-cn 下载成功")
    else:
        print(f"⚠️ vibe-coding-cn 下载失败: {result.stderr}")
        print("   您可以手动执行: git clone https://github.com/tukuaiai/vibe-coding-cn.git vibe/vibe-coding-cn")
        print("   下载失败不影响系统核心功能")


def main():
    print(f"正在初始化项目: {PROJECT_NAME}")
    for d in DIRS:
        os.makedirs(d, exist_ok=True)
    
    # 创建 GitHub CI 所需目录
    github_dir = ".github/workflows"
    os.makedirs(github_dir, exist_ok=True)
    
    for path, content in FILES.items():
        # 确保文件所在目录存在
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"已创建文件: {path}")
    
    # 下载 vibe-coding-cn 作为参考资源
    setup_vibe_resources()
    
    print("\n✅ 初始化完成！")
    print("请按照 README.md 开始你的第一个 AI 工程项目。")

if __name__ == "__main__":
    main()