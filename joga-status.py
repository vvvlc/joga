import pandas as pd
import streamlit as st
import datetime
import io

lines=[]
with open("joga-editme.csv","rt") as f:
    lines.append(f.readline())
    lines=lines + [l for l in f.readlines() if l[0:1].isnumeric() ]

df=pd.read_csv(io.StringIO("".join(lines)))

df.Datum=pd.to_datetime(df.Datum,format="%d.%m.%Y")
df.Stazeno=pd.to_datetime(df.Stazeno,format="%d.%m.%Y %H:%M") #06.03.2019 18:13
st.title(f"Joga Status\nServer/file time: {datetime.datetime.now().strftime('%a %d.%m.%Y %H:%M')}/{df.Stazeno.max().strftime('%a %d.%m.%Y %H:%M')}")
#filter today a week before
#today=pd.to_datetime(datetime.datetime.now().date())
#today_df=df[df.Datum==today].groupby(['Datum','Popis','Od']).tail(1)
#lastweek=[ pd.to_datetime(datetime.datetime.now().date()-datetime.timedelta(days=7*i)) for i in range(history)]
#lastweek_df=df[df.Datum==lastweek].groupby(['Datum','Popis','Od']).tail(1)
#selected_day=pd.merge(today_df,lastweek_df,left_on=['Popis','Od'], right_on=['Popis','Od'],suffixes=("","_"))

history=6
lastweek=[ pd.to_datetime(datetime.datetime.now().date()-datetime.timedelta(days=7*i)) for i in range(history)]
lastweek_df=[ df[df.Datum==i].groupby(['Datum','Popis','Od']).tail(1) for i in lastweek] 

selected_day=lastweek_df[0]
for i in range(1,len(lastweek)):
    if not lastweek_df[i] is None:
        selected_day=pd.merge(selected_day,lastweek_df[i],left_on=['Popis','Od'], right_on=['Popis','Od'],suffixes=("",f"_{i}"),how='left')


def safe_eval(p):
    if pd.isna(p):
        return ""
    try:
        v=str(eval(p))
        if v==str(p):
            return v
        else:
            return v+"*"
    except:
        return p

def tt(row):
    #print(row)
    return f"{safe_eval(row.Rezervace)} [{','.join(str(safe_eval(row[f])) for f in row.index if 'Rezervace_' in f)}"

selected_day.Rezervace=selected_day.apply(lambda row: tt(row), axis=1)

selected_day.Od=selected_day.Datum+pd.to_timedelta(selected_day.Od+":00", unit='m')
selected_day=selected_day.drop(columns=(k  for k in selected_day.columns for c in ('Stazeno','Kapacita','Aktivita','Do','Datum','Instruktor_','Typ_','Rezervace_') if c in k))


#make sure that Od is unique
for i in range(len(selected_day)-1):
        if  selected_day.iloc[i].Od==selected_day.iloc[i+1].Od:
            selected_day.ix[i+1,'Od']+=pd.to_timedelta(1,unit='s')#datetime.timedelta(seconds=1)

now=datetime.datetime.now()
#now+=-datetime.timedelta(hours=7)
selected_day.Od=selected_day.Od.apply(lambda k: k+pd.DateOffset(days=1) if k<now else k)
selected_day=selected_day.sort_values('Od')

st.write(selected_day[['Od','Rezervace','Instruktor','Popis']].style.format({
        #'Od':lambda d: f"{d.strftime('%d %H:%M %S')}", 
        'Od':lambda d: f"{d.strftime('%H:%M')}", 
        "Instruktor": lambda k:k[:10]
        }))
