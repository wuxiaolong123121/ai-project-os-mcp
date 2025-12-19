"""
Configuration management for AI Project OS MCP Server.
"""

import os
import yaml

class Config:
    """
    MCP Server Configuration
    """
    
    def __init__(self):
        self.project_root = os.getenv("MCP_PROJECT_ROOT", ".")
        self.config_path = os.getenv("MCP_CONFIG_PATH", "config.yaml")
        self.log_level = os.getenv("MCP_LOG_LEVEL", "INFO")
        
        # Load defaults
        self.name = "ai-project-os-mcp"
        self.version = "0.1"
        self.rules = {
            "R1": "AI MUST query current stage before any action",
            "R2": "AI MUST NOT generate code unless stage == S5",
            "R3": "AI MUST abort on architecture violation",
            "R4": "AI MUST submit audit for every S5 task",
            "R5": "AI MUST respect src guard and lock status"
        }
        self.violation_policy = "hard_refusal"
        self.audit_required_stage = "S5"
        
        # Load from file if exists
        self._load_from_file()
    
    def _load_from_file(self):
        """
        Load configuration from YAML file
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                    if config_data:
                        self._update_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")
    
    def _update_from_dict(self, data):
        """
        Update configuration from dictionary
        """
        if "server" in data:
            self.name = data["server"].get("name", self.name)
        if "mcp_version" in data:
            self.version = data.get("mcp_version", self.version)
        if "rules" in data:
            # Convert list of dicts to dict if needed, or just replace
            if isinstance(data["rules"], list):
                self.rules = {r["id"]: r["description"] for r in data["rules"]}
            elif isinstance(data["rules"], dict):
                self.rules = data["rules"]
        if "enforcement" in data:
            self.violation_policy = data["enforcement"].get("violation_policy", self.violation_policy)
            self.audit_required_stage = data["enforcement"].get("audit_required_stage", self.audit_required_stage)

# Global config instance
config = Config()
