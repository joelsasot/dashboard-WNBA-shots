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
from blockers_functions import *
from shotmaps import *
from timeline_functions import *
from shooter_functions import *
from avg_functions_shooter import *
from auxiliary_functions_avg import *
from timeline_functions_avg import *

st.set_page_config(layout="wide",    initial_sidebar_state='collapsed')
def check_layout():
    '''With JS evaluation script, gets the width and height of the device.
    Sleep a little to get the values from JS.
    Then define a layout state depending on which is bigger.
    '''
    width, height = streamlit_js_eval(js_expressions='window.parent.innerWidth'),streamlit_js_eval(js_expressions='window.parent.innerHeight')
    # height = streamlit_js_eval(js_expressions='window.parent.innerHeight')
    return width, height

st.markdown('''
            <style>
            .firstRow {height : 15vh;
                width : 100%}
            .secondRow {height : 30vh;
                width : 100%}
            </style>''', unsafe_allow_html = True)

st.write('<style>div.block-container{padding-top:0.8rem;}   .st-bb{background-color:transparent;color:black} </style>', unsafe_allow_html=True)
# w = st.session_state.understood['item'][0]
# h = st.session_state.understood['item'][1]
# st.write(w,h)

def color_selectbox(n_element:int, color:str):

    js = f'''
    <script>
    // Find all the selectboxes
    var selectboxes = window.parent.document.getElementsByClassName("stSelectbox");
    
    // Select one of them
    var selectbox = selectboxes[{n_element}];
    
    // Select only the selection div
    var selectregion = selectbox.querySelector('[data-baseweb="select"]');
    
    // Modify the color
    selectregion.style.backgroundColor = '{color}';
    selectregion.style.Color = '{"white"}';
    
    </script>
    '''
    st.components.v1.html(js, height=0)



def obtain_game_ids(data,team_1,team_1_location,team_2, team_2_location):
    filtered_data = filter_data(data,team_1,team_1_location,team_2, team_2_location,True)
    return sorted(list(filtered_data['game_id'].unique()))

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

def add_inside_data(data,values):
    data = temporal_data_preprocessing(data,values)
    data['minute'] = (data['qtr']-1)*10 + data['simple_timestamp']//60
    data['inside'] = data.apply(lambda row: is_inside(row,values),axis = 1)
    return data

def filter_data(data,team_1,team_1_location,team_2, team_2_location,H2H_mode,shot_result, shot_value,values):
    data = add_inside_data(data,values)
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

import pandas as pd
import altair as alt
import geopandas as gpd
from variables_shots import *

alt.data_transformers.enable('default', max_rows=None)

def data_filtering(data,team_name):

    team_data = data[data['shooting_team']==team_name]

    return team_data

def check_home_vs_away(filtered_data,team_1,team_1_location,team_2, team_2_location):
    if team_1 == team_2:
        if team_1_location != team_2_location and team_1_location!= 'All' and team_2_location !='All':
            filtered_data.loc[filtered_data['shooting_team']==filtered_data['home_team_name'],'shooting_team'] = team_1 + ' Home'
            filtered_data.loc[filtered_data['shooting_team']==filtered_data['away_team_name'],'shooting_team'] = team_1 + ' Away'
            team_1 = team_1 + ' '+team_1_location
            team_2 = team_2 + ' '+team_2_location
    return filtered_data,team_1,team_2



def filter_player_data(filtered_data,player_selection):
    if len(player_selection)!=0:
        return filtered_data[filtered_data['Name'].isin(player_selection)]
    return filtered_data

def check_players_teams(player_selection,filtered_data):
    teams = []
    filtered_data['Name'] = filtered_data['shooting_player'].apply(reduce_player_name)

    for player in player_selection:
        team = filtered_data[filtered_data['Name']==player]['shooting_team'].unique()
        if team not in teams:
            teams.append(team)
    return (len(teams) == 2 and len(player_selection)) or len(player_selection) <= 1

def main():

    with st.sidebar:
        WIDTH,HEIGHT = check_layout()
    st.header('WNBA Shots *comparative analysis*')
    
    data = pd.read_csv('clean_data.csv')
    player_team_dictionary = generate_player_team_dictionary(data)
    team_1,team_1_location,team_2, team_2_location, shot_result, shot_value,H2H_mode,game_id,values,Avg_Mode= define_filters(data)
    if not Avg_Mode:
        allowed = answer_H2H_check(check_H2H_mode(team_1,team_1_location,team_2, team_2_location,H2H_mode))
        if not allowed:
            st.write("\*-\*")

        else:
            keep_executing = True

            data = add_inside_data(data,values)
            team_data = data[data['shooting_team'].isin([team_1,team_2])]
            player_selector = alt.selection_point(fields = ["Name"])
            filtered_data = filter_data(data,team_1,team_1_location,team_2, team_2_location,H2H_mode,shot_result, shot_value,values)
            filtered_data,team_1,team_2 = check_home_vs_away(filtered_data,team_1,team_1_location,team_2, team_2_location)
            filtered_data['Name'] = filtered_data['shooting_player'].apply(reduce_player_name)
            custom_palette = alt.Scale(domain=[team_1,team_2],range=["#1b9e77","#d95f02" ])
            if game_id!= None:
                filtered_data = filtered_data[filtered_data['game_id']==game_id]
            player_selection = []
            if values[0]==values[1]:
                keep_executing = False
            if keep_executing:
                shooter_column, scatter_plot_column, blocker_column = st.columns([0.34,0.33,0.33],gap='large')
                with shooter_column:
                    shooter_container = st.container(border = False,height = int( HEIGHT* 0.64 * 0.6*0.82)+10)
                    with shooter_container:
                        filtered_data_shooter = filtered_data[filtered_data['inside']]
                        shooter_chart = shooters_chart(filtered_data_shooter,shot_result,player_selector,custom_palette,HEIGHT)
                        shooter_event = st.altair_chart(shooter_chart, key="alt_chart", on_select="rerun",use_container_width=True)
                        for k,v in shooter_event['selection'].items():
                            for i in shooter_event['selection'][k]:
                                player_selection.append(i['Name'])
                        filtered_data = filter_player_data(filtered_data,player_selection)
                        if len(player_selection)>2:
                            keep_executing = False  
                    keep_executing = check_players_teams(player_selection,filtered_data)
                    if keep_executing:
                        with scatter_plot_column:
                            data_scatter_plot = data[data['inside']]
                            if H2H_mode:
                                data_scatter_plot = data_scatter_plot[data_scatter_plot['game_id']==game_id]
                            scatter_plot = shooter_scatter_chart(data_scatter_plot, team_1,team_2,shot_result,player_selection,HEIGHT,WIDTH)
                            st.altair_chart(scatter_plot,use_container_width=True)
                        with blocker_column:
                            blocker_container = st.container(border = False,height = int( HEIGHT* 0.64 * 0.6*0.82)+15)
                            with blocker_container:
                                if shot_result!='Made' and shot_value!=1:
                                    filtered_data_blocker = filtered_data[filtered_data['inside']]

                                    blocker_chart =  blockers_chart(filtered_data_blocker,player_team_dictionary,player_selection,team_1,team_2,WIDTH,HEIGHT)
                                    st.altair_chart(blocker_chart,use_container_width=False)

            if keep_executing:
                
                with st.container(border = False):
                    shotmap_team1_column,timeline_column = st.columns([0.4,0.6])
                    url_geojson = 'https://raw.githubusercontent.com/joelsasot/WNBA-shots/main/court_zones_coordinates.geojson'
                    # url_geojson = 'https://raw.githubusercontent.com/joel-sasot/WNBA-shots-viz/main/court_zones_coordinates.geojson'
                    geoloc = alt.Data(url=url_geojson, format=alt.DataFormat(property='features',type='json'))
                    with shotmap_team1_column:
                        filtered_data_shotmap = filtered_data[filtered_data['inside']]
                        if shot_value!=1:
                                spatial_shot_distribution_chart = spatial_charts_concatenation(filtered_data_shotmap,geoloc,team_1,team_2,H2H_mode,WIDTH,HEIGHT,player_selection)
                                st.altair_chart(spatial_shot_distribution_chart)
                        else:
                            with st.container(border = True,height=int(HEIGHT*0.65*0.5)):
                                st.markdown(
                                    """
                                    <span style="color:gray;font-size:5">
                                        They are all taken from the same location!
                                    </span>
                                    """,
                                    unsafe_allow_html=True
                            )
                    with timeline_column:
                        timeline_container = st.container(border = False)
                        with timeline_container:
                            if H2H_mode:
                                point_difference = point_difference_chart(filtered_data,team_1,team_1_location,team_2,team_2_location,WIDTH,HEIGHT,values,custom_palette).properties(title = alt.TitleParams('Point difference through match',color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 15))
                                st.altair_chart(point_difference, use_container_width=True)
                                # st.write('A')
                            else:
                                title_timeline = define_timeline_title(shot_result)
                                timeline = timeline_chart(filtered_data,custom_palette,WIDTH,HEIGHT,values).properties(title = alt.TitleParams(title_timeline,color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 15))
                                st.altair_chart(timeline, use_container_width=True)

            else:
                st.write('Incompatible filter configuration.')
    else:
        if not H2H_mode:
            keep_executing = True
            
            data = add_inside_data(data,values)
            team_data = data[data['shooting_team'].isin([team_1,team_2])]
            player_selector = alt.selection_point(fields = ["Name"])
            filtered_data = filter_data_avg(data,H2H_mode,shot_result, shot_value,values)
            filtered_data,team_1,team_2 = check_home_vs_away(filtered_data,team_1,team_1_location,team_2, team_2_location)
            filtered_data['Name'] = filtered_data['shooting_player'].apply(reduce_player_name)
            custom_palette = alt.Scale(domain=[team_1,'Avg '+team_1,team_2,'Avg '+team_2,'Avg League'],range=["#1b9e77","#1b9e77","#d95f02","#d95f02",'black' ])
            if game_id!= None:
                filtered_data = filtered_data[filtered_data['game_id']==game_id]
            player_selection = []
            if values[0]==values[1]:
                keep_executing = False
            if keep_executing:
                shooter_column, scatter_plot_column, blocker_column = st.columns([0.34,0.33,0.33],gap='large')
                with shooter_column:
                    shooter_container = st.container(border = False,height = int( HEIGHT* 0.64 * 0.6*0.82)+10)
                    with shooter_container:
                        filtered_data_shooter = filtered_data[filtered_data['inside']]
                        shooter_chart = shooters_chart_avg(data,[team_1,team_2],shot_result,player_selector,custom_palette,HEIGHT)
                        shooter_event = st.altair_chart(shooter_chart, key="alt_chart", on_select="rerun",use_container_width=True)
                        for k,v in shooter_event['selection'].items():
                            for i in shooter_event['selection'][k]:
                                player_selection.append(i['Name'])
                        filtered_data = filter_player_data(filtered_data,player_selection)
                        if len(player_selection)>2:
                            keep_executing = False  
                    keep_executing = check_players_teams(player_selection,filtered_data)
                    if keep_executing:
                            with scatter_plot_column:
                                data_scatter_plot = data[data['inside']]
                                if H2H_mode:
                                    data_scatter_plot = data_scatter_plot[data_scatter_plot['game_id']==game_id]
                                scatter_plot = shooter_scatter_chart_avg(data_scatter_plot, team_1,team_2,shot_result,player_selection,HEIGHT,WIDTH)
                                st.altair_chart(scatter_plot,use_container_width=True)
                            with blocker_column:
                                blocker_container = st.container(border = False,height = int( HEIGHT* 0.64 * 0.6*0.82)+15)
                                with blocker_container:
                                    if shot_result!='Made' and shot_value!=1:
                                        filtered_data_blocker = filtered_data[filtered_data['inside']]
                                        blocker_chart =  blockers_chart(filtered_data_blocker,player_team_dictionary,player_selection,team_1,team_2,WIDTH,HEIGHT)
                                        st.altair_chart(blocker_chart,use_container_width=False)
                if keep_executing:
                    
                    with st.container(border = False):
                        shotmap_team1_column,timeline_column = st.columns([0.4,0.6])
                        url_geojson = 'https://raw.githubusercontent.com/joelsasot/WNBA-shots/main/court_zones_coordinates.geojson'
                        geoloc = alt.Data(url=url_geojson, format=alt.DataFormat(property='features',type='json'))
                        with shotmap_team1_column:
                            filtered_data_shotmap = filtered_data[filtered_data['inside']]
                            if shot_value!=1:
                                    spatial_shot_distribution_chart = spatial_charts_concatenation(filtered_data_shotmap,geoloc,team_1,team_2,H2H_mode,WIDTH,HEIGHT,player_selection)
                                    st.altair_chart(spatial_shot_distribution_chart)
                            else:
                                with st.container(border = True,height=int(HEIGHT*0.65*0.5)):
                                    st.markdown(
                                        """
                                        <span style="color:gray;font-size:5">
                                            They are all taken from the same location!
                                        </span>
                                        """,
                                        unsafe_allow_html=True
                                )
                        with timeline_column:
                            timeline_container = st.container(border = False)
                            with timeline_container:
                                if H2H_mode:
                                    point_difference = point_difference_chart(filtered_data,team_1,team_1_location,team_2,team_2_location,WIDTH,HEIGHT,values,custom_palette).properties(title = alt.TitleParams('Point difference through match',color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 15))
                                    st.altair_chart(point_difference, use_container_width=True)
                                    # st.write('A')
                                else:
                                    title_timeline = define_timeline_title(shot_result)
                                    timeline = timeline_chart_avg(filtered_data,custom_palette,WIDTH,HEIGHT,values,data).properties(title = alt.TitleParams(title_timeline,subtitle='Gray line represents the average team of the league', subtitleColor='gray',color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 15))
                                    st.altair_chart(timeline, use_container_width=True)
        else:
            st.write('*H2H mode* and *vs Avg mode* are not available yet :(')
main()  