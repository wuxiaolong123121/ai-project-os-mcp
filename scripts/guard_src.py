import json 
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