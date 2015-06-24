#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
#ISJ Skriptovaci jazyky Projekt - Stahovanie prispevkov z fora ceske-hry.cz
#Autor: Filip Gulan xgulan00@stud.fit.vutbr.cz

import re
import sys
import urllib3
import os.path
import shutil

"""
Funkcia na prevedenie si datumov z fora, ktore su v specialnom formate na datum v tvare 14 misetneho cisla
Argument: datum tkroy konvertujem na cislo
Vracia: prevedeny datum na cislo
"""
def datumNacislo(datum):
    den = re.search("^.*?(?=\.)", datum).group()
    if len(den) < 2: #aby bol jendotny format tak ak je jendociferny den tak doplnim 0 ako 2 cifru
        den = '0' + den
    mesiacRok = re.search("(?<= ).*?(?=,)", datum).group()
    mesiac = re.search("^.*(?= )", mesiacRok).group()
    mesiace = {'leden': '01', 'únor': '02', 'březen': '03', 'duben': '04', 'květen': '05', 'červen': '06', 'červenec': '07', 'srpen': '08', 'září': '09', 'říjen': '10', 'listopad': '11', 'prosinec': '12'}
    mesiac = mesiace[mesiac]
    rok = re.search("(?<= ).*$", mesiacRok).group()
    cas = re.search("(?!.* ).*$", datum).group()
    hodiny = re.search("^.*?(?=:)", cas).group()
    minuty = re.search("(?<=:).*?(?=:)", cas).group()
    sekundy = re.search("(?!.*:).*$", cas).group()
    datum = rok + mesiac + den + hodiny + minuty + sekundy #spojim string a nakoniec prevedem v return na int a vratim
    return(int(datum))

"""
Funkcia na prehladavanie subfora
Argument: meno subfora ktore prehladavam, link subfora ktore prehladavam
"""
def ziskajInformacie(menoSubfora, html2):
    global prispevokCislo
    global datumF #datum fora
    global firstpage
    global metaonly
    menoSuboru = re.sub("[\*\.\"/\[\]:;|=,]", "", menoSubfora) #odstranim potencialne nechcene znaky v nazovch suborov
    vystup = open("forum/ceske-hry/" + menoSuboru, 'a+') #otvorim si subor do ktoreho budem zapisovat
    vystup.write("\n++++++++++++++++++++++++++\n"+ datumF + "\n++++++++++++++++++++++++++\n\n") #zapisem si hlavicku s datumom

    while 1: #iterujem cez temy v subforum, proste iba cz stranky kde je vypis tem
        try:
            htmltext = http.request('GET', "http://www.ceske-hry.cz/forum/" + html2)
            htmltext = htmltext.data.decode("utf8")
            #htmltext = htmlfile.read()
        except:
            print("Nastala chyba nadvazovania komunikacie so serverom Ceske-hry.cz!\n", file=sys.stderr)
            sys.exit(1)

        #najdem si vsetky linky na dane temy, potom linky na dane temy a datumy ci tam vobec ist pozerat novy prispevok
        diskusia = re.findall("(?:(?<=<span class=\"topictitle\"><a href=\").*?(?=\" class=\")|(?<=<span class=\"topictitle\"><b>Oznámení:</b> <a href=\").*?(?=\" class=\")|(?<=<span class=\"topictitle\"><b>\[ Hlasování \]</b> <a href=\").*?(?=\" class=\"))", htmltext)
        html2 = re.search("(?<!Předchozí</a>&nbsp;&nbsp;<a href=\")(?<=</a>&nbsp;&nbsp;<a href=\").*?(?=\">Další</a></b></span></td>)", htmltext)
        aktualFor = re.findall("(?<=<span class=\"postdetails\">).*?(?=<br /><a href=)", htmltext)

        for i in range(len(diskusia)): #iterujem cez prispevky danej otvorenej temy
            if datumNacislo(datumAktual) > datumNacislo(aktualFor[i]): #ak tam neni novy prispevok tak ani nejdem dalej
                continue

            html = diskusia[i]
            while 1: #aby som mohol prehadzat na dalsie stranky
                try:
                    htmltext = http.request('GET', "http://www.ceske-hry.cz/forum/" + html)
                    htmltext = htmltext.data.decode("utf8")
                except:
                    print("Nastala chyba nadvazovania komunikacie so serverom Ceske-hry.cz!\n", file=sys.stderr)
                    sys.exit(1)
                tema = re.search("(?<=<title>České-Hry\.cz :: Fórum :: Zobrazit téma - ).*?(?=</title>)", htmltext) #vytuahnem si meno temy

                for vyskyt in re.finditer("<span class=\"name\">.*?class=\"nav\">Návrat nahoru</a>", htmltext, re.DOTALL): #iterujem cez vsetky rpispevky na danej stranke temy
                    autor = re.search("(?<=<span class=\"name\">).*?(?=</b></span><br /><span class=\"postdetails\">)", vyskyt.group()) #vytiahnem si autora prispevku
                    autor = re.sub("<a name=\"[0-9]*\"></a><b>", "", autor.group())
                    datum = re.search("(?<=border=\"0\" /></a><span class=\"postdetails\">).*?(?=<span class=\"gen\">&nbsp;</span>&nbsp; )", vyskyt.group()) #vytiahnem sidatum rpispevku
                    if metaonly == 0: #ak nechcem iba metainformacie, tak idem spracovavat aj prispevky jednotlive
                        text = re.search("(?<=<span class=\"postbody\">)(?!.*<span class=\"postbody\">).*?(?=</table>)", vyskyt.group(), re.DOTALL).group()
                        text = re.sub("<.*?>", "", text) #odstranim html tagy
                        text = re.sub("(?s)[\t]+", "", text) #odstranim biele znaky nechene
                        text = re.sub("(?s)[\n\r]+", "\n", text)
                        text = re.sub("(?s)_________________.*$", "", text) #odstranim podpis uzoivatela
                        text = re.sub("Naposledy upravil.*$", "", text) #odstranim informaciu o tom kedy bolo naposledy upraveny prispevok
                        text = re.sub("(?s)\n$", "", text)
                        text = re.sub("(?s)^\n", "", text)
                    prispevokAkt = re.sub("Zaslal: ", "", datum.group()) #zistim si datum prsiepvku bez slovicka zaslal
                    if datumNacislo(datumAktual) < datumNacislo(prispevokAkt): #ak je to novy prispevok tak ho zapisem
                        print("Spracovavam/kontrolujem prispevok cislo: " + str(prispevokCislo))
                        if metaonly == 0: #chcem vsetko
                            vystup.write("Subforum: " + menoSubfora + "\nTema: " + tema.group() + "\nUzivatel: " + autor + "\n" + datum.group() + "\nText prispevku:\n" + text + "\n--------------------------\n")
                        else: #chcem iba meta informacie
                            vystup.write("Subforum: " + menoSubfora + "\nTema: " + tema.group() + "\nUzivatel: " + autor + "\n" + datum.group() + "\n--------------------------\n")
                        prispevokCislo += 1

                html = re.search("(?<!Předchozí</a>&nbsp;&nbsp;<a href=\")(?<=</a>&nbsp;&nbsp;<a href=\").*?(?=\">Další</a></b><br />)", htmltext) #najdem si link na dalsiu stranku
                if html == None: #ak som nenasiel link, neni tam dalsia stranka = ukoncujem prehladavanie tejto temy
                    break
                html = html.group()
                html = re.sub("&amp;", "&", html) #odstranim znaky z odkau ktore robia sarapatu

        if html2 == None or firstpage == 1: #ak som ennasiel link na dalsiu stranku v dnanom subfore koncim, alebo koncim aj vtedy ak nechcem spracovavat viacero stranok
            vystup.close()
            break
        html2 = html2.group()
        html2 = re.sub("&amp;", "&", html2)

firstpage = 0 #priznak ci je zadasny argument firstpage
metaonly = 0 #a argumetn metaonly
if len(sys.argv) == 2: #ak je tam iba jeden argument musi to byt jeden z tych dole
    if sys.argv[1] == "-firstpage": #argument na vypis iba prvych stranok v danom subfore
        firstpage = 1
    elif sys.argv[1] == "-metaonly": #argument na vypis iba metainformaci bez tprispevku
        metaonly = 1
    elif sys.argv[1] == "-repair": #argument, ktory ked je zadany, tak vymaze vsetko, ak by sa rozbil log/alebo adresarova struktura...
        if os.path.exists("forum"):
            shutil.rmtree("forum")
        sys.exit(0)
    else: #ak tam nieco je ale nezname, tak chyba
        print("Nespravne zadanie argumentov!", file=sys.stderr)
        exit(1)
elif len(sys.argv) == 3: #2 argumenty jeden z nizsie musi byt
    if sys.argv[1] == "-firstpage" or sys.argv[2] == "-firstpage":
        firstpage = 1
    else: #ak tam nieco je ale nezname, tak chyba
        print("Nespravne zadanie argumentov!", file=sys.stderr)
        exit(1)
    if sys.argv[1] == "-metaonly" or sys.argv[2] == "-metaonly":
        metaonly = 1
    else: #ak tam nieco je ale nezname, tak chyba
        print("Nespravne zadanie argumentov!", file=sys.stderr)
        exit(1)
elif len(sys.argv) > 3: #viac argumentov chyba
    print("Nespravne zadanie argumentov!", file=sys.stderr)
    exit(1)

prispevokCislo = 0 #pocitanie prisoevkov na vypis na stdin co robim prave
http = urllib3.connection_from_url('http://www.ceske-hry.cz/forum/')

try:
    if not os.path.exists("forum"): #ak neexistuju zlozky treba ich vytvorit
        os.makedirs("forum")
    if not os.path.exists("forum/ceske-hry"): #ak neexistuju zlozky treba ich vytvorit
        os.makedirs("forum/ceske-hry")
except:
    print("Adresarovu strukturu sa nepodarilo vytvorit!", file=sys.stderr)
    exit(1)

prveSpustenie = 0 #na zistenie ci to je prve spustenie kedy stahujem 50 prispevkov alebo nte, kedy aktualizujem
if os.path.exists("forum/log"): #neni prve spustenie
    try:
        log = open("forum/log", 'r') #otvorim si log subor a vytiahnem ifnormaciu o tom aky tweet bol najaktualnejsi
        logRiadky = log.readlines()
    except:
        print("Subor log nejde otvorit!", file=sys.stderr)
    finally:
        log.close()
    poslednyRiadok = logRiadky[-2] #ziskam datum z lgu
    datumAktual = re.sub("Datum: ", "", poslednyRiadok) #ulzoim si datum aby som mal ako porovnavat a vedel aktualizovat
else: #prve spustenie nastavim priznak
    prveSpustenie = 1

try:
    htmltext = http.request('GET', "http://www.ceske-hry.cz/forum/index.php")
    htmltext = htmltext.data.decode("utf8")
except:
    print("Nastala chyba nadvazovania komunikacie so serverom Ceske-hry.cz!\n", file=sys.stderr)
    sys.exit(1)
subfora = re.findall("(?<=<span class=\"forumlink\"> <a href=\").*?(?=\" class=\"forumlink\">)", htmltext) #najdem si linky na vsetky subfora
subforaMena = re.findall("(?<=\" class=\"forumlink\">).*?(?=</a><br />)", htmltext) #najdem si mena vsetkych subfor
aktualSubFor = re.findall("(?<=<span class=\"gensmall\">).*?(?=<br /><a href=)", htmltext) #najdem si datumy poslednych aktualizaci subfor
datumF = re.search("(?<=Právě je ).*?(?=<br /></span><span class=\"nav\">)", htmltext).group() #najdem si aktualny cas fora

if prveSpustenie == 1: #ak je prve psustenie, tak nastavim fiktivny cas na rok este pred ako bolo forum vytvorene a porovnavam s tym
    datumAktual = "24. duben 2000, 10:08:05"
try: #otvorim log a zapisem donho datum kedy bol skript naposledy spusteny
    log = open("forum/log", 'a+')
    log.write("Datum: " + datumF + "\n--------------------------\n")
except:
    print("Subor nejde otvorit alebo vytvorit alebo sa dono nepodarilo zapisat!", file=sys.stderr)
    log.close()
    exit(1)
finally:
    log.close()

for i in range(len(subfora)): #spracovavam informacie v jendotlivych subforach
    if datumNacislo(datumAktual) < datumNacislo(aktualSubFor[i]): #ak v subfore je aktualizacia tak ju vyhladam a zapisem
        ziskajInformacie(subforaMena[i], subfora[i])