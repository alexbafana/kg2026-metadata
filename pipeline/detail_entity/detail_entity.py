import os
import json

kaust="./"
ner1=7
ner2=8
loendid={}
valjaanne="de"
with open(kaust+"detail_entity/olemisagedused.txt", encoding = "utf-8") as name_file:
  failisisu = name_file.readlines()
  for cat in ["per", "gpe", "loc", "org", "tit", "prd"]:
    name_list=[name[4:].split("\t")[0].replace("_", " ") for name in failisisu if name.startswith(cat+"_")]
    partial_name_set = set()
    full_name_set = set()

    for name in name_list:
        name = name.lower().strip()
        #Üheosalised nimed talletatakse täisnimede hulka
        if len(name.split()) == 0: continue
        if len(name.split()) == 1:
            full_name_set.add(name)
        #Mitmeosalise nime komponendid talletatakse nimeosade hulka
        #ja lisatakse tühikuga eraldatuna täisnimede hulka
        else:
            full_name_set.add(name)
            name_parts = name.split()
            #print(name_parts)
            last_name = name_parts[-1]
            first_name_parts = name_parts[:-1]
            partial_name_set.add(last_name)
            for name_part in first_name_parts:
                partial_name_set.add(name_part)
    loendid[cat]={
     "full_name_set":full_name_set,
     "partial_name_set":partial_name_set
    }


def get_names(directory, filename, category):
    """Funktsioon otsib failist nimesid ja võrdleb neid teadaolevate nimede loendiga.
        Tuntud ja tundmatud nimed väljastatakse eraldi."""
    file_text = open(directory + "/" + filename, "r", encoding = "utf-8")
    cat=category 
    if category=="prod": cat="prd"
    if category=="title": cat="tit"
    full_name_set=loendid[cat]["full_name_set"]
    partial_name_set=loendid[cat]["partial_name_set"]
    #Eelnevate märgendusridade loend mitmeosaliste nimede tuvastamiseks
    previous_lines = []
    #Muutuja üheosaliste nimede tuvastamiseks
    single_full_name = ""
    #Failist leitud nimede hulk, mis kattub etteantud nimedega
    names_found = set()
    #Failist leitud uute nimede hulk
    new_names = set()
    #Iga märgendusrea väljad salvestatakse loendina
    for line in file_text.readlines()[1:]:
        line_text = line.lower().strip().split(";")
        #Alakriipsude ja võrdusmärkide eemaldamine liitsõnade ja tuletiste algvormidest
        line_text = [sub.replace("_", "") for sub in line_text]
        line_text = [sub.replace("=", "") for sub in line_text]
        #Kontroll, kas sõna on teatud liiki nimi:
        if line_text[ner1].endswith(category) or line_text[ner2].endswith(category):
            #Mitmeosaliste nimede tuvastamine - kontroll, kas eelmine sõna on nimi
            if len(previous_lines) > 0 and (previous_lines[-1][5] == "propn"
                or previous_lines[-1][ner1]!= "o" or previous_lines[-1][ner2]!= "o"): 
                  #and not (line_text[ner1].startswith("b") or line_text[ner2].startswith("b")):
                #Kontroll, kas praegune sõna sisaldub nimeosade hulgas
                if line_text[3] in partial_name_set or line_text[4] in partial_name_set:
                    #Kaheosalise nime eri kujud -
                    #moodustatud algvormidest, sõnavormidest või nende kombinatsioonist
                    name_pair1 = previous_lines[-1][4] + " " + line_text[4]
                    name_pair2 = previous_lines[-1][3] + " " + line_text[4]
                    name_pair3 = previous_lines[-1][3] + " " + line_text[3]
                    name_pair4 = previous_lines[-1][4] + " " + line_text[3]
                    #Kontroll, kas mõni nimepaar sisaldub täisnimede hulgas -
                    #kui jah, talletatakse see leitud nimede hulgas
                    if name_pair1 in full_name_set:
                        names_found.add(name_pair1)
                    elif name_pair2 in full_name_set:
                        names_found.add(name_pair2)
                    elif name_pair3 in full_name_set:
                        names_found.add(name_pair3)
                    elif name_pair4 in full_name_set:
                        names_found.add(name_pair4)
                    #Kui ükski nimepaar täisnimede hulgas ei esine, kontrollitakse,
                    #kas üle-eelmine sõna on nimi - kui jah, otsitakse kolmeosalist nime
                    else:
                        if len(previous_lines) > 1 and (previous_lines[-2][5] == "propn"
                            or previous_lines[-2][ner1] != "o" or previous_lines[-2][ner2] != "o"):
                            #Kõige tõenäolisemad kolmeosalise nime kujud
                            name_triplet1 = previous_lines[-2][4] + " " + previous_lines[-1][4]\
                                + " " + line_text[4]
                            name_triplet2 = previous_lines[-2][3] + " " + previous_lines[-1][3]\
                                + " " + line_text[4]
                            name_triplet3 = previous_lines[-2][3] + " " + previous_lines[-1][4]\
                                + " " + line_text[4]
                            name_triplet4 = previous_lines[-2][3] + " " + previous_lines[-1][3]\
                                + " " + line_text[3]
                            #Kontroll, kas mõni nimekolmik sisaldub täisnimede hulgas -
                            #kui jah, talletatakse see leitud nimede hulgas
                            if name_triplet1 in full_name_set:
                                names_found.add(name_triplet1)
                            elif name_triplet2 in full_name_set:
                                names_found.add(name_triplet2)
                            elif name_triplet3 in full_name_set:
                                names_found.add(name_triplet3)
                            elif name_triplet4 in full_name_set:
                                names_found.add(name_triplet4)
                            #Kui ükski nimekolmik täisnimede hulgas ei esine, kontrollitakse,
                            #kas see sisaldab kahe- või kolmeosalist nime -
                            #kui jah, lisatakse nimi tundmatute nimede hulka
                            else:
                                previous_name1 = previous_lines[-2]
                                previous_name2 = previous_lines[-1]
                                #Kontroll, kas praegune nimi kuulub eelnevaga kokku
                                if (line_text[ner1][-3:] == previous_name2[ner1][-3:]\
                                    and line_text[ner1].startswith("i")) or \
                                    (line_text[ner2][-3:] == previous_name2[ner2][-3:]\
                                    and line_text[ner2].startswith("i")):
                                    #Kontroll, kas eelmine ja üle-eelmine nimi kuuluvad kokku -
                                    #kui jah, talletatakse uus nimi kujul: sõnavorm + lemma + lemma
                                    if (previous_name1[ner1][-3:] == previous_name2[ner1][-3:]\
                                        and previous_name1[ner1].startswith("b")\
                                        and previous_name2[ner1].startswith("i")) or \
                                        (previous_name1[ner2][-3:] == previous_name2[ner2][-3:]\
                                        and previous_name1[ner2].startswith("b")\
                                        and previous_name2[ner2].startswith("i")):
                                        new_name = previous_name1[3] + " " + previous_name1[4]\
                                            + " " + line_text[4]
                                        if new_name not in list(names_found) and new_name.split()[0] != new_name.split()[1]:
                                            new_names.add(new_name)
                                    #Kui kokku kuuluvad vaid praegune ja eelmine nimi,
                                    #siis talletatakse uus nimi kujul: sõnavorm + lemma
                                    else:
                                        if previous_name2[ner1].startswith("b") or \
                                            previous_name2[ner2].startswith("b"):
                                            new_name = previous_name2[3] + " " + line_text[4]
                                            new_names.add(new_name)
                        #Kui üle-eelmine sõna ei ole nimi, kontrollitakse,
                        #kas praegune ja eelmine nimi kuuluvad kokku -
                        #kui jah, talletatakse uus nimi kujul: sõnavorm + lemma
                        else:
                            previous_name = previous_lines[-1]
                            if (line_text[ner1][-3:] == previous_name[ner1][-3:]\
                                and line_text[ner1].startswith("i")\
                                and previous_name[ner1].startswith("b")) or \
                                (line_text[ner2][-3:] == previous_name[ner2][-3:]\
                                and line_text[ner2].startswith("i")\
                                and previous_name[ner2].startswith("b")):
                                new_name = previous_name[3] + " " + line_text[4]
                                if new_name not in list(names_found):
                                    new_names.add(new_name)
                #Kui praegune nimi ei esine nimeosade hulgas, kontrollitakse,
                #kas see kuulub eelmise nimega kokku
                else:
                    name_cat_1 = ""
                    name_cat_2 = ""
                    previous_name = previous_lines[-1]
                    if line_text[ner1][-3:] == previous_name[ner1][-3:]\
                        and line_text[ner1].startswith("i"):
                        name_cat_1 = line_text[ner1][-3:]
                    if line_text[ner2][-3:] == previous_name[ner2][-3:]\
                        and line_text[ner2].startswith("i"):
                        name_cat_2 = line_text[ner2][-3:]
                        #Kontroll, kas tegemist on kolmeosalise nimega -
                        #kui jah, talletatakse uus nimi kujul: sõnavorm + lemma + lemma
                        if len(previous_lines) > 1 and ((previous_lines[-2][ner1].endswith(name_cat_1)\
                            and previous_lines[-2][ner1].startswith("b")) or (previous_lines[-2][ner2].endswith(name_cat_2)\
                            and previous_lines[-2][ner2].startswith("b"))):
                            new_name = previous_lines[-2][3] + " " + previous_name[4]\
                                + " " + line_text[4]
                            if new_name not in list(names_found) and new_name.split()[0] != new_name.split()[1]:
                                new_names.add(new_name)
                        #Kui uus nimi on kaheosaline, talletatakse see kujul: sõnavorm + lemma
                        else:
                            new_name = previous_name[3] + " " + line_text[4]
                            if new_name not in list(names_found):
                                new_names.add(new_name)
            #Kui eelmine sõna ei ole nimi, kontrollitakse, kas sõna sisaldub täisnimede hulgas -
            #kui jah, salvestatakse see loendiga kattuval kujul, aga ei lisata veel leitud nimede hulka
            #else:
            if 1==1:
                #Nimi leitakse ja salvestatakse lemma kujul
                if line_text[4] in full_name_set:
                    single_full_name = line_text[4]
                #Lemmatiseerimisvea tõttu võidakse nimi leida ja salvestada sõnavormina
                elif line_text[3] in full_name_set:
                    single_full_name = line_text[3]
                #Kui sõna ei sisaldu täisnimede ega nimeosade loendis, salvestatakse see lemma kujul
                else:
                    if line_text[3] not in partial_name_set and line_text[4] not in partial_name_set:
                        single_full_name = line_text[4]
        #Kui sõna ei ole märgendatud nimena, kontrollitakse, kas see kuulub siiski eelneva nimega kokku
        #Juhul kui eelnenud nimi on üheosaline, talletatakse see leitud või uute nimede hulgas
        else:
            if len(previous_lines) != 0 and (single_full_name == previous_lines[-1][3] or
              single_full_name == previous_lines[-1][4]):
                potential_name = single_full_name + " " + line_text[3]
                if potential_name in full_name_set:
                  names_found.add(potential_name)
                else:
                  if single_full_name in full_name_set:
                    names_found.add(single_full_name)
                  else:
                    new_names.add(single_full_name)
                single_full_name = ""
        #Märgendusrida talletatakse järgmise tsükli jaoks eelnevate ridade loendis
        previous_lines.append(line_text)
        #Meeles hoitakse kahte eelnevat rida
        if len(previous_lines) > 2:
            previous_lines.pop(0)
        koopiad=set()
        new_names=set([uus.strip() for uus in new_names if len(uus.strip())>0])
        for uus in new_names:
           if len(uus.split(" "))>1:
            for vana in names_found:
              if vana.startswith(uus):
                koopiad.add(uus)
        for k in koopiad:  new_names.remove(k)
    return names_found, new_names


#Sõnastikud nimede ja failide seoste talletamiseks
known_name_dict = {"loc":{}, "gpe":{}, "org":{}, "per":{}, "title":{}, "prod":{}}
new_name_dict = {"loc":{}, "gpe":{}, "org":{}, "per":{}, "title":{}, "prod":{}}
item_directory = kaust+"../data/detail/"

def main():
  import os
  nr=0

  for entry in list(os.scandir(item_directory)):
    if entry.name.endswith(".txt"):
      try:
        nr+=1
        if nr % 1000 == 0 : 
          print(nr, entry.name, flush=True)
        for category in ["per", "loc", "gpe", "org", "title", "prod"]:
          names_in_file = get_names(item_directory, entry.name, category)
        #Tuntud nimede lisamine sõnastikku
          for name in names_in_file[0]:
            if name in known_name_dict[category]:
                known_name_dict[category][name] = known_name_dict[category][name] + "," + entry.name
            else:
                known_name_dict[category][name] = entry.name
        #Uute nimede lisamine sõnastikku
          for name in names_in_file[1]:
            if name in new_name_dict[category]:
                new_name_dict[category][name] = new_name_dict[category][name] + "," + entry.name
            else:
                new_name_dict[category][name] = entry.name
      except Exception as ex:
         print(ex)


  import os
  os.makedirs(kaust+"../data/entity/", exist_ok=True)
  known_names_file_path = kaust+"../data/entity/known_names.json"
  with open(known_names_file_path, "w", encoding = "utf-8") as f_known:
#    json.dump(known_name_dict, f_known, ensure_ascii = False)
    json.dump(known_name_dict, f_known, indent=2, ensure_ascii=False)

  new_names_file_path = kaust+"../data/entity/new_names.json"
  with open(new_names_file_path, "w", encoding = "utf-8") as f_new:
#    json.dump(new_name_dict, f_new, ensure_ascii = False)
    json.dump(new_name_dict, f_new, indent=2, ensure_ascii=False)

  from collections import defaultdict
  fmainimised=defaultdict(list)
  for dn in ["known", "new"]:
    if dn=="known": d=known_name_dict
    else: d=new_name_dict
    for category in ["per", "loc", "gpe", "org", "title", "prod"]:
     dkeys=list(d[category].keys())
     dkeys.sort(key=lambda rida: -len(d[category][rida].split(",")))
     v=[]
     cat=category
     if cat=="prod": cat="prd"
     if cat=="title": cat="tit" 
     for key in dkeys:
       # freq_list.write(key+";")
       # freq_list.write(category+";")
        mentions = d[category][key].split(",")
        for m in mentions:
           fmainimised[m].append(cat+"_"+key.replace(" ", "_"))
       # freq_list.write(str(len(mentions))+";")
        s=key+";"+cat+";"+str(len(mentions))
        v.append(s)
     with open(kaust+"../data/entity/"+cat+"_"+dn+"_freq.txt", "w", encoding="utf-8") as f2:
      print("\n".join(v), file=f2)
    for m in fmainimised:
      fmainimised[m].sort()
    with open(kaust+"../data/entity/fail_olem.json", "w", encoding="utf-8") as f2:
      json.dump(fmainimised, f2, ensure_ascii=False, indent=2)

  vasted=json.load(open(kaust+"detail_entity/olemikoodid_err_ol.json", encoding="utf-8"))
  v={}
  for fnimi in sorted(fmainimised.keys()):
    m=[]
    for olem in fmainimised[fnimi]:
     if olem in vasted:
       if len(vasted[olem])>0:
        m.append(vasted[olem])
    v[fnimi]=m
  json.dump(v, open(kaust+"../data/entity/file_known_entities.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

if __name__=="__main__":
  main()