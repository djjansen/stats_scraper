# -*- coding: utf-8 -*-
"""
This script reads data from the below sites and creates pandas Excel files to 
support personal Tableau dashboards. All data collected is publicly available for download from the site,
and rate limiting is employed to keep rapidity of requests reasonable.
"""

from bs4 import BeautifulSoup,Comment
import requests
import time
import pandas as pd

#open writer to create Excel sheet
writer = pd.ExcelWriter('hockeyStats.xlsx', engine='xlsxwriter')

#attach these abbreviations to team summary data to allow for joins on player data
NHL_abbrevs=["ANA","ARI","BOS","BUF","CGY","CAR","CHI","COL",
             "CBJ","DAL","DET","EDM","FLA","Avg","LAK","MIN",
             "MTL","NSH","NJD","NYI","NYR","OTT","PHI","PIT",
             "SJS","STL","TBL","TOR","VAN","VEG","WSH","WPG"]

#domains for outer loops, allows for extracting from multiple, similar sites
domains = ["https://www.hockey-reference.com/"]
#subdomains for looping through multiple pages to collect stats
subdomains = {"leagues/NHL_2020_goalies.html":"goalies",
              "leagues/NHL_2020_skaters.html":"skaters",
              "leagues/NHL_2020.html":"league_summary"}

#main for loop, constructing URLs and parsing html
for domain in domains:  
    for page in subdomains:
        url = domain+page
        response = requests.get(url) 
        soup = BeautifulSoup(response.content, "html.parser")  
        #this table is weird, so the code extracts the table data from a comment
        if subdomains[page]=="league_summary":
            subsoup = soup.find("div",id="all_stats")
            comment = subsoup.find(text=lambda text:isinstance(text, Comment))
            commentsoup = BeautifulSoup(comment , 'html.parser')
            statsTable = commentsoup.find("table")
        #normal table identification
        else:
            statsTable = soup.find("table",id="stats")
        
        #create list of lists from table rows
        statsDf = []
        
        for tr in statsTable.find_all("tr"):
            headers =[x.string for x in tr.find_all("th",scope="col")][1:]
            cols=tr.find_all('td')
            cols=[x.text.strip() for x in cols]
            #ignore empty header rows
            if len(headers) > 0:
                #re-insert missing column (again, for weird table)
                if subdomains[page]=="league_summary":
                    headers.insert(0,"Team")
                headers = filter(None, headers)
                statsDf.append(headers)
            if len(cols) > 0:
                statsDf.append(cols)
        
        #convert list of lists to dataFrame, assign first row to column names
        statsDf = pd.DataFrame(statsDf) 
        statsDf.columns = statsDf.iloc[0]
        statsDf=statsDf[1:]
        
        #sort alphabetically, join abbreviations list
        if subdomains[page]=="league_summary":
           statsDf.sort_values(by=['Team'],inplace=True)
           statsDf['Abbr']=NHL_abbrevs
        
        print(statsDf)
        #write finished dataFrame to Excel sheet, name stored in subdomains dict        
        statsDf.to_excel(writer, sheet_name=subdomains[page])
        
        #sleep for rate limiting
        time.sleep(3)
#save Excel document
writer.save()