#!/usr/bin/env python
# -*- coding: utf-8 -*-
# - *- coding: ISO-8859-2 -*-

import requests
from bs4 import BeautifulSoup
import unicodedata
import sys
import urllib
import datetime
from pytz import timezone
import sys

def quote(s):
        return s

def _format_time(fhours):
    # http://stackoverflow.com/a/27496953/2561483
    ihours = int(fhours)
    return "%02d:%02d" % (ihours,(fhours-ihours)*60)

def scrap_current_week_to_csv(outfile, now, aktivita, append=False):
    

    if aktivita.startswith(u'Jóga'):
        nazev = u'Jóga'
    else:
        #nazev = unicodedata.normalize('NFKD', aktivita)
        nazev = aktivita
        
    
    url = 'http://jogaandel.travelsoft.cz/?lokalita=chodov&typaktivity=' + aktivita + '&nazevaktivity=' + nazev
    #url = 'http://jogaandel.travelsoft.cz/?'+urllib.urlencode({"lokalita":"chodov", "typaktivity":aktivita, "nazevaktivity": nazev }, 1)
    #url = 'http://jogaandel.travelsoft.cz/?'+urllib.urlencode({"lokalita":"chodov", "typaktivity":aktivita.decode("iso-8859-2"), "nazevaktivity": nazev.decode("iso-8859-2") }, 1)
    print url
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    #data
    dates = []
    rows = soup.find('table', {'id' : 'ctl00_ContentPlaceHolder1_modulKalendarAkci1_tblRezervaceKalendar'}).find_all('tr')
    for row in rows[1:]:
        dates.append(row.td.text.split(' ')[0])
    #v dates je [0] ted datum pondelka, [1] uterka, atd.

    #zpusob zapisu do souboru
    if append:
        mode = 'ab'
    else:
        mode = 'wb'

    #hodiny
    with open(outfile, mode) as f:
        if not append:
            f.write('Stazeno,Datum,Popis,Od,Do,Rezervace,Kapacita,Instruktor,Typ,Aktivita\n'.encode('ascii'))
        #policka s rozvrhem jsou v jedne bunce tabulky jako div-y
        pole = rows[1].find_all('td')[1].find_all('div')
        for item in pole:
            #den je urcen pres pozici policka v css ...
            day = int(item.attrs['style'].split(';')[0].split(':')[1].split(' ')[1][:-2]) / 25
            if day >= 0:
                datum = dates[int(day)]
                #print(str(item.attrs['class'][0])) #urcuje barvu/typ policka
                #naparsovani popisku akce
                dsc_lines = item.attrs['title'].split('\r\n') #4 radky s popisem akce
                akce = dsc_lines[0]
                if '/' in akce: #radek ve formatu: OD - DO / POPIS
                    popis = akce.split('/')[1].strip()
                    x = akce.split('/')[0].split('-')
                    od = ":".join(x[0].split(':')[1:]).strip()
                    do = x[1].strip()
                else: # jinak formatovany radek -> vezmeme to jako popis
                    # urcime cas zacatku z css a cas konce pres dobu trvani
                    popis = akce.split(':')[1].strip()
                    pos = int(item.attrs['style'].split(';')[0].split(' ')[-1][:-2])
                    delka = int(dsc_lines[2].split(' ')[1]) / 60
                    zac = 7 + pos / 48
                    od = _format_time(zac)
                    do = _format_time(zac + delka)
                obsaz = item.span.text.split('/')
                rezervace = obsaz[0]
                kapacita = obsaz[1]
                if len(dsc_lines)>=4:
                    tmp= dsc_lines[3]
                    if tmp.startswith(u'instruktor'):
                        instruktor = tmp.split(':')[1].strip()
                    else:
                        instruktor=''
                else:
                    instruktor= ''
                typ = dsc_lines[1].split(':')[1].strip()

 #               print ",".encode("utf8").join([datum, popis, od, do, rezervace, kapacita, instruktor, typ])
#               print aktivita
#                for x in [datum, popis, od, do, rezervace, kapacita, instruktor, typ, aktivita]:
#                    print x.encode("iso-8859-2")
#                    sys.stdout.write(x.encode("iso-8859-2"))
#                        sys.stdout.write(codedata.normalize('NFKD', x).encode('ascii', 'ignore'))

                #f.write(u",".join([datum, popis, od, do, rezervace, kapacita, instruktor, typ, aktivita]).encode("iso-8859-2"))
                #f.write(u",".join([snow, datum, popis, od, do, rezervace, kapacita, instruktor, typ, aktivita]).encode("utf8"))
                #sout=u",".join([snow, datum, popis, od, do, rezervace, kapacita, instruktor, typ, aktivita])
                csv_line = [snow, datum, popis, od, do, rezervace, kapacita, instruktor, typ, aktivita]
                #replace, by -
                sout=u",".join([fld.replace(',','-') for fld in csv_line])
                                                                
                f.write(unicodedata.normalize('NFKD', sout).encode('ascii', 'ignore')+"\n")
#                unic = (','.join([datum, popis, od, do, rezervace, kapacita, instruktor, typ, aktivita]) + '\n')
                #print ",".encode("utf8").join([datum, popis, od, do, rezervace, kapacita, instruktor, typ, aktivita])
#                f.write(unicodedata.normalize('NFKD', unic).encode('ascii', 'ignore'))


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
    scrap_current_week_to_csv(outfilename, snow ,u'Jóga modrý sál', append=True)
    scrap_current_week_to_csv(outfilename, snow, u'Jóga zelený sál', append=True)
    scrap_current_week_to_csv(outfilename, snow, u'Hot-joga', append=True)


#javascript:__doPostBack('ctl00$ContentPlaceHolder1$modulKalendarAkci1$lbNasledujiciTyden','')
#javascript:__doPostBack('ctl00$ContentPlaceHolder1$modulVyberAktivity1$snippetZalozkaTypAktivity1$lbTypAktivity','')
