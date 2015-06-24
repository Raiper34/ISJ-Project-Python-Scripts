#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
#ISJ Skriptovaci jazyky Projekt - Stahovanie prispevkov z twittera steam_games
#Autor: Filip Gulan xgulan00@stud.fit.vutbr.cz

from TwitterSearch import *
import urllib3
import re
import os.path
import sys
from datetime import datetime
import shutil

nolink = 0 #na zistenie ci to je zadany argument noink 0nezadany 1 zadany
if len(sys.argv) > 1: #ak je tam nejaky argument
    if sys.argv[1] == "-nolink": #argument -nolink, ktory nebude stahovat obsah odkazovanych web stranok
        nolink = 1
    if sys.argv[1] == "-repair": #argument, ktory ked je zadany, tak vymaze vsetko, ak by sa rozbil log/alebo adresarova struktura...
        if os.path.exists("twitter"):
            shutil.rmtree("twitter")
        sys.exit(0)
    else: #ak tam nieco je ale nezname, tak chyba
        print("Nespravne zadanie argumentov!", file=sys.stderr)
        exit(1)

prveSpustenie = 0 #na zistenie ci to je prve spustenie kedy stahujem 50 prispevkov alebo nte, kedy aktualizujem
if os.path.exists("twitter/log"): #neni prve spustenie
    try:
        log = open("twitter/log", 'r') #otvorim si log subor a vytiahnem ifnormaciu o tom aky tweet bol najaktualnejsi
        logRiadky = log.readlines()
    except:
        print("Subor log nejde otvorit!", file=sys.stderr)
    finally:
        log.close()
    poslednyRiadok = logRiadky[-2]
    poslednyRiadok = re.sub("Posledny tweet: ", "", poslednyRiadok)
else: #prve spustenie nastavim priznak
    prveSpustenie = 1


http = urllib3.PoolManager() #ak by som si bol skutocne isty ze tam bduu iba linky na steam tak by som vyuzil zmysluplne aj urllib3 :-D
try:
    profil = TwitterUserOrder('steam_games') #profil ktory spracovavam
    #informacie o mojej apke ISJxgulan00
    aplikacia = TwitterSearch(
        consumer_key = '9WeCwJxmOEjiZsBMxKH95kGZm',
        consumer_secret = '0rGIV7gzSkj3A5PNJOCQ9Ds3O1GNEe7uu4vbeWq7Ol48T0dZBh',
        access_token = '192156919-Lnwildgb9xMXYF5bORZZhKIwrFTkql6Nw0r84iUy',
        access_token_secret = 'vPylUoRSeRryxhlEDyiOPU6pxviF88H30oTPTViRF8TTA'
    )


    try:
        if not os.path.exists("twitter"): #ak neexistuju zlozky treba ich vytvorit
            os.makedirs("twitter")
        if not os.path.exists("twitter/stranky/"):
            os.makedirs("twitter/stranky/")
    except:
        print("Adresarovu strukturu sa nepodarilo vytvorit!", file=sys.stderr)
        exit(1)


    try:
        tweets = open("twitter/tweety", 'a+') #tweety pojdu do tohoto suboru
    except:
        print("Subor nejde otvorit alebo vytvorit!", file=sys.stderr)
        exit(1)


    tweetCislo = 0 #premena pocitanie poctu spracovanych tweetov
    for tweet in aplikacia.search_tweets_iterable(profil): #idem po tweete na uzivatelovom timeline
        data = tweet['text'] #text tweetu

        if tweetCislo == 0: #ak je to prvy tweet, tak si ho ulozim
            prvyTweet = data
            try: #otvorim log a zapisem donho prvy tweet a nasledne hned zavrem
                log = open("twitter/log", 'a+') #zapisem informacie o aktualnom tweety do suboru aby som vedel aktualizovat
                log.write("Datum: " + str(datetime.now()) + "\nPosledny tweet: " + prvyTweet + "\n--------------------------\n")
            except:
                print("Subor nejde otvorit alebo vytvorit alebo sa dono nepodarilo zapisat!", file=sys.stderr)
                log.close()
                tweets.close()
                exit(1)
            finally:
                log.close()

        if prveSpustenie == 0: #ak to neni prve spustenie, tak porovavam s poslednym aktualnym tweetom ci ma cenu okracovat
            if data + "\n" == poslednyRiadok:
                break


        if tweetCislo == 0: #este pred zapisanim dam do suboru aktualn datum kedy boli tweety ulozene
            tweets.write("--------------------------\n"+ str(datetime.now()) + "\n--------------------------\n")

        if nolink == 1: #ak je nolink zadany tak nas linky na stranky nezuimaju
            link = None
        else:
            link = re.search("http://.*?(?= |$)", data) #ak tam je link tak si ho najdem

        print("Spracovavam tweet cislo: " + str(tweetCislo + 1))
        tweets.write(data + "\n")


        if link is not None: #ak tam je link, tak stiahneme obsah toho linku
            htmltext = http.request('GET', link.group())
            htmltext = htmltext.data.decode("utf8")
            menoSuboru = re.search("(?<=<title>).*?(?=</title>)", htmltext).group() #podla title to budem pomenovavat subor
            menoSuboru = re.sub("[\*\.\"/\[\]:;|=,]", "", menoSuboru)
            try:
                stranka = open("twitter/stranky/" + menoSuboru + ".html", 'w+') #vytvorim subor a zapisem donho
                print(htmltext, file=stranka)
            except:
                print("Subor nejde otvorit alebo vytvorit alebo sa dono nepodarilo zapisat!", file=sys.stderr)
                stranka.close()
                tweets.close()
                exit(1)
            finally:
                stranka.close()


        if prveSpustenie == 1: #ak je prve spustenie, tak berem prvych 50 tweetov
            if tweetCislo + 1 >= 50:
                break
        tweetCislo += 1

    tweets.close()

except TwitterSearchException as e:
    print(e, file=sys.stderr)