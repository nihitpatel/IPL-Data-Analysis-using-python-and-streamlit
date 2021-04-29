import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

matches = pd.read_csv('IPL Matches 2008-2020.csv')
deliveries = pd.read_csv('IPL Ball-by-Ball 2008-2020.csv')

matches["year"] = matches.date.apply(lambda x: int(x[:4]))
years_list = list(matches.year.unique())

year = st.selectbox("Year",years_list)

team_list = list(matches[(matches.year == year)].team1.unique())

team1 = st.selectbox("Team 1",team_list)
team_list.remove(team1)
team2 = st.selectbox("Team 2",team_list)

mat = matches[(matches.year == year) & (matches.team1.isin([team1,team2])) & (matches.team2.isin([team1,team2]))]

m = ["Date : " + i + "  |  Venue : " + j for i,j in zip(list(mat.date),list(mat.venue))]
select_match = st.selectbox("Select Match : ",m)

ind = m.index(select_match)

mat_detail = pd.DataFrame(mat.iloc[ind])

city = ["City",list(mat_detail.loc['city'])[0]]
date = ["Date",list(mat_detail.loc['date'])[0]]
venue = ["Venue",list(mat_detail.loc['venue'])[0]]
toss_w = ["Toss Winner",list(mat_detail.loc['toss_winner'])[0]]
toss_d = ["Toss Decision",str(list(mat_detail.loc['toss_decision'])[0]).capitalize()]
winner = ["Winner",list(mat_detail.loc['winner'])[0]]
result = ["Result","Won by " + str(int(list(mat_detail.loc['result_margin'])[0])) + " " + str(list(mat_detail.loc['result'])[0])]
potm = ["Player of the Match",list(mat_detail.loc['player_of_match'])[0]]
u1 = ["Umpire 1",list(mat_detail.loc['umpire1'])[0]]
u2 = ["Umpire 2",list(mat_detail.loc['umpire2'])[0]]
eli = ["Eliminator", "No" if list(mat_detail.loc['umpire1'])[0]=='N' else "Yes"]

final_table = pd.DataFrame([date,venue,toss_w,toss_d,winner,result,potm,u1,u2,eli],columns=["",""])

#tab = tabulate(final_table, tablefmt = 'fancy_grid',numalign="center",showindex=False)
st.dataframe(final_table)


full_data = deliveries[deliveries.id == mat.iloc[ind].id]
AgGrid(full_data)

cur_mat = deliveries[deliveries.id == mat.iloc[ind].id]
cur_mat["cur_over"] = cur_mat.over + (cur_mat.ball/10)
cur_mat = cur_mat.sort_values(by=['cur_over'])

cur_mat_1 = cur_mat[cur_mat.batting_team == team1].reset_index()
cur_mat_1["total_score"] = cur_mat_1.total_runs
for i in range(1,len(cur_mat_1.total_score)) :
    cur_mat_1.iloc[i,-1] +=  cur_mat_1.iloc[i-1,-1]

cur_mat_2 = cur_mat[cur_mat.batting_team == team2].reset_index()
cur_mat_2["total_score"] = cur_mat_2.total_runs
for i in range(1,len(cur_mat_2.total_score)) :
    cur_mat_2.iloc[i,-1] +=  cur_mat_2.iloc[i-1,-1]

cur_mat = pd.concat([cur_mat_1,cur_mat_2])
cur_mat.player_dismissed = cur_mat.player_dismissed.fillna(0)
cur_mat_1.player_dismissed = cur_mat_1.player_dismissed.fillna(0)
cur_mat_2.player_dismissed = cur_mat_2.player_dismissed.fillna(0)

marker1 = list(cur_mat_1[cur_mat_1.player_dismissed != 0].index)
marker2 = list(cur_mat_2[cur_mat_2.player_dismissed != 0].index)

plt.style.use("ggplot")
plt.figure(figsize=(10,6),dpi=80)
plt.plot('cur_over','total_score',data=cur_mat_1,marker='o',ms=6, markevery=marker1)
plt.plot('cur_over','total_score',data=cur_mat_2,marker='s',ms=6, markevery=marker2)
x=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
plt.xticks(x)
plt.legend([team1,team2])
st.pyplot(plt)

st.write("Scorecard of " + team1)
st.dataframe(pd.DataFrame(cur_mat_1.groupby(["batsman"])["batsman_runs"].sum()).reset_index())
st.dataframe(pd.DataFrame(cur_mat_1[cur_mat_1.is_wicket == 1].groupby(['bowler'])['is_wicket'].sum()).reset_index().rename(columns={'bowler':'Bowler','is_wicket':'Wickets'}))
st.write("Scorecard of " + team2)
st.dataframe(pd.DataFrame(cur_mat_2.groupby(["batsman"])["batsman_runs"].sum()).reset_index())
st.dataframe(pd.DataFrame(cur_mat_2[cur_mat_2.is_wicket == 1].groupby(['bowler'])['is_wicket'].sum()).reset_index().rename(columns={'bowler':'Bowler','is_wicket':'Wickets'}))
