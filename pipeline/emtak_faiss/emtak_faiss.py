import os
import json
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
ROOT = Path(__file__).resolve().parents[2]
sisendkaust=ROOT / "data/plaintext"
valjundkaust=ROOT / "data/emtak_faiss"
os.makedirs(valjundkaust, exist_ok=True)

if not os.environ.get("OPENAI_API_KEY"):
  raise RuntimeError(
      "OPENAI_API_KEY is required for the EMTAK embedding stage. "
      "Set it in the environment; do not store it in this repository."
  )

embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
faiss_index = FAISS.load_local(
    str(Path(__file__).resolve().parent),
    embedding_model,
    allow_dangerous_deserialization=True,
)

import os
fnimed=os.listdir(sisendkaust)
fnimed.sort()

def main():
 for fnimi in fnimed:
  print(fnimi) 
  try:
   fsisu=(sisendkaust / fnimi).read_text(encoding="utf-8")
   results = faiss_index.similarity_search_with_score(fsisu, k=30)
   koodid=[{"kood":doc.metadata["code"], "skoor":score.item()}for (doc, score) in results]
   print(len(results), flush=True)
   with open(valjundkaust / fnimi, "w", encoding="utf-8") as f2:
    print(koodid, file=f2)
  except Exception as ex:
   print("probleem", fnimi, ex)

if __name__=="__main__":
  main()
