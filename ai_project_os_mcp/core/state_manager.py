"""
状态管理器 - state.json 权威读写
"""

import json
import os
from datetime import datetime

class StateManager:
    """
    管理项目状态，确保状态的一致性和权威性
    """
    
    def __init__(self, project_root="."):
        """
        初始化状态管理器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.state_file = os.path.join(project_root, "state.json")
        self._ensure_state_file_exists()
    
    def _ensure_state_file_exists(self):
        """
        确保状态文件存在，如果不存在则创建默认状态
        """
        if not os.path.exists(self.state_file):
            default_state = {
                "stage": "S1",
                "frozen": False,
                "locked": False,
                "last_updated": datetime.now().isoformat(),
                "version": "0.1"
            }
            self.save_state(default_state)
    
    def load_state(self):
        """
        加载当前项目状态
        
        Returns:
            dict: 项目状态字典
        """
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_state(self, state):
        """
        保存项目状态
        
        Args:
            state: 项目状态字典
        """
        # 更新最后修改时间
        state["last_updated"] = datetime.now().isoformat()
        
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def update_state(self, updates):
        """
        更新项目状态的部分字段
        
        Args:
            updates: 要更新的状态字段字典
            
        Returns:
            dict: 更新后的完整状态
        """
        state = self.load_state()
        state.update(updates)
        self.save_state(state)
        return state
