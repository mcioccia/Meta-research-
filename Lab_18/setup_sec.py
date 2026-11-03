"""Configure the SEC identity locally; never commit it.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"buffett-sec-review"/"scripts"))
from sec_facts import NOTICE,read_identity
print(NOTICE)
name=input("Your name for SEC requests: ").strip()
email=input("Your email for SEC requests: ").strip()
os.environ["SEC_USER_AGENT"]=name+" "+email
identity=read_identity(ROOT/".local"/"sec_identity.json")
target=ROOT/".local"/"sec_identity.json"
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({"ai_disclosure":NOTICE,"user_agent":identity},indent=2),encoding="utf-8")
print("Saved local SEC settings. This folder is excluded from Git.")
print("Next: python buffett-sec-review/scripts/sec_facts.py COST --root .")

