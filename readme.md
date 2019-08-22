setup
=====

## initial setup
```
virtualenv -p python3 joga3
source joga3/bin/activate
pip install -r requirements.txt
./joga2.py
```

## test run 
`joga3/bin/python joga2.py`

## cron
`crontab -e `

```
MAILTO=emailaddress
PYTHONIOENCODING=utf8
* * * * *  /home/vitek/robozonky/bin/cronic /home/vitek/robozonky/joga/joga.sh
@weekly  echo "Joga summary" | mutt -a /home/vitek/robozonky/joga/joga-final.zip -s "joga overview" -- emailaddress > /dev/null
@daily  /home/vitek/robozonky/bin/cronic (cd /home/vitek/robozonky/joga && git push)
```


for edit csv file
=================

* git fetch
* git merge origin/master
* git mergetool
  use `diffu` to save changes
* vim joga-editme.csv
* ./joga.sh
* git commit
* git push
* `crontab -e `
  uncomment joga line

