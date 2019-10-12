# -*- coding: utf-8 -*-
"""
Last updated on 10/12/2019
"""

from bs4 import BeautifulSoup,Comment
import requests
import pandas as pd

writer = pd.ExcelWriter('hockeyStats.xlsx', engine='xlsxwriter')

domains = ["https://www.hockey-reference.com/"]
subdomains = {"leagues/NHL_2020_goalies.html":"goalies",
              "leagues/NHL_2020_skaters.html":"skaters",
              "leagues/NHL_2020.html":"league_summary"}
for domain in domains:  
    for page in subdomains:
        url = domain+page
        print(url)
        response = requests.get(url) 
        soup = BeautifulSoup(response.content, "html.parser")  
        if subdomains[page]=="league_summary":
            subsoup = soup.find("div",id="all_stats")
            comment = subsoup.find(text=lambda text:isinstance(text, Comment))
            commentsoup = BeautifulSoup(comment , 'html.parser')
            statsTable = commentsoup.find("table")
            print(statsTable)
        else:
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
        
        statsDf.to_excel(writer, sheet_name=subdomains[page],header=False)

writer.save()