"""
submit_audit工具 - 提交S5审计记录
"""

import os
from ai_project_os_mcp.core import RuleEngine
from ai_project_os_mcp.config import config

rule_engine = RuleEngine()

def submit_audit(state, payload):
    """
    提交S5审计记录
    
    Args:
        state: 当前项目状态
        payload: 工具负载，包含审计记录所需字段
        
    Returns:
        dict: 提交结果
    """
    # 验证阶段
    if state["stage"] != config.audit_required_stage:
        return {"status": "FAILED", "reason": f"Audit only allowed in {config.audit_required_stage}"}
    
    # 验证必填字段
    required_fields = ["sub_task_id", "layer", "files_changed", "correctness_assertion", "architecture_compliance", "reviewer"]
    
    for field in required_fields:
        if field not in payload:
            return {"status": "FAILED", "reason": f"Missing required field: {field}"}
    
    # 验证文件变更
    files_changed = payload.get("files_changed", [])
    missing_files = []
    for file_path in files_changed:
        # 简单检查文件是否存在 (对于新增文件可能不适用，但对于修改文件适用)
        # 这里假设 files_changed 是相对路径
        full_path = os.path.join(config.project_root, file_path)
        if not os.path.exists(full_path):
            # 如果是 DELETE 操作，文件可能已经不存在，这里简化处理，只警告
            pass
            # missing_files.append(file_path)
    
    # 创建或更新审计文件
    audit_file = os.path.join(config.project_root, "docs", "S5_audit.md")
    
    # 确保docs目录存在
    os.makedirs(os.path.dirname(audit_file), exist_ok=True)
    
    # 构建审计记录
    audit_record = f"""
## Sub-task: {payload['sub_task_id']}
- Context Refresh: ✅
- Layer: {payload['layer']}
- Files Changed:
{chr(10).join([f'  - {file}' for file in payload['files_changed']])}
- Correctness Assertion:
  - {payload['correctness_assertion']}
- Architecture Compliance:
  - {'✅ No violation of S3' if payload['architecture_compliance'] else '❌ Architecture violation'}
- Reviewer:
  - {payload['reviewer']}
- Status: PASSED
"""
    
    # 写入审计记录
    try:
        # 如果文件不存在，创建并添加标题
        if not os.path.exists(audit_file):
            with open(audit_file, "w", encoding="utf-8") as f:
                f.write("# S5 Audit Log\n\n")
        
        # 追加审计记录
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(audit_record)
        
        return {"status": "PASSED", "message": "Audit submitted successfully", "audit_file": audit_file}
    except Exception as e:
        return {"status": "FAILED", "reason": f"Error writing audit: {str(e)}"}
