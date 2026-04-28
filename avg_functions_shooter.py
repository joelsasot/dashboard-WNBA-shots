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


def adapt_criteria(criteria):
    if criteria=='Missed':
        return 'shots_missed'
    if criteria=='Made':
        return 'shots_made'
    if criteria == 'Points':
        return 'points_scored'
    if criteria == 'Accuracy':
        return 'accuracy'
    return 'All'
def sort_top_players(top_players,criteria):
    if criteria == 'Missed':
        return  top_players.sort_values(by=[adapt_criteria(criteria)],ascending=True)
    return  top_players.sort_values(by=[adapt_criteria(criteria)],ascending=False)


def create_scatterplot_dataset(data):
    shots_made_by_player = data[data['made_shot']].groupby(['shooting_team','shooting_player']).size().reset_index().rename(columns={0:'shots_made'})
    # shots_made_by_player['shots_missed'] = None

    shots_missed_by_player = data[~data['made_shot']].groupby(['shooting_team','shooting_player']).size().reset_index().rename(columns={0:'shots_missed'})
    # shots_missed_by_player['shots_made'] = None
    shots_by_player = shots_missed_by_player.merge(shots_made_by_player,how = 'outer', on=['shooting_team','shooting_player'])
    shots_by_player['All'] = shots_by_player['shots_missed'] + shots_by_player['shots_made'] 
    shots_by_player['accuracy'] = round((shots_by_player['shots_made'] / shots_by_player['All'])*100,2)
    
    avg_teams_shots = shots_by_player.groupby(by='shooting_team')[['shots_missed','shots_made','accuracy','All']].mean().reset_index()
    avg_teams_shots['Name'] = 'Avg '+avg_teams_shots['shooting_team']
    shots_by_player['Name'] = shots_by_player['shooting_player'].apply(reduce_player_name)
    multiteam_players = {}
    for player in shots_by_player['Name']:
        if len(shots_by_player[shots_by_player['Name']==player]['shooting_team'].unique())>1:
            # Then that player has been a top shooter for more than one team. Her data should not be shown together
            player_teams = shots_by_player[shots_by_player['Name']==player]['shooting_team'].unique()
            multiteam_players[player] = player_teams
    for player,v in multiteam_players.items():
        for team in v:
            last = ""
            if team[-4:] in ['Home','Away']:
                last = '-'+team[-4] 
            
            shots_by_player.loc[(shots_by_player['Name'] == player)&(shots_by_player['shooting_team']== team), 'Name'] = player + ' '+team[0:2]+last
    return shots_by_player,avg_teams_shots




def create_shooter_dataset_avg(data,teams,criteria):
    shots_made_by_player = data[data['made_shot']].groupby(['shooting_team','shooting_player']).size().reset_index().rename(columns={0:'shots_made'})
    # shots_made_by_player['shots_missed'] = None

    shots_missed_by_player = data[~data['made_shot']].groupby(['shooting_team','shooting_player']).size().reset_index().rename(columns={0:'shots_missed'})
    # shots_missed_by_player['shots_made'] = None
    shots_by_player = shots_missed_by_player.merge(shots_made_by_player,how = 'outer', on=['shooting_team','shooting_player'])
    shots_by_player['All'] = shots_by_player['shots_missed'] + shots_by_player['shots_made'] 
    shots_by_player['accuracy'] = round((shots_by_player['shots_made'] / shots_by_player['All'])*100,2)
    points_by_player = data.groupby(['shooting_team','shooting_player'])['shot_value'].sum().reset_index().rename(columns={'shot_value':'points_scored'})
    shots_by_player = shots_by_player.merge(points_by_player, on=['shooting_team','shooting_player'])
    shots_by_player_t1 = shots_by_player[shots_by_player['shooting_team']==teams[0]]
    avg_shots_by_player_t1 = shots_by_player_t1.groupby(by='shooting_team')[['shots_missed','shots_made','accuracy','All']].mean().reset_index()
    avg_shots_by_player_t1['Name'] = 'Avg '+teams[0]

    shots_by_player_t2 = shots_by_player[shots_by_player['shooting_team']==teams[1]]
    avg_shots_by_player_t2 = shots_by_player_t2.groupby(by='shooting_team')[['shots_missed','shots_made','accuracy','All']].mean().reset_index()
    avg_shots_by_player_t2['Name'] = 'Avg '+teams[1]
    shots_by_league = shots_by_player.copy()
    shots_by_league['shooting_team'] = 'Avg League'
    avg_shots_league = shots_by_league.groupby(by = 'shooting_team')[['shots_missed','shots_made','accuracy','All']].mean().reset_index()
    avg_shots_league['Name'] = 'Avg League'

    teams_players = shots_by_player[shots_by_player['shooting_team'].isin(teams)]

    top_players = teams_players.groupby('shooting_team', group_keys=False).apply(
        lambda group: group.nlargest(4, 'All')
    )
    top_players = sort_top_players(top_players,criteria)
    top_players['Name'] = top_players['shooting_player'].apply(reduce_player_name)
    multiteam_players = {}
    for player in top_players['Name']:
        if len(top_players[top_players['Name']==player]['shooting_team'].unique())>1:
            # Then that player has been a top shooter for more than one team. Her data should not be shown together
            player_teams = top_players[top_players['Name']==player]['shooting_team'].unique()
            multiteam_players[player] = player_teams
    for player,v in multiteam_players.items():
        for team in v:
            last = ""
            if team[-4:] in ['Home','Away']:
                last = '-'+team[-4] 
            
            top_players.loc[(top_players['Name'] == player)&(top_players['shooting_team']== team), 'Name'] = player + ' '+team[0:2]+last
    top_players_avg = pd.concat([top_players,avg_shots_league,avg_shots_by_player_t1,avg_shots_by_player_t2])
    return top_players_avg

def shooters_charting_avg(top_players,criteria,player_selector,custom_palette,HEIGHT):
    background_chart = alt.Chart(top_players).mark_bar(filled=True,align='center',size = 10).encode(
    y=alt.Y('Name:N',axis = alt.Axis(labelPadding=5,labelFontSize=8,labelColor='black', labelFontWeight=500,titleColor = 'gray',ticks = False,grid = False,domainColor='lightgray',domain = False,domainCap='round',title='',titleAngle=0,titlePadding=40 )).sort('-x'),
    x = alt.X(str(adapt_criteria(criteria))+':Q',axis = alt.Axis(labelPadding=5,labelFontSize=8,labelColor='dimgray',domain = False,grid = False,title = None)),
    color = alt.Color("shooting_team:N",scale = custom_palette,legend = None),
    # color = alt.value('lightgray'),
    opacity = alt.condition(
        player_selector,
        alt.value(1),
        alt.value(0.25)     # If false, opacity = 0.5
    ),
    ).properties(view=alt.ViewConfig(strokeWidth=0),height =  HEIGHT* 0.64 * 0.6*0.82,).add_params(player_selector)
    return background_chart

def shooters_chart_avg(data,teams,shot_result,player_selector,custom_palette,HEIGHT):
    top_players = create_shooter_dataset_avg(data,teams,shot_result)
    chart = shooters_charting_avg(top_players,shot_result,player_selector,custom_palette,HEIGHT)
    if shot_result == 'All':
        title_word = 'Top Shooters'
    elif shot_result == 'Made':
        title_word = 'Top Scorers'
    elif shot_result == 'Missed':
        title_word = 'Top Shot Missers'
    elif shot_result == 'Accuracy':
        title_word = 'Most Accurate Shooters'
    return chart.properties(title = alt.TitleParams(title_word,color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 25))


def shooter_scatter_chart_avg(data, team_1,team_2,shot_result,player_selection,HEIGHT,WIDTH):
    shots_by_player,avg_teams_shots = create_scatterplot_dataset(data)
    custom_palette = alt.Scale(domain=[team_1,team_2] + [team if team not in [team_1,team_2] else None for team in data['shooting_team'].unique()], range=["#1b9e77","#d95f02" ] + ['lightgray' for team in data['shooting_team'].unique()])    
    opacity_scale = alt.Scale(domain=[True,False],range=[1,0.1] )
    shots_by_player['selected'] = True
    if player_selection!=[]:
        shots_by_player.loc[~shots_by_player['Name'].isin(player_selection),'selected'] = False
    # st.write(shots_by_player.head())
    scatter_plot = alt.Chart(shots_by_player).mark_point(filled=True,size = 20).encode(
    y=alt.Y('accuracy:Q',axis = alt.Axis(ticks = False,grid = False,labels = False,domainColor='lightgray',domain = False,domainCap='round')).sort('-x'),
    x = alt.X('All:Q',axis = alt.Axis(gridOpacity=0.5,title = 'Total Shots',labelFontSize=8)),
    color = alt.Color("shooting_team:N",scale = custom_palette,legend = None),
    opacity = alt.Opacity('selected:N',scale = opacity_scale,legend = None),
    tooltip=['Name','shooting_team']
    ).properties(view=alt.ViewConfig(strokeWidth=0), height =  HEIGHT* 0.64 * 0.6*0.90,width=WIDTH*0.33*0.85*0.6)

    accuracy_reference_line = y_axis_scatter(shots_by_player)
    custom_palette_avg = alt.Scale(domain=[team_1,team_2] + [team if team not in [team_1,team_2] else None for team in data['shooting_team'].unique()], range=["#1b9e77","#d95f02" ] + ['black' for team in data['shooting_team'].unique()])    

    scatter_plot_avg = alt.Chart(avg_teams_shots).mark_point(filled=False,shape = "stroke").encode(
    y=alt.Y('accuracy:Q',axis = alt.Axis(ticks = False,grid = False,labels = False,domainColor='lightgray',domain = False,domainCap='round')).sort('-x'),
    x = alt.X('All:Q',axis = alt.Axis(gridOpacity=0.5,title = 'Total Shots',labelFontSize=8)),
    color = alt.Color("shooting_team:N",scale = custom_palette_avg,legend = None),
    opacity = alt.Opacity('selected:N',scale = opacity_scale,legend = None),
    tooltip=['Name','shooting_team']
    ).properties(view=alt.ViewConfig(strokeWidth=0), height =  HEIGHT* 0.64 * 0.6*0.90,width=WIDTH*0.33*0.85*0.6)

    accuracy_reference_line = y_axis_scatter(shots_by_player)

    
    return (accuracy_reference_line+scatter_plot_avg+scatter_plot).resolve_scale(y='shared',color = 'independent',size = 'independent').properties(title = alt.TitleParams('Total Attempts vs Accuracy',subtitle='Stroke shapes represent team averages',color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 25)).interactive()


def y_axis_scatter(shots_by_player):    
    min_count = shots_by_player['accuracy'].min()
    max_count = shots_by_player['accuracy'].max()
    count_domain_line = alt.Chart(pd.DataFrame({'All': [0, 0], 'accuracy': [min_count, max_count]})).mark_line(
        color='lightgray',
        strokeWidth=1
    ).encode(
        y=alt.Y('accuracy:Q',scale=alt.Scale(domain=[0, 100]),axis = alt.Axis(labelPadding=5,labels = True,labelColor='gray',titleColor = 'gray',values=[min_count, max_count],ticks = False,grid = False,domain = False,domainCap='round',titleFontWeight=100,titleAngle=0,titlePadding=40,title = 'Accuracy(%)' )),
        x=alt.value(0)  # Fixed at the x=0 position
    )
    return count_domain_line
