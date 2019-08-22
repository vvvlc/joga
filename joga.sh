#!/bin/bash
cd /home/vitek/robozonky/joga 

env
touch joga-editme.csv
#joga.py generates
joga3/bin/python joga2.py >> joga-editme.csv
rc=$?
if [[ $rc -ne 0 ]]; then
	wget https://hchk.io/1d687bb2-cbe4-4ef7-b079-21cd264298e6/fail -q -O /dev/null || echo Health check failure reporting failed
	exit $rc
fi
#echo eliminate duplicities
#serad zaznamy (bez datumu porizeni zaznamu, -u zajisti, ze se ulozi vzdy nejstarsi zaznam, ktery je duplicitni
#	- sort -u -t, -k2,9   eliminuhje duplicity
#	- dalsi sort na seradit zaznamy podle 
#		data konani 2
#		cas konani 4
#		popis 3
#		stazeno 1
#(cat header.csv && tail -n +2 out.csv | sort -u -t, -k2,9 | sort -u  -t, -k2,5 -k8,10 -k1,1  -k 1.7,1.10n -k1.4,1.5n -k 1.1,1n -k1.12,1.13n -k1.15,1.16n) > final.csv
(cat header.csv && tail -n +2 joga-editme.csv | sort -u -t, -k2,9 | sort  -t,  -k 2.7,2.10n -k2.4,2.5n -k 2.1,2.2n -k4,4i  -k3,3  -k 1.7,1.10n -k1.4,1.5n -k 1.1,1.2n -k1.12,1.13n -k1.15,1.16n) > joga_header.csv
cp joga_header.csv joga-editme.csv
rm joga-final.zip
zip joga-final.zip joga_header.csv
#git commit -am "dataupdate"
#heath check
wget https://hchk.io/1d687bb2-cbe4-4ef7-b079-21cd264298e6 -q -O /dev/null || echo Health check success reporting failed  
