import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from db import create_mysql_engine, upsert_weather


def fetch_weather_data():
    page = requests.get("https://www.timeanddate.com/weather/india/delhi/historic")
    soup=BeautifulSoup(page.content,"html.parser")
    table=soup.find_all("table",{"class":"zebra tb-wt fw va-m tb-hover"})
    l=[]
    for i,items in enumerate(table):
        for i,row in enumerate(items.find_all("tr")):
            d = {}
            try:
                d['hour'] = row.find_all("th",{"class":""})[0].text
                if d['hour'] == 'Time':
                    d['hour'] = np.nan
                else:
                    d['hour'] = int(d['hour'].split('.')[0])

            except:
                d['hour'] = np.nan

            try:
                d['Temp'] = row.find_all("td",{"class":""})[0].text
            except:
                d['Temp'] = np.nan
                
            try:
                d['Weather'] = row.find("td",{"class":"small"}).text
            except:
                d['Weather']= np.nan
                
            try:   
                d['Wind'] = row.find_all("td",{"class":"sep"})[0].text
            except:
                d['Wind'] = np.nan
                
            try:  
                d['Direction'] = row.find("span")["title"]
            except:
                try:
                    d['Direction'] = row.find("span",{"class":"comp sa16"})["title"]
                except:
                    d['Direction'] = np.nan
                
            try:
                d['Humidity'] = row.find_all("td",{"class":""})[2].text
            except:
                d['Humidity'] = np.nan
            
            try:
                d['Barometer'] =  row.find_all("td",{"class":"sep"})[1].text
            except:
                d['Barometer'] = np.nan
        
            try:
                d['Visibility'] =  row.find_all("td",{"class":""})[3].text
            except:
                d['Visibility'] = np.nan
                    
            l.append(d)

    df = pd.DataFrame(l)
    df2 = df.dropna(how = 'all')
    df2 = df2.reset_index()
    df2.pop('index')
    df2['Barometer'] = df2['Barometer'].str.extract('(\d+\.\d+)') + r'"Hg'
    df2['Weather'] = df2['Weather'].str.replace(" ","")
    df2['Visibility'] = df2['Visibility'].str.extract('(\d+)') + 'mi'
    df2['Wind'] = df2['Wind'].str.extract('(\d+)') + 'mph'
    df2['Temp'] = df2['Temp'].str.extract('(\d+)') + u'\N{DEGREE SIGN}' + 'C'
    df2['date'] = datetime.now().strftime("%d-%m-%Y")

    return df2


def main():
    engine = create_mysql_engine()
    df = fetch_weather_data()
    print(df.head())
    upsert_weather(df, engine)


if __name__ == '__main__':
    main()


'''
create table weather(
hour varchar(200) not null,    
Temp varchar(200),
Weather tinytext,
Wind  tinytext,
Direction tinytext,
Humidity varchar(200),
Barometer varchar(200),
Visibility tinytext,
date varchar(200) not null, 
primary key(date, hour)
);
'''