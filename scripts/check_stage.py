import os
import json
import sys

VALID_STAGES = ["S1", "S2", "S3", "S4", "S5"]
DEFAULT_STAGE = "S1"

def check():
    if not os.path.exists("state.json"):
        print("state.json 未找到，正在创建默认 state.json（stage=S1）")
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump({"stage": DEFAULT_STAGE}, f)
    
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