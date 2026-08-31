import os
import json
fnimed=os.listdir("../data/plaintext/")
fnimed.sort()
vasted=json.load(open("../../../andmed/kuupaev_pealkiri/eol.json", encoding="utf-8"))
v={}
for fnimi in fnimed:
  v[fnimi[:-4]]=vasted[fnimi[:-4]]
with open("date_title.json", "w", encoding="utf-8") as f2:
  json.dump(v, f2, ensure_ascii=False, indent=2)