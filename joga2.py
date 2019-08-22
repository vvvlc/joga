#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# - *- coding: ISO-8859-2 -*-


import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import unicodedata
import sys
import urllib
import datetime
from pytz import timezone
import sys
import re

import urllib3
urllib3.disable_warnings()

def quote(s):
    return s

def _format_time(fhours):
    # http://stackoverflow.com/a/27496953/2561483
    ihours = int(fhours)
    return "%02d:%02d" % (ihours,(fhours-ihours)*60)

def tostr(uni):
    #return unicodedata.normalize('NFKD', uni).encode('ascii', 'ignore').strip()
    return str(uni).strip()

def scrap_current_week_to_csv(outfile, now, cdate, append=False):


    #url = 'http://jogaandel.travelsoft.cz/?lokalita=chodov&typaktivity=' + aktivita + '&nazevaktivity=' + nazev
    #nastav chodov a kopiruj phpsessionid
    s = requests.session()
    r = s.get("https://rezervace.dum-jogy.cz/rs/kalendar_vypis/zmena_mistnosti/4",verify=False)
    
    #url = 'http://rezervace.dum-jogy.cz/rs/kalendar_vypis/kalendar_vypis/2018-06-04/1'
    url = 'https://rezervace.dum-jogy.cz/rs/kalendar_vypis/kalendar_vypis/'+cdate+'/1'
    
    #url = 'http://jogaandel.travelsoft.cz/?'+urllib.urlencode({"lokalita":"chodov", "typaktivity":aktivita, "nazevaktivity": nazev }, 1)
    #url = 'http://jogaandel.travelsoft.cz/?'+urllib.urlencode({"lokalita":"chodov", "typaktivity":aktivita.decode("iso-8859-2"), "nazevaktivity": nazev.decode("iso-8859-2") }, 1)
    #print url
    r = s.get(url,verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')

    akce={}
    #lekce    
    #print('Stazeno,Datum,Popis,Od,Do,Rezervace,Kapacita,Instruktor,Typ,Aktivita')
    for i in soup.find_all('div', {'class': 'jedna-lekce-vypis'}):
        #detail  
        idakce=i.attrs['id'].split('_')[-1]
        akce['https://rezervace.dum-jogy.cz/rs/akce/tooltip/'+idakce]='t_'+idakce
        #akce['https://rezervace.dum-jogy.cz/rs/akce/zobrazit_akci/'+idakce]='a_'+idakce

    pool = ThreadPoolExecutor(20)
    #futures = [pool.submit(s.get,url,verify=False) for url in list(akce.keys())[1:5]]
    futures = [pool.submit(s.get,url,verify=False) for url in akce.keys()]
    akce=dict(((akce[r.result().url], r.result()) for r in as_completed(futures)))
    #results = [r.result() for r in as_completed(futures)]
    #akce=dict(((akce[r.url], r) for r in results))

    lekce_wrapper_pattern=r'lekce-wrapper-((\d{4})-(\d{2})-(\d{2}))'
    for day in soup.find_all('div',{'class':re.compile(lekce_wrapper_pattern)}):
        #find class with 
        for classname in day.attrs['class']:
            matchObj=re.match(lekce_wrapper_pattern,classname.strip())
            if matchObj:
                datum=matchObj.group(4).strip()+'.'+matchObj.group(3).strip()+'.'+matchObj.group(2).strip()
                break
            else:
                datum='n/a'

        for i in day.find_all('div', {'class': 'jedna-lekce-vypis'}):    
            #rdetail = s.get('https://rezervace.dum-jogy.cz/rs/akce/tooltip/'+idakce,verify=False)
            idakce=i.attrs['id'].split('_')[-1]
            rdetail = akce['t_'+idakce]
            soupdetail = BeautifulSoup(rdetail.text, 'html.parser')
            try:
                popis=tostr(soupdetail.find('div',{'class':'tooltip-lekce-nazev'}).text)
            except Exception as e:
                #e.args += (rdetail.url,rdetail.text)
                #raise
                popis="N/A"
                        
            od=tostr(i.find('span',{'class':'cas-od'}).text).strip()
            do=tostr(i.find('span',{'class':'cas-do'}).text).strip()[1:].strip()        

            tmp=tostr(i.find('div',{'class':'lekce-telo-ceny_a_obsazenost'}).text).strip()                                        
            #kdyz to neni vyplneni tak uz lekce probehla a nemusim ten radek vypisovat
            if len(tmp)>0:
                tmp=tmp.replace(')','').replace('(','').split("/")
                rezervace=tmp[0].strip()
                kapacita=tmp[1].strip()
                instruktor=tostr(i.find('div',{'class':'lekve-telo-instruktor'}).text) 
                typ=tostr(i.find('div',{'class':'lekce-telo-aktivita'}).text)
                aktivita=''
                
                csv_line = [snow, datum, popis, od, do, rezervace, kapacita, instruktor, typ, aktivita]
                        #replace, by -
                print(",".join([fld.replace(',','-') for fld in csv_line]))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        outfilename = 'out.csv'
    else:
        outfilename = sys.argv[1]

    now = datetime.datetime.now(timezone('CET'))
    snow = now.strftime("%d.%m.%Y %H:%M")
    #print snow
    # pozor
    #fix issue with time zone +06:00 NewYour vs Prague and broken time 6:39:07->7:27:50 -> celkovy posun o 6:48:43
    #last cron executed in May  8 06:05:01  of NY time of old time before I moved time to 6:39:07->7:27:50


    #pozor zase problem s datem
    #Tue, Sep 19, 2017  8:38:03 AM  mypc
    #Tue Sep 19 02:08:27 EDT 2017   jenkins time
    #Tue, Sep 19, 2017  8:38:05 AM my pc

    cdate=(datetime.datetime.today()-datetime.timedelta(days=datetime.datetime.today().weekday())).strftime("%Y-%m-%d")
    #print(cdate)
    scrap_current_week_to_csv(outfilename, snow,cdate, append=True)

    cdate=(datetime.datetime.today()-datetime.timedelta(days=datetime.datetime.today().weekday()-7)).strftime("%Y-%m-%d")
#    print(cdate)
    scrap_current_week_to_csv(outfilename, snow,cdate, append=True)

#javascript:__doPostBack('ctl00$ContentPlaceHolder1$modulKalendarAkci1$lbNasledujiciTyden','')
#javascript:__doPostBack('ctl00$ContentPlaceHolder1$modulVyberAktivity1$snippetZalozkaTypAktivity1$lbTypAktivity','')

