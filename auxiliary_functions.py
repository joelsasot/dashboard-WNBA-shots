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

def assign_players(player_A,player_B,team_1,team_2,dataset):
    player_1,player_2 = None,None
    if player_A != None:
        team_A = dataset[dataset['Name']==player_A]['shooting_team'].unique()[0]
        if team_A == team_1:
            player_1 = player_A
        if team_A == team_2:
            player_2 = player_A
    if player_B != None:
        team_B = dataset[dataset['Name']==player_B]['shooting_team'].unique()[0]
        if team_B == team_1:
            player_1 = player_B
        if team_B == team_2:
            player_2 = player_B
    return player_1,player_2

def define_filters(data):
    team_names = sorted(list(data['shooting_team'].unique()))
    team_names2 = sorted(list(data['shooting_team'].unique()))
    place_names = ['All','Home','Away']
    place_names2 = ['All','Home','Away']

 
    c1,c2,c3,c4,c5,c6,c7,c8,c9 = st.columns([0.14,0.09,0.14,0.09,0.09,0.09,0.15,0.11,0.09], gap='small')

    st.write('<style>div.block-container{padding-top:0.25rem;}   .st-bb{background-color:transparent;color:black} </style>', unsafe_allow_html=True)
    with c1:
        with stylable_container(
                key = "filter_team1", css_styles = """.st-bb {background-color:#1b9e77;color:white} .st-bb {stroke-width: 1.75px;stroke:white}"""
        ):
            team_1 = st.selectbox("Team 1:", team_names,index = 0)
    with c2:
        with stylable_container(
        key = "filter", css_styles = """ .st-bb{fill:black;stroke:black}"""
        ):
            team_1_location = st.selectbox("Location 1:", place_names,index = 0)
    with c3:
        with stylable_container(
                key = "filter_team2", css_styles = """.st-bb {background-color:#d95f02;color:white} .st-bb {stroke-width: 1.75px;stroke:white}"""
        ):
            team_2 = st.selectbox("Team 2:", team_names2,index = 2)
    with c4:
        with stylable_container(
        key = "filter2", css_styles = """ .st-bb{fill:black;stroke:black}"""
        ):
            team_2_location = st.selectbox("Location 2:", place_names2,index = 0)    
    with c5:
        with stylable_container(
        key = "filter3", css_styles = """ .st-bb{fill:black;stroke:black}"""
        ):
            shot_result = st.selectbox("Shot Result:", ['All','Made','Missed','Accuracy'],index = 0)

    with c6:
        with stylable_container(
        key = "filter4", css_styles = """ .st-bb{fill:black;stroke:black}"""
        ):
            shot_value = st.selectbox("Max Shot Value:", ['All',3,2,1],index = 0)   
    with c7:
            values = st.slider("Minute interval:", 0, 40, (0, 40))
    with c8:
        with stylable_container(
        key = "filter5", css_styles = """ .st-bb{fill:black;stroke:black}"""        ):
            H2H_mode = st.checkbox("# **H2H**")
            Avg_Mode = st.checkbox("# ***vs Avg* mode**")
            
    with c9:
        with stylable_container(
        key = "filter6", css_styles = """ .st-bb{fill:black;stroke:black}"""        ):
            game_id_list = []
            if H2H_mode:
                allowed = check_H2H_mode(team_1,team_1_location,team_2, team_2_location,H2H_mode,)
                if allowed==True:
                    game_id_list = obtain_game_ids(data,team_1,team_1_location,team_2, team_2_location,shot_result, shot_value)
            game_id = st.selectbox("Game ID:",game_id_list ,index = 0,disabled = (not H2H_mode))


    return team_1,team_1_location,team_2, team_2_location, shot_result, shot_value,H2H_mode,game_id,values,Avg_Mode
def obtain_game_ids(data,team_1,team_1_location,team_2, team_2_location,shot_result, shot_value):
    filtered_data = filter_data(data,team_1,team_1_location,team_2, team_2_location,True,shot_result, shot_value)
    return sorted(list(filtered_data['game_id'].unique()))
def check_H2H_mode(team_1,team_1_location,team_2, team_2_location,H2H_mode):
    if H2H_mode:
        if team_1== team_2:
            return "Same Team"
        if team_1_location == "All" or team_2_location=='All':
            return "All Location"
        if team_1_location == team_2_location:
            return "Same Location"
    else:
        if team_1== team_2 and ((team_1_location == "All" and team_2_location!='All') or (team_1_location != "All" and team_2_location=='All') or (team_1_location == "All" and team_2_location=='All')or (team_1_location == team_2_location)) :
            return 'Same team and "All" locations included'
    return True

def answer_H2H_check(check_H2H_mode):
    if check_H2H_mode == 'Same Team':
        st.write("You have selected the same team for the H2H analysis. Please, change either of them")
        return False
    if check_H2H_mode == 'Same Location':
        st.write("You have selected the same location for both teams in the H2H analysis. Please, change either of them.")
        return False
    if check_H2H_mode == 'All Location':
        st.write("You have selected 'All' as a location. Please, change it to either 'Home' or 'Away' to enable H2H analysis.")
        return False
    if check_H2H_mode =='Same team and "All" locations included':
        st.write("You have selected the same team twice and a set of incompatible locations. Please, change it to enable further analysis.")
        return False
    return True


def reduce_player_name(name):
    split_name = name.split(" ")
    Name = [word[0]+'. ' for word in split_name[:-1:]] + [split_name[-1]]
    return "".join(Name)



def team_location_filtering(team,team_data,team_location,H2H_mode,other_team):
    if team_location=="Home":
        team_data = team_data[team_data['home_team_name']==team]
        if H2H_mode:
            team_data = team_data[team_data['away_team_name']==other_team]
    elif team_location=="Away":
        team_data = team_data[team_data['away_team_name']==team]
        if H2H_mode:
            team_data = team_data[team_data['home_team_name']==other_team]
    return team_data

def filter_data(data,team_1,team_1_location,team_2, team_2_location,H2H_mode,shot_result, shot_value):
    
    if shot_value!='All':
        data = data[data['max_value']==shot_value]
    if shot_result == 'Made':   
        data = data[data['made_shot']]
    elif shot_result == 'Missed':
        data = data[~data['made_shot']]
    elif shot_result == 'Accuracy':
        pass
    team_1_data = data[data['shooting_team'].isin([team_1])]
    team_1_data = team_location_filtering(team_1,team_1_data,team_1_location,H2H_mode,team_2)

    team_2_data = data[data['shooting_team'].isin([team_2])]
    team_2_data = team_location_filtering(team_2,team_2_data,team_2_location,H2H_mode,team_1)

    return pd.concat([team_1_data,team_2_data])