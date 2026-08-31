from transformers import BertTokenizer, BertForTokenClassification
from transformers import pipeline

import stanza

sisendkaust="../data/plaintext/"
vastustekaust="../data/detail/"

import sys
import os

def yhenda(st, bo, tunnus="ner1"):
  olemid=[]
  tyyp="-"
  algus=-1
  ots=-1
  for b in bo:
    if b["entity"][0]=="B" and b["word"][0]!="#":
      if tyyp!="-": olemid.append([tyyp, algus, ots])
      tyyp=b["entity"]
      algus=b["start"]
      ots=b["end"]
    if b["entity"][0]=="B" and b["word"][0]=="#":
      ots=b["end"]
    if b["entity"][0]=="I":
       if tyyp[1:]!=b["entity"][1:]: 
         if b["end"]-algus<25:
           ots=b["end"]           
       else:
         ots=b["end"]
  if tyyp!="-": olemid.append([tyyp, algus, ots])
  if not olemid: return st
  onr=0
  sees=False
  for sona in st:
    while olemid[onr][2]<sona["start_char"]: 
      onr+=1
      if onr==len(olemid): break
    if onr==len(olemid): break
    if sona["start_char"]==olemid[onr][1] or \
       not sees and sona["start_char"]>olemid[onr][1]\
                and sona["start_char"]<olemid[onr][2]: 
      sees=True
      sona[tunnus]=olemid[onr][0]
    elif sees and sona["start_char"]<=olemid[onr][2]:
      sona[tunnus]="I"+olemid[onr][0][1:]
    if sona["end_char"]>=olemid[onr][2]: 
        sees=False
        onr+=1
        if onr==len(olemid): break
  return st

os.makedirs(vastustekaust, exist_ok=True)
stanza_nlp=stanza.Pipeline('et', use_gpu=False, processors="tokenize,pos,lemma")
tokenizer = BertTokenizer.from_pretrained('tartuNLP/EstBERT_NER')
bertner = BertForTokenClassification.from_pretrained('tartuNLP/EstBERT_NER')
bert_nlp = pipeline("ner", model=bertner, tokenizer=tokenizer)


tokenizer = BertTokenizer.from_pretrained('tartuNLP/EstBERT_NER_v2')
bertner = BertForTokenClassification.from_pretrained('tartuNLP/EstBERT_NER_v2')
bert_nlp2 = pipeline("ner", model=bertner, tokenizer=tokenizer)

import os
fnimed=os.listdir(sisendkaust)
fnimed.sort()

def main():
 for fnimi in fnimed:
  print(fnimi)
# try:
  fsisu=open(sisendkaust+fnimi, encoding="utf-8").read()
  dok=stanza_nlp(fsisu)
  with open(vastustekaust+fnimi, "w", encoding="utf-8") as f2:
   print(";".join(["file", "sent_id", "word_id", "word", "lemma", "upos", "xpos", "ner_tag", "nertag2"]), file=f2)
   lause_id=0
   for lause in dok.sentences:
    lause_id+=1
    stlause=stanza_nlp(lause.text).to_dict()[0]
    olemid=bert_nlp(lause.text)
    olemid2=bert_nlp2(lause.text)
    yhenda(stlause, olemid, "ner1")
    yhenda(stlause, olemid2, "ner2")
    for word in stlause:
      sona_andmed = "\n".join([f'{fnimi};{str(lause_id)};{word["id"]};{word["text"]};{word["lemma"]};{word["upos"]};{word["xpos"] if "xpos" in word else "?"};{word["ner1"] if "ner1" in word else "O"};{word["ner2"] if "ner2" in word else "O"}'])
      print(sona_andmed, file=f2)
# except Exception as ex:
#   print(ex, fnimi)

if __name__=="__main__":
  main()