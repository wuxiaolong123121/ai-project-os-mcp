"""
freeze_stage工具 - 冻结项目到下一个阶段
"""

from ai_project_os_mcp.core import RuleEngine
from ai_project_os_mcp.core.violation import HardRefusal

rule_engine = RuleEngine()
hard_refusal = HardRefusal()

def freeze_stage(state, payload):
    """
    冻结项目到下一个阶段
    
    Args:
        state: 当前项目状态
        payload: 工具负载，包含target_stage字段
        
    Returns:
        dict: 冻结结果
    """
    target_stage = payload.get("target_stage")
    
    if not target_stage:
        return {"success": False, "error": "Missing target_stage"}
    
    # 验证阶段转换
    is_valid, reason = rule_engine.validate_stage_transition(state["stage"], target_stage)
    
    if not is_valid:
        return {"success": False, "error": reason}
    
    # 更新状态
    new_state = state.copy()
    new_state["stage"] = target_stage
    new_state["frozen"] = True
    
    return {
        "success": True,
        "new_stage": target_stage,
        "new_state": new_state
    }
