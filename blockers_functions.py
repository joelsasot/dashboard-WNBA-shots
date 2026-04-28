
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import altair as alt
from streamlit_extras.stylable_container import stylable_container
alt.data_transformers.enable('default', max_rows=None)
from variables_shots import *
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from auxiliary_functions import *
from shooter_functions import *



def generate_player_team_dictionary(data):
    player_team_df = data[['shooting_team','shooting_player']]
    player_team_df = player_team_df.drop_duplicates()
    player_team_dictionary = {}
    for player in data['shooting_player'].unique():
        player_data = data[data['shooting_player']==player]
        player_teams = dict(player_data['shooting_team'].value_counts())
        player_team_dictionary[player] = max(player_teams, key=player_teams.get)
    return player_team_dictionary

def create_blockers_dataset(team_data,player_team_dictionary,player_selection):
    team_data['reduced_name'] = team_data['shooting_player'].apply(reduce_player_name)
    if player_selection!= []:
        team_data = team_data[team_data['reduced_name'].isin(player_selection)]
    blockers_df = team_data.groupby(by=['shooting_team','blocking_player']).size().reset_index().rename(columns={0:'count'})
    if blockers_df.shape[0]==0:
        return pd.DataFrame()
    top_blockers = blockers_df.groupby('shooting_team', group_keys=False).apply(
        lambda group: group.nlargest(5, 'count')
    )
    top_blockers['team'] = top_blockers['blocking_player'].apply(lambda x: player_team_dictionary[x])
    top_blockers['reduced_name'] = top_blockers['blocking_player'].apply(reduce_player_name)
    return top_blockers


def assign_players(player_A,player_B,team_1,team_2,top_blockers):
    player_1,player_2 = None,None
    if player_A != None:
        team_A = top_blockers[top_blockers['reduced_name']==player_A]['shooting_team'].unique()[0]
        if team_A == team_1:
            player_1 = player_A
        if team_A == team_2:
            player_2 = player_A
    if player_B != None:
        team_B = top_blockers[top_blockers['reduced_name']==player_B]['shooting_team'].unique()[0]
        if team_B == team_1:
            player_1 = player_B
        if team_B == team_2:
            player_2 = player_B
    return player_1,player_2

def blockers_charting(top_blockers,team_1,team_2,custom_palette,player_selection,WIDTH,HEIGHT,team_data):
    player_A,player_B = None,None
    if len(player_selection) == 1:
        player_A = player_selection[0] 
    if len(player_selection) == 2:
        player_A = player_selection[0] 
        player_B = player_selection[1] 
    player_1,player_2 = assign_players(player_A,player_B,team_1,team_2,team_data)
    max_count = top_blockers['count'].max()
    values = [0,max_count]
    if max_count !=1 and max_count/2!=1 :
        half = max_count//2
        values = [0,half,max_count]
    
    against_1 = "" if player_2!=None and player_1==None else 'against '
    subtitle_1 = player_1 if player_1!=None else "" if player_2!=None and player_1==None else team_1
    against_2 = "" if player_1!=None and player_2==None else 'against '
    subtitle_2 = player_2 if player_2!=None else "" if player_1!=None and player_2==None else team_2
    background_chart_1 = alt.Chart(top_blockers[top_blockers['shooting_team']==team_1]).mark_bar(filled=True,align='center',size = 1).encode(
    y=alt.Y('reduced_name:N',axis = alt.Axis(labelPadding=5,labelFontSize=8,labelColor='black', labelFontWeight=500,titleColor = 'gray',ticks = False,grid = False,domainColor='lightgray',domain = False,domainCap='round',title='',titleAngle=0,titlePadding=40 )).sort('-x'),
    x = alt.X('count:Q',axis = None),
    color = alt.Color("team:N",scale = custom_palette,legend = None),

    ).properties(height = HEIGHT* 0.65 * 0.6 *0.5*0.65*0.91,
                 width = WIDTH*0.85*0.225*0.75,
                 view=alt.ViewConfig(strokeWidth=0),title =alt.TitleParams(against_1,subtitle=subtitle_1,subtitleColor='#1b9e77',color='gray',fontSize = 12, fontWeight=200,anchor='start',dy = 81,dx=-60))

    background_chart_2 = alt.Chart(top_blockers[top_blockers['shooting_team']==team_2]).mark_bar(filled=True,align='center',size = 1).encode(
        y=alt.Y('reduced_name:N',axis = alt.Axis(labelPadding=5,labelFontSize=8,labelColor='black', labelFontWeight=500,titleColor = 'gray',ticks = False,grid = False,domainColor='lightgray',domain = False,domainCap='round',title='',titleAngle=0,titlePadding=40 )).sort('-x'),
        x = alt.X('count:Q',axis = alt.Axis(values=values,labelPadding=5,labelFontSize=10,labelColor='dimgray',domain = False,grid = False,title = None)),
        color = alt.Color("team:N",scale = custom_palette,legend = None),

    ).properties(height = HEIGHT* 0.65 * 0.6 *0.5*0.65*0.91,
                 width = WIDTH*0.85*0.225*0.75,
                     view=alt.ViewConfig(strokeWidth=0),title =alt.TitleParams(against_2,subtitle=subtitle_2,color='gray',subtitleColor="#d95f02",fontSize = 12, fontWeight=200,anchor='start',dy = 81,dx=-60))
    together =  alt.vconcat(background_chart_1,background_chart_2,spacing = 10).resolve_scale(x = 'shared')
    return together

def empty_chart(team_data,empty_WIDTH,empty_HEIGHT):
    empty_chart = alt.Chart(team_data).mark_text(align='center',size = 12).encode(
    ).properties(view=alt.ViewConfig(strokeWidth=0),height = empty_HEIGHT ,width = empty_WIDTH ,title = '')
    return empty_chart

def blockers_chart(team_data,player_team_dictionary,player_selection,team_1,team_2,WIDTH,HEIGHT):
    top_blockers = create_blockers_dataset(team_data,player_team_dictionary,player_selection)
    if top_blockers.shape[0] == 0:
        return  empty_chart(team_data,10,10)
    custom_palette = alt.Scale(domain=[team_1,team_2] + [team if team not in [team_1,team_2] else None for team in top_blockers['team'].unique()],
                        range=["#1b9e77","#d95f02" ] + ['lightgray' for team in top_blockers['team'].unique()])    
    blockers_chart = blockers_charting(top_blockers,team_1,team_2,custom_palette,player_selection,WIDTH,HEIGHT,team_data)
    return blockers_chart.properties(title = alt.TitleParams('Top Blockers',color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 30))
