import json 
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