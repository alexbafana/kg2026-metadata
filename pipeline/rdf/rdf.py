import os
import json
import datetime
import numpy as np
import sys
import traceback
import re
import urllib.parse
from collections import defaultdict
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import FOAF , XSD
from rdflib.graph import Collection, BNode

EX = Namespace("http://mkm.ee/schema/")
EKW = Namespace("http://mkm.ee/schema/kw/")
ART = Namespace("http://mkm.ee/article/")
ENT = Namespace("http://mkm.ee/entity/")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCT = Namespace("http://purl.org/dct/terms/")
NLP = Namespace("http://mkm.ee/nlp/")
VER = Namespace("http://mkm.ee/version/")
CLS = Namespace("http://mkm.ee/classification/")
WD = Namespace("http://wikidata.org/wiki/")
MARL = Namespace("http://www.gsi.upm.es/ontologies/marl/ns#") 
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#") 

#artikkel = URIRef("http://mkm.ee/article/20240210_003")
allikas = URIRef("http://mkm.ee/schema/source")
pealkiri = URIRef("http://purl.org/dc/terms/title")
sisu = URIRef("http://mkm.ee/schema/bodyText")
loodud = URIRef("http://purl.org/dc/terms/created")
artiklityyp = URIRef("http://mkm.ee/schema/Article")
seosed = URIRef("http://mkm.ee/schema/mentions")
lemmas_pred = URIRef("http://mkm.ee/nlp/lemmas")

kaust="../data/"
emtakyles=json.load(open("rdf/emtakyles.json"))
olemikoodid=json.load(open("detail_entity/olemikoodid_err_ol.json", encoding="utf-8"))
lemmavasted=json.load(open("rdf/lemmavasted.json", encoding="utf-8"))
koodivasted=json.load(open("rdf/koodivasted.json"))
kppk=json.load(open(kaust+"meta/date_title.json"))


def emtak_gpt(fnimi, valjaanne):
  koht=kaust+"emtak_faiss_gpt/"+valjaanne+"/"+fnimi
  if os.path.exists(koht):
    d=json.load(open(koht, encoding="utf-8"))
    koodid=set()
    for kood in d:
      koodid.add(kood)
      if kood in emtakyles:
        for k2 in emtakyles[kood]: koodid.add(k2)
    return list(koodid)
  return []
  
def emtak_faiss(fnimi):
  koht=kaust+"emtak_faiss/"+fnimi
  if os.path.exists(koht):
    kogused=defaultdict(int)
    fsisu=open(koht).read()
    if fsisu:
     d=eval(fsisu)
     for paar in d:
      kogused[paar["kood"]]+=1
      for k2 in emtakyles[paar["kood"]]: kogused[k2]+=1
     v=[kood for kood in kogused if kogused[kood]>=3]
     return v
  return []
  
def unesco(fnimi, valjaanne, g, artikkel):
  koht=kaust+"unesco_gemet/"+valjaanne+"/"+fnimi
  if os.path.exists(koht):
    d=json.load(open(koht, encoding="utf-8"))
    u=d["UNESCO"]
    if u:
     for cls in u: 
#      g.add((artikkel, EX.unescoCls, Literal(cls)))
#      g.add((artikkel, EX.unescoCls, EX["kw/"+cls]))
      g.add((artikkel, EX.unescoCls, EKW[urllib.parse.quote_plus(cls)]))
      if u[cls]:
       if "alamklassid" in u[cls]:
        for subcls in u[cls]["alamklassid"]:
#         g.add((artikkel, EX.unescosubCls, Literal(subcls)))
         g.add((artikkel, EX.unescosubCls, EKW[urllib.parse.quote_plus(subcls)]))
       if "marksonad" in u[cls]:
        for ukw in u[cls]["marksonad"]:
         #g.add((artikkel, EX.unescoKw, Literal(ukw)))
         g.add((artikkel, EX.unescoKw, EKW[urllib.parse.quote_plus(ukw)]))
    if "loeteluvalised_marksonad" in d:
      for kw in d["loeteluvalised_marksonad"]:
#        g.add((artikkel, EX.unesco_gemet_additional_keyword, Literal(kw)))
       try:
        g.add((artikkel, EX.unesco_gemet_additional_keyword, EKW[urllib.parse.quote_plus(kw)]))
       except Exception as ex:
         pass
        
def olemiks(oloetelu, nimetus):
  n=nimetus.lower().replace(" ", "_").replace('"', "").replace("[", "").replace("]", "")
  for olem in oloetelu: 
    if olem[4:]==n: return olem
  return "olemita_"+n
  
def olemiseosed(fnimi, valjaanne, g, artikkel):
  koht=kaust+"olemiseosed/"+valjaanne+"/"+fnimi
  if os.path.exists(koht):
   d=json.load(open(koht, encoding="utf-8"))
   oloetelu=olemid[fnimi]
   nr=0
   for voti in d:   
    nr+=1
    if isinstance(d[voti], dict):
       d[voti]=[d[voti]]
    for snr in range(len(d[voti])):        
     try:
      seosenimi=fnimi[:-4]+"_olemiseos_"+str(nr)
      if snr>0: seosenimi+="_"+str(snr+1)
      seos=EX[seosenimi]
      g.add((artikkel, EX.olemiseos, seos))
      for plokk in ["1", "2"]:
        olem=olemiks(oloetelu, d[voti][snr]["roll "+plokk][0])
        g.add((seos, EX["role_"+plokk], ENT[olem]))
        g.add((seos, EX["role_"+plokk+"_type"], Literal(d[voti][snr]["roll "+plokk][1])))
      if "grupp" in d[voti][snr]:
#        g.add((seos, EX["grupp"], Literal(d[voti][snr]["grupp"])))
        g.add((seos, EX["grupp"], EX["gr/"+urllib.parse.quote_plus(d[voti][snr]["grupp"])]))
      if "seos" in d[voti][snr]:
        g.add((seos, EX["seos"], Literal(d[voti][snr]["seos"])))
      if "subjekt" in d[voti][snr] and d[voti][snr]["subjekt"]:
        g.add((seos, EX["subjekt"], ENT[olemiks(oloetelu, d[voti][snr]["subjekt"])]))
      if "objekt" in d[voti][snr] and d[voti][snr]["objekt"]:
        g.add((seos, EX["objekt"], ENT[olemiks(oloetelu, d[voti][snr]["objekt"])])) 
     except:
       pass     

def keybert(fnimi, valjaanne, g, artikkel):
  kkoht=kaust+"votmesona/keybert/"+valjaanne+"/"+fnimi[:-4]+".json"
  if os.path.exists(kkoht):
    dok=json.load(open(kkoht, encoding="utf-8"))
    lemmakoodid=set()
    pkoodid={kood:set() for kood in koodivasted}
    for sona in dok:
      if dok[sona]>=0.3:
        if not re.findall("^[a-zšõäöü]+$", sona):  continue
        if '"' in sona: continue
#        g.add((artikkel, EX["keybert"], Literal(sona)))
        g.add((artikkel, EX["keybert"], EKW[sona]))
        if sona in lemmavasted: lemmakoodid.add(lemmavasted[sona])
    for lemmakood in lemmakoodid:
      for kood in koodivasted:
        if lemmakood in koodivasted[kood]:
          for vaste in koodivasted[kood][lemmakood]:
            pkoodid[kood].add(vaste)
    for kood in pkoodid:
      for vaste in pkoodid[kood]:
        g.add((artikkel, WD["Property:"+kood], WD[vaste]))

def ava_olemid():
  olemikoht=kaust+"entity/file_known_entities.json"
  if os.path.exists(olemikoht):
    return json.load(open(olemikoht))
  return None
olemid=ava_olemid()  



def tonaalsused(fnimi, valjaanne, g, artikkel):
  if fnimi[:-4] in emtaktonaalsus:
    for v in emtaktonaalsus[fnimi[:-4]]:
      st="Neutral"
      if v["sentiment"]=="positiivne": st="Positive"
      if v["sentiment"]=="negatiivne": st="Negative"
      tp="narrower"
      if v["tyyp"]=="valdkond": tp="broader"
      nimetus="assessment_"+fnimi[:-4]+"_"+v["emtak"]
      g.add((artikkel, CLS["hasEMTAKAssessment"], EX[nimetus]))
      g.add((EX[nimetus], CLS["emtakCode"], CLS[v["emtak"]]))
      g.add((EX[nimetus], CLS["sentiment"], MARL[st]))
      g.add((EX[nimetus], CLS["type"], SKOS[tp]))
      

def tootle_fail(fnimi):
    kood=fnimi[:-4]
    g=Graph()
    g.bind("ex", EX)
    g.bind("ekw", EKW)
    g.bind("art", ART)
    g.bind("dct", DCT)
    g.bind("prov", PROV)
    g.bind("ent", ENT)
    g.bind("nlp", NLP)
    g.bind("ver", VER)
    g.bind("cls", CLS)
    g.bind("marl", MARL)
    g.bind("skos", SKOS)
    g.bind("wd", WD)
    artikkel = URIRef("http://mkm.ee/article/"+kood)

    g.add((artikkel, RDF.type, artiklityyp))
    g.add((artikkel, pealkiri, Literal(kppk[kood]["pealkiri"])))
    if kppk[kood]["aeg"]:
      g.add((artikkel, loodud, Literal(kppk[kood]["aeg"],  datatype=XSD.date)))
      g.add((artikkel, EX.createdyear, Literal(kppk[kood]["aeg"][:4],  datatype=XSD.integer)))
    g.add((artikkel, allikas, Literal(fnimi.split("_")[0])))
    g.add((artikkel, sisu, Literal(open(kaust+"plaintext/"+fnimi, encoding="utf-8").read())))
    g.add((artikkel, URIRef("http://www.w3.org/ns/prov#generatedAtTime"), Literal(datetime.datetime.now().replace(microsecond=0).isoformat(),  datatype=XSD.dateTime)))
#    if sm and (kood in sm):
#      s1=sm[kood]
#      lemmas_list=BNode()
#      Collection(g,lemmas_list, [Literal(x) for x in s1])
#      Collection(g,lemmas_list, [EKW[urllib.parse.quote_plus(x)] for x in s1])
#      g.add((artikkel, lemmas_pred, lemmas_list))
    #keybert(fnimi, valjaanne, g, artikkel)
    if olemid and fnimi in olemid:
      oloetelu=olemid[fnimi]
      mentions_list=BNode()
      mentions_pred=EX.mentions
      mention_uris=[ENT[x] for x in oloetelu]
      for uri in mention_uris:
         g.add((artikkel, mentions_pred, uri))
    #egpt=emtak_gpt(fnimi, valjaanne)
    #if egpt:
    #  emtak_list=BNode()
    #  emtak_pred=CLS.hasEMTAKClassification
    #  emtak_uris=[CLS[x] for x in egpt]
    #  for uri in emtak_uris:
    #    g.add((artikkel, emtak_pred, uri))
    efaiss=emtak_faiss(fnimi)
    if efaiss:
      emtak_list=BNode()
      emtak_pred=CLS.hasEMTAKFaiss3
      emtak_uris=[CLS[x] for x in efaiss]
      for uri in emtak_uris:
        g.add((artikkel, emtak_pred, uri))
    #epred=EX.economypercent
    #g.add((artikkel, EX.economypercent, Literal(mudeliprotsent[fnimi]["majandusmudel1.bin"], datatype=XSD.integer)))
    #g.add((artikkel, EX.culturepercent, Literal(mudeliprotsent[fnimi]["kultuurimudel1.bin"], datatype=XSD.integer)))
    #g.add((artikkel, EX.naturepercent, Literal(mudeliprotsent[fnimi]["loodusmudel1.bin"], datatype=XSD.integer)))
    #g.add((artikkel, EX.technologypercent, Literal(mudeliprotsent[fnimi]["tehnikamudel6.bin"], datatype=XSD.integer)))
    
    #unesco(fnimi, valjaanne, g, artikkel)
    #olemiseosed(fnimi, valjaanne, g, artikkel)
    #if emtaktonaalsus:
    #  tonaalsused(fnimi, valjaanne, g, artikkel)   
    with open(kaust+"rdf/articles/"+fnimi[:-4]+".ttl", "w", encoding="utf-8") as f2:
      print(g.serialize(format="ttl"), file=f2)
  
def main():
  #mudeliprotsent=json.load(open(kaust+"mudeliprotsent/"+valjaanne+".json"))
  #sm=None
  #smkoht=kaust+"votmesona/sm/"+valjaanne+".json"
  #if os.path.exists(smkoht):
  #  sm=json.load(open(smkoht, encoding="utf-8"))
  #emtaktonaalsus=None
  #artiklitonaalsus=None
  #koht=kaust+"tonaalsus/"+valjaanne+"_emtak.json"
  #if os.path.exists(koht):
  #  emtaktonaalsus=json.load(open(koht, encoding="utf-8"))
  #  artiklitonaalsus=json.load(open(koht, encoding="utf-8"))
  os.makedirs(kaust+"rdf/articles/", exist_ok=True)
#  fnimed=os.listdir(kaust+"avatekst/"+valjaanne)[:100]
  fnimed=os.listdir(kaust+"plaintext/")
  fnimed.sort()
  fnr=0
#  for fnimi in fnimed:
  for fnimi in fnimed:
    fnr+=1
    if fnr % 1000 ==0: print(fnr, flush=True)
    try:
      tootle_fail(fnimi)
    except Exception as ex:
#      exc_type, exc_obj, exc_tb = sys.exc_info()
      print("probleem", ex, traceback.format_exc(),  flush=True)
      
if __name__=="__main__":
   main()