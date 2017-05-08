# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 10:45:36 2017

In this program file I am going to create 2 datasets:
    1. All coaches with coaching post each season
    2. All players stats for each season, especially  win shares


Win shares are attributed to a mentor as a proportion of the total 
outgoing links from the mentee going to this given mentor, where links are
given by no. of years played together.

Modification 170328: only past prime players can be mentors

@author: Bence Szabo
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re as re
import string


############################################
#I. Creating the NBA player dataset
############################################

#input: years taken into account
y_start = 1999
y_finish = 2015
seasons = range(y_start, y_finish + 1)

#we are going to append to this
varlist = ['Player',
 'Pos',
 'Age',
 'Tm',
 'G',
 'MP',
 'PER',
 'TS%',
 '3PAr',
 'FTr',
 'ORB%',
 'DRB%',
 'TRB%',
 'AST%',
 'STL%',
 'BLK%',
 'TOV%',
 'USG%',
 'OWS',
 'DWS',
 'WS',
 'WS/48',
 'OBPM',
 'DBPM',
 'BPM',
 'VORP']

df_nba_stats = pd.DataFrame(columns = varlist)

#defined scraping function of NBA player stats
def nba_player_stats(url_s, year, varlist):
    # url that we are scraping
    url = url_s
    
    # this is the html from the given url
    html = urlopen(url).read()
    soup = BeautifulSoup(html)  
        
    column_headers = [th.getText() for th in 
                      soup.findAll("tr", limit=2)[0].findAll("th")]
    del column_headers[0]
    
    stats_raw = [[td.getText() for td in
                 soup.findAll("tr")[1:][i].findAll("td")] for i in range(len(soup.findAll("tr")[1:]))]
    
    df = pd.DataFrame(stats_raw, 
                      columns = column_headers)
    
    #I only need OWS and DWS
    df = df[varlist]
    df["Year"] = year
    
    #correct for missing rows 
    df = df[df.Player.str.contains("None") == False]
    
    #correct for players traded within year: only use first one
    df = df[df.Tm.str.contains("TOT") == False]
    df = df.drop_duplicates(subset = "Player" , keep = "first")
    
    #correct for moving NBA teams: SEA -> OKC, NOH -> NOP, VAN -> MEM, CHA -> CHO CHH -> CHO, NJN -> BRK 
    df.loc[df.Tm == "NOH", "Tm"] = "NOP"
    df.loc[df.Tm == "CHA", "Tm"] = "CHO"
    df.loc[df.Tm == "CHH", "Tm"] = "CHO"    
    df.loc[df.Tm == "SEA", "Tm"] = "OKC"
    df.loc[df.Tm == "VAN", "Tm"] = "MEM"
    df.loc[df.Tm == "NJN", "Tm"] = "BRK"
    
    return df

# draft dates collection: needs to be separately
abc = list(string.ascii_lowercase)
# no name with x-s
abc[23:25] = abc[24:26]
abc = abc[0:-1]
url_base = "http://www.basketball-reference.com/players/"
draft_df = pd.DataFrame(columns = ["Player", "From"])

#scraping the starting years
for l in range(len(abc)):
    url_draft = url_base + abc[l]
    # url
    html = urlopen(url_draft).read()
    soup = BeautifulSoup(html) 
    #create list of names of the Coaches
    column_headers = [th.getText() for th in soup.findAll("tr", limit = 2)[0].findAll("th")    ]
    player_names = [[ th.getText() for th in 
                        soup.findAll("tr")[1:][i].findAll("th")] for i in
                                    range(len(soup.findAll("tr")[1:]))   ] 
    draft_data = [[ td.getText() for td in 
                        soup.findAll("tr")[1:][i].findAll("td")] for i in
                                    range(len(soup.findAll("tr")[1:]))   ]
    
    player_names = pd.DataFrame(player_names)    
    draft_data = pd.DataFrame(draft_data)
    draft_data = pd.concat([player_names, draft_data], axis = 1)
    draft_data.columns = column_headers
    draft_data = draft_data[["Player", "From"]]
    draft_data["From"] = pd.to_numeric(draft_data["From"])
    
    draft_df = draft_df.append(draft_data)
    
###################################
#CREATING THE DATASET
###################################

for y in seasons: 
     url_s = "http://www.basketball-reference.com/leagues/NBA_{a}_advanced.html".format(a = y)
     df = nba_player_stats(url_s, y, varlist)
     df_nba_stats = df_nba_stats.append(df)

df_nba_stats.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_nba_stats.csv", 
                    sep = ";",
                    header = True) 

#if I do not want to download it again
df_nba_stats = pd.read_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_nba_stats.csv",
                    sep = ";",
                    index_col = 0)

draft_df.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/draft_df.csv", 
                    sep = ";",
                    header = True)  

 #if I do not want to download it again
draft_df = pd.read_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/draft_df.csv",
                    sep = ";",
                    index_col = 0)         
#####################################
#sort the data and save it
sl = ["Player", "Year"]
df_nba_stats_A = df_nba_stats.sort_values(by = sl, axis = 0)

#numeric conversion
numvarlist = ["Age", "G", "OWS", "DWS"]
final_varlist = ["Player", "Year", "Tm", "Age", "G", "OWS", "DWS"]
df_nba_stats_A = df_nba_stats_A[final_varlist]
for i in range(4):
    df_nba_stats_A[numvarlist[i]] = pd.to_numeric(df_nba_stats_A[numvarlist[i]])

#attach draft year
df_nba_stats_A = df_nba_stats_A.merge(draft_df, left_on = "Player", right_on = "Player", how = "left")
df_nba_stats_A["In_league"] = df_nba_stats_A["Year"] - df_nba_stats_A["From"] + 1
df_nba_stats_A.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_nba_stats_A.csv", 
                    sep = ";",
                    header = True) 

#☺basic descriptive stats
df_nba_stats_A.describe()

#yearly stats
df_nba_stats_A.groupby("Year").aggregate(np.mean)
df_nba_stats_A.groupby("Year").aggregate(np.median)

#Mechanism 1: players being on the same team with veteran players
#So create links between players who are at least 25 and those under 25 if same year same team
#so under 25 data are for construction of NW
df_young = df_nba_stats_A[4 > df_nba_stats_A["In_league"]]
#prime age players
df_prime = df_nba_stats_A[(df_nba_stats_A["In_league"] > 3) & (9 > df_nba_stats_A["In_league"])]
#all veteren players: >8 years in the league
df_old = df_nba_stats_A[df_nba_stats_A["In_league"] > 3]

#merge data by year, team
v = ["Player", "Year", "Tm"]

#to be a mentee
df_young_nodes = df_young[v].reset_index(drop=True)
#to be a mentor
df_old_nodes = df_old[v].reset_index(drop=True)

#take average of OWS DWS of prime time of players
stat_prime = df_prime.groupby("Player").aggregate(np.mean)
#take the average of the less than 25 of age
stat_rookie = df_young[df_young["In_league"] == 1].groupby("Player").aggregate(np.mean)

#prime stats
stat_prime["Mentee"] = stat_prime.index
sn = ["Mentee", "OWS", "DWS"]
stat_prime  = stat_prime[sn].reset_index(drop=True)
stat_prime.columns = ["Mentee", "OWS_prime", "DWS_prime"]

#rookie stats
stat_rookie["Mentee"] = stat_rookie.index
sn = ["Mentee", "OWS", "DWS"]
stat_rookie  = stat_rookie[sn].reset_index(drop=True)
stat_rookie.columns = ["Mentee", "OWS_rookie", "DWS_rookie"]

#control for rookie stats
stat_normalized = stat_prime.merge(stat_rookie, left_on = "Mentee", right_on = "Mentee", how = "left")

#we keep only those who were rookies in time frame
stat_normalized = stat_normalized[np.isnan(stat_normalized["OWS_rookie"]) == False]
stat_normalized["dOWS"] = stat_normalized["OWS_prime"] - stat_normalized["OWS_rookie"]
stat_normalized["dDWS"] = stat_normalized["DWS_prime"] - stat_normalized["DWS_rookie"]
stat_normalized = stat_normalized[["Mentee", "dOWS", "dDWS"]]
#THESE ARE THE WEIGHTS IN THE NETWORK

############################################
#II. Creating coach dataset
############################################

url_coach_base = "http://www.basketball-reference.com/coaches/"

#we do the following: create a list with the shortened versions of the coaches,
# go through the tags and download all tables, win out the info with years and teams

html = urlopen(url_coach_base).read()
soup = BeautifulSoup(html)  

#create list of names of the Coaches
column_headers = [th.getText() for th in soup.findAll("tr", limit = 2)[1].findAll("th")    ]
coach_name_data = [[ th.getText() for th in 
                    soup.findAll("tr")[2:][i].findAll("th")] for i in
                                range(len(soup.findAll("tr")[2:]))   ]
coach_name_data = pd.DataFrame(coach_name_data)
coach_name_data = pd.DataFrame(coach_name_data.ix[:, 0], columns = ["Coach"])

coach_name_data = coach_name_data[coach_name_data.Coach.str.contains("Coach") == False]
coach_name_data = coach_name_data[(coach_name_data.Coach.str.len() < 2) == False]
coach_name_data = coach_name_data.reset_index(drop=True)

#links to each coach: need to be separately created
link_list = list()
for link in soup.findAll('a', attrs={'href': re.compile("/coaches")}):
    a = str(link)
    a = re.findall(r'"[^"]*"', a)[0]
    a = a[1:-1]
    link_list.append(a)
coach_links = [link_list[i] for i in range(2,357)]
 
#SCRAPING THE COACH DATA
   
url_base = "http://www.basketball-reference.com"

df_coaches = pd.DataFrame(columns = ["Coach", "Year", "Tm"])
df_coaches_stat = pd.DataFrame(columns = ["Coach", "WL_pc"])
#define coach data scraper function
#03.28: I put the career averages in!
def coach_scrape(soup_c):    
    
    column_headers = [th.getText() for th in soup_c.findAll("tr", limit = 2)[1].findAll("th")]
    coach_data = [[td.getText() for td in 
                   soup_c.findAll("tr")[2:][i].findAll("td")] for i in 
                                 range(len(soup_c.findAll("tr")[2:])) ]
    coach_data2 = [[th.getText() for th in 
                   soup_c.findAll("tr")[2:][i].findAll("th")] for i in 
                                 range(len(soup_c.findAll("tr")[2:])) ]   
    
    df_c = pd.DataFrame(coach_data)
    
    tmp = pd.DataFrame(coach_data2)
    df_c = pd.concat([tmp, df_c], axis = 1)
    df_c.columns = column_headers
    #clear duplicates
    df_c = df_c.drop_duplicates(subset = "Season" , keep = "first")
    #clear mess
    df_c = df_c[df_c.Season.str.contains("-") == True]
    #needed variables are Seasons and Team
    #create year variable
    df_c["Year"] = df_c.Season.str.slice(0,4)
    df_c["Year"] = pd.to_numeric(df_c["Year"])
    df_c = df_c[["Year", "Tm", "Age"]]
    
    #correct for moving NBA teams: SEA -> OKC, NOH -> NOP, VAN -> MEM, CHA -> CHO CHH -> CHO, NJN -> BRK 
    df_c.loc[df_c.Tm == "NOH", "Tm"] = "NOP"
    df_c.loc[df_c.Tm == "CHA", "Tm"] = "CHO"
    df_c.loc[df_c.Tm == "CHH", "Tm"] = "CHO"    
    df_c.loc[df_c.Tm == "SEA", "Tm"] = "OKC"
    df_c.loc[df_c.Tm == "VAN", "Tm"] = "MEM"
    df_c.loc[df_c.Tm == "NJN", "Tm"] = "BRK" 
    
    return df_c

#get the coach stats
def coach_stat(soup_c):     
    coach_data = [[td.getText() for td in 
                   soup_c.findAll("tr")[2:][i].findAll("td")] for i in 
                                 range(len(soup_c.findAll("tr")[2:])) ]
    df_c = pd.DataFrame(coach_data)
    asd = df_c[pd.isnull(df_c[0]) == True].index.tolist()[0] -1
    c_stat = pd.DataFrame(df_c.loc[[asd]][6])
    c_stat.columns = ["WL_pc"]
    c_stat["WL_pc"] = pd.to_numeric(c_stat["WL_pc"])
    c_stat = c_stat.reset_index(drop=True)
    c_stat = c_stat.loc[[0]]
    return c_stat

#Run code
for c in range(len(coach_links)):    
    #create link
    url_c = url_base + coach_links[c]
    #BeautifulSoup
    html_c = urlopen(url_c).read()
    soup_c = BeautifulSoup(html_c)  
    
    #scrape the dataset
    df = coach_scrape(soup_c)
    #get the stat
    c_stat = coach_stat(soup_c)
    
    #put the coaches name to it
    name = pd.DataFrame(coach_name_data.loc[c, ["Coach"] ] )
    name = name.reset_index(drop = True)
    name.columns = ["Coach"]
    #attach coach name to the data
    df = pd.concat([name, df], axis = 1)
    df["Coach"] = df["Coach"][0]
    #put it into the big dataset
    df_coaches = df_coaches.append(df)
    
    #coaching stats:
    dfc = pd.concat([name, c_stat], axis = 1)
    df_coaches_stat = df_coaches_stat.append(dfc)
    

#reset indices 
df_coaches = df_coaches.reset_index(drop=True)
df_coaches_stat = df_coaches_stat.reset_index(drop=True)

df_coaches.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_coaches.csv", 
                    sep = ";",
                    header = True) 
#coaches' stat
df_coaches_stat.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_coaches_stat.csv", 
                    sep = ";",
                    header = True) 

#for loading the coaches data
df_coaches = pd.read_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_coaches.csv", 
                    sep = ";",
                    index_col = 0)

#############################
#III. Create the Network
#############################
#indices of all players
df_nba_index = df_nba_stats.groupby("Player").aggregate(np.mean).copy()
df_nba_index["Player"] = df_nba_index.index
df_nba_index = df_nba_index.reset_index(drop = True)
df_nba_index["MentorID"] = df_nba_index.index
df_nba_index["Mentor"] = df_nba_index["Player"]
df_nba_index = df_nba_index[["Mentor", "MentorID"]]

#indices of all coaches 
#of whom we have an index from his status as a player: attach one
#all the others: give a LARGE number as an index: 100000 start
df_coaches.columns = ["Age", "Mentor", "Tm", "Year"]
df_coaches_index = df_coaches.groupby("Mentor").aggregate(np.mean).copy()
df_coaches_index["Mentor"] = df_coaches_index.index
df_coaches_index = df_coaches_index.reset_index(drop = True)

#due to errors I am not going to consider the players and the coaches the same, there will be
#"coach" identities and "player" identities"

#df_coaches_index = df_coaches_index.merge(df_nba_index, on = "Mentor", how = "left")
#df_coaches_index = df_coaches_index[["Mentor", "MentorID"]]
#df_coaches_index["MentorID"][np.isnan(df_coaches_index["MentorID"]) == True] = df_coaches_index.index + 100000

df_coaches_index["MentorID"] = df_coaches_index.index + 100000
df_coaches_index = df_coaches_index[["Mentor", "MentorID"]]
                        
df_mentor_index = pd.concat([df_nba_index, df_coaches_index], axis = 0)
df_mentor_index = df_mentor_index.drop_duplicates(subset = "Mentor", keep = "first")
#mentee indices
df_mentee_index = df_nba_index
df_mentee_index.columns = ["Mentee", "MenteeID"]             
df_mentee_index = df_mentee_index.reset_index(drop=True)
 
#set of mentors: separately for players and coaches, and then append
#1. players: filter out links where players are both sides and age is 
#CHANGE: link counts matter => so not from left, but all
#link can be more than 1 time
df_links1 = df_old.merge(df_young, on=["Year", "Tm"], how = "left")
df_links1 = df_links1[["Player_x", "Year", "Tm", "Age_x", "Player_y", "Age_y"]]
df_links1 = df_links1[ (df_links1["Age_x"] > df_links1["Age_y"] )  ]
df_links1 = df_links1[ (df_links1["Player_x"] != df_links1["Player_y"])   ]
df_links1 = df_links1[["Player_x", "Player_y"]]
df_links1.columns = ["Mentor", "Mentee"]
#how many mentors did a guy have?
mt_l = df_links1.groupby("Mentee").aggregate(np.count_nonzero).copy()
mt_l["Mentee"] = mt_l.index
mt_l = mt_l.reset_index(drop = True)    
mt_l.columns = [["Mentor_total", "Mentee"]]

mt_l2 = df_links1.copy()
mt_l2["n"] = 1
mt_l2 = mt_l2.groupby(["Mentor","Mentee"]).size().reset_index(name="N")

#keep only the first, but attach the weights
df_links1 = df_links1.drop_duplicates(subset = ["Mentor", "Mentee"], keep = "first")

#2. coaches: filter out links where name it the same or age is not passing
df_links2 = df_coaches.merge(df_young, on=["Year", "Tm"], how = "left")
df_links2 = df_links2[["Mentor", "Year", "Tm", "Age_x", "Player", "Age_y"]]
df_links2 = df_links2[( df_links2["Age_x"] > df_links2["Age_y"] )  ]
df_links2 = df_links2[( df_links2["Mentor"] != df_links2["Player"] )  ]
df_links2 = df_links2[["Mentor", "Player"]]
df_links2.columns = ["Mentor", "Mentee"]
#df_links2 = df_links2.drop_duplicates(subset = ["Mentor", "Mentee"], keep = "first")

#how many mentors did a guy have?
mt_c = df_links2.groupby("Mentee").aggregate(np.count_nonzero).copy()
mt_c["Mentee"] = mt_c.index
mt_c = mt_l.reset_index(drop = True)    
mt_c.columns = [["Mentor_total", "Mentee"]]

mt_c2 = df_links2.copy()
mt_c2["n"] = 1
mt_c2 = mt_c2.groupby(["Mentor","Mentee"]).size().reset_index(name="N")

#attach weights to WS-s
df_links1 = df_links1.merge(mt_l, on = "Mentee", how = "left")
df_links1 = df_links1.merge(mt_l2, on = ["Mentor","Mentee"], how = "left")
df_links2 = df_links2.merge(mt_c, on = "Mentee", how = "left")
df_links2 = df_links2.merge(mt_c2, on = ["Mentor","Mentee"], how = "left")


##################
#LINKS
###################
df_links = pd.concat([df_links1, df_links2], axis = 0)
df_links = df_links.merge(stat_normalized, on = "Mentee", how = "left")
df_links = df_links[np.isnan(df_links["dOWS"]) == False]

#rescale them
df_links["dOWS"] = df_links["dOWS"] * df_links["N"] / df_links["Mentor_total"]
df_links["dDWS"] = df_links["dDWS"] * df_links["N"] / df_links["Mentor_total"]

#so link is really being mentored by, so we want weighted indegrees 
df_links = df_links[["Mentee", "Mentor", "dOWS", "dDWS"]]

#attach ID-s created
df_links = df_links.merge(df_mentee_index, on = "Mentee", how = "left")
df_links = df_links.merge(df_mentor_index, on = "Mentor", how = "left")

######################################
#Saving into appropriate formats
######################################

#########################
#1. Baseline version
#########################

#igraph in Python is too difficult to install, so I proceed with R
df_links.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_links.csv", 
                    sep = ";",
                    header = True) 

#for loading in
df_links = pd.read_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_links.csv",
                    sep = ";",
                    index_col = 0)

#for Gephi
#OWS gephi
df_links_gephi_OWS = df_links.copy()
df_links_gephi_OWS = df_links_gephi_OWS[["Mentee", "Mentor", "dOWS", "MenteeID", "MentorID"]]
df_links_gephi_OWS.columns = [["Mentee", "Mentor", "Weight", "Source", "Target"]]
df_links_gephi_OWS.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_links_gephi_OWS.csv", 
                    sep = ";",
                    header = True) 
#DWS gephi
df_links_gephi_DWS = df_links.copy()
df_links_gephi_DWS = df_links_gephi_DWS[["Mentee", "Mentor", "dDWS", "MenteeID", "MentorID"]]
df_links_gephi_DWS.columns =  [["Mentee", "Mentor", "Weight", "Source", "Target"]]
df_links_gephi_DWS.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_links_gephi_DWS.csv", 
                    sep = ";",
                    header = True) 

##################################################
#2. Alternative version: normalized variables
##################################################

#If someone actually "worsened" what should we do??
#solution: increase every value with the minimum to make it nonnegative
df_links_v2 = df_links.copy()
df_links_v2["dOWS"] = (df_links_v2["dOWS"] - np.mean(df_links_v2["dOWS"])) / np.std(df_links_v2["dOWS"])
df_links_v2["dDWS"] = (df_links_v2["dDWS"] - np.mean(df_links_v2["dDWS"])) / np.std(df_links_v2["dDWS"])
df_links_v2.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_links_v2.csv", 
                    sep = ";",
                    header = True) 

#for Gephi
#gephi OWS v2
df_links_v2_gephi_OWS = df_links_v2.copy()
df_links_v2_gephi_OWS = df_links_v2_gephi_OWS[["Mentee", "Mentor", "dOWS", "MenteeID", "MentorID"]]
df_links_v2_gephi_OWS.columns = [["Mentee", "Mentor", "Weight", "Source", "Target"]]
df_links_v2_gephi_OWS.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_links_v2_gephi_OWS.csv", 
                    sep = ";",
                    header = True) 

#gephi DWS v2
df_links_v2_gephi_DWS = df_links_v2.copy()
df_links_v2_gephi_DWS = df_links_v2_gephi_DWS[["Mentee", "Mentor", "dDWS", "MenteeID", "MentorID"]]
df_links_v2_gephi_DWS.columns =  [["Mentee", "Mentor", "Weight", "Source", "Target"]]
df_links_v2_gephi_DWS.to_csv("C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project/df_links_v2_gephi_DWS.csv", 
                    sep = ";",
                    header = True) 

