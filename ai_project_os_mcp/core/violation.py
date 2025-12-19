"""
违反处理 - Hard Refusal
"""

class Violation(Exception):
    """
    规则违反异常
    """
    
    def __init__(self, rule_id, message):
        """
        初始化违反异常
        
        Args:
            rule_id: 违反的规则ID
            message: 违反原因
        """
        self.rule_id = rule_id
        self.message = message
        super().__init__(f"MCP Violation ({rule_id}): {message}")

class HardRefusal:
    """
    硬拒绝处理器，处理规则违反情况
    """
    
    def __init__(self):
        """
        初始化硬拒绝处理器
        """
        self.violation_count = 0
    
    def refuse(self, rule_id, message):
        """
        执行硬拒绝
        
        Args:
            rule_id: 违反的规则ID
            message: 违反原因
            
        Raises:
            Violation: 规则违反异常
        """
        self.violation_count += 1
        raise Violation(rule_id, message)
    
    def get_violation_count(self):
        """
        获取违反计数
        
        Returns:
            int: 违反计数
        """
        return self.violation_count
    
    def reset_violation_count(self):
        """
        重置违反计数
        """
        self.violation_count = 0
