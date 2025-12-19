"""
Tests for RuleEngine
"""

import unittest
from ai_project_os_mcp.core.rule_engine import RuleEngine

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine()
        
    def test_validate_context_refresh(self):
        valid_code = "# ...\n[Context Refresh]\n# ..."
        invalid_code = "# Just some code"
        
        self.assertTrue(self.engine.validate_context_refresh(valid_code)[0])
        self.assertFalse(self.engine.validate_context_refresh(invalid_code)[0])
        
    def test_validate_pseudo_tdd(self):
        valid_code_1 = "# 正确性断言: should work"
        valid_code_2 = "assert result == True"
        invalid_code = "print('hello')"
        
        self.assertTrue(self.engine.validate_pseudo_tdd(valid_code_1)[0])
        self.assertTrue(self.engine.validate_pseudo_tdd(valid_code_2)[0])
        self.assertFalse(self.engine.validate_pseudo_tdd(invalid_code)[0])
        
    def test_is_architecture_violation(self):
        # Test allowed directory
        action_allowed = {"file_path": "ai_project_os_mcp/core/new_file.py"}
        self.assertFalse(self.engine.is_architecture_violation(action_allowed)[0])
        
        # Test disallowed directory
        action_disallowed = {"file_path": "forbidden_dir/file.py"}
        self.assertTrue(self.engine.is_architecture_violation(action_disallowed)[0])
        
        # Test dependency violation (core importing tools)
        action_dep_violation = {
            "file_path": "ai_project_os_mcp/core/logic.py",
            "content": "from ai_project_os_mcp.tools import get_stage"
        }
        self.assertTrue(self.engine.is_architecture_violation(action_dep_violation)[0])
        
        # Test allowed dependency
        action_dep_allowed = {
            "file_path": "ai_project_os_mcp/tools/my_tool.py",
            "content": "from ai_project_os_mcp.core import RuleEngine"
        }
        self.assertFalse(self.engine.is_architecture_violation(action_dep_allowed)[0])

if __name__ == "__main__":
    unittest.main()
