# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd

writer = pd.ExcelWriter('hockeyStats.xlsx', engine='xlsxwriter')

response = requests.get("https://www.hockey-reference.com/playoffs/NHL_2019_goalies.html") 
soup = BeautifulSoup(response.content, "html.parser")  
    
statsTable = soup.find("table",id="stats")

statsDf = []

for tr in statsTable.find_all("tr"):
    headers =[x.string for x in tr.find_all("th",scope="col")][1:]
    cols=tr.find_all('td')
    cols=[x.text.strip() for x in cols]
    if len(headers) > 0:
        statsDf.append(headers)
    if len(cols) > 0:
        statsDf.append(cols)

statsDf = pd.DataFrame(statsDf)    
print(statsDf)

statsDf.to_excel(writer, sheet_name='stats')
writer.save()