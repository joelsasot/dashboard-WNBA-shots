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

def correct_last_second_shots(timestamp):
    if timestamp == 600:
        return 599
    return timestamp

def is_inside(row,values):
    lower_bound = values[0]
    higher_bound = values[1]
    return lower_bound <= row['minute'] and row['minute']<higher_bound



def temporal_data_preprocessing(data,values):
    data['timestamp'] = 600 -  data['quarter_seconds_remaining'] 
    data['timestamp']  = data['timestamp'].apply(correct_last_second_shots)
    data['simple_timestamp'] = (data['timestamp']//60)*60
    data = data[data['qtr']<5]



    return data

def quarter_chart_line(team_data,quarter_num,custom_palette,strokeDashOption = [1,0]):
    team_data_qi = team_data[team_data['qtr']==quarter_num]
    if strokeDashOption != [1,0]:
        team_data_qi = team_data_qi[team_data_qi['made_shot']==True]
    # st.write(team_data_qi[['qtr','simple_timestamp','inside']].head())
    # st.write(values)
    team_data_qi['Minute'] = team_data_qi['minute']+1
    opacity_scale = alt.Scale(domain=[True,False],range=[1,0.3] )
    chart_qi = alt.Chart(team_data_qi).mark_line(    strokeDash=strokeDashOption).encode(
    x=alt.X('simple_timestamp:Q',axis = alt.Axis(labelColor='gray',titleColor = 'black',labels =False,ticks = False,grid = False,domain = True,domainCap='round',domainColor='lightgray',title='',titleFontWeight=100,)),
    # x=alt.X('simple_timestamp:Q',axis = alt.Axis(labelColor='gray',titleColor = 'black',labels =False,ticks = False,grid = False,domain = False,domainCap='round',domainColor='dimgray',title='Q'+str(quarter_num),titleFontWeight=100,)),
    y=alt.Y('sum(count):Q',axis = alt.Axis(labelPadding=5,labelColor='black',labels =False,titleColor = 'gray',ticks = False,grid = False,domain = False,domainCap='round',titleFontWeight=100,title = None,titleAngle=0,titlePadding=40 )),
    color = alt.Color("shooting_team:N",scale = custom_palette,legend = None),
    opacity = alt.Opacity('inside:N',scale = opacity_scale,legend = None),
    tooltip = ['Minute']
    ).properties(
        title=alt.TitleParams('Q'+str(quarter_num),fontSize=12,color='black',fontWeight=300,anchor = 'middle',dy = 35),
        view=alt.ViewConfig(strokeWidth=0)
    )
    return chart_qi

def y_axis_reference(team_data,limit):    
    min_count = team_data.groupby(by=['simple_timestamp','qtr','shooting_team'])['count'].sum().reset_index()['count'].min()
    max_count = team_data.groupby(by=['simple_timestamp','qtr','shooting_team'])['count'].sum().reset_index()['count'].max()
    count_domain_line = alt.Chart(pd.DataFrame({'simple_timestamp': [0, 0], 'count': [min_count, max_count]})).mark_line(
        color='lightgray',
        strokeWidth=1
    ).encode(
        y=alt.Y('count:Q',scale=alt.Scale(domain=[0, limit]),axis = alt.Axis(labelPadding=5,labels = True,labelColor='gray',titleColor = 'gray',values=[min_count, max_count],ticks = False,grid = False,domain = False,domainCap='round',titleFontWeight=100,titleAngle=0,titlePadding=40 )),
        x=alt.value(0)  # Fixed at the x=0 position
    )
    return count_domain_line

    
def generate_total_quarter_background(team_data,quarter_num,custom_palette,variable):
    team_data = team_data[team_data['inside']]
    
    team_data_qi = team_data[team_data['qtr']==quarter_num]
    if team_data_qi.shape[0]==0:
        return empty_chart(team_data,10,10)
    team_data_qi = team_data_qi.groupby(by=['shooting_team'])[variable].sum().reset_index()
    team_data_qi['winner'] = team_data_qi[variable] == team_data_qi[variable].max()
    team_data_qi['winner'] = team_data_qi['winner'].apply(lambda x: 'winner' if x else 'loser')

    background_chart = alt.Chart(team_data_qi).mark_rect(filled=False,align='center',size = 500,).encode(
    y=alt.Y('shooting_team:N',axis = alt.Axis(labelPadding=5,labelColor='gray',titleColor = 'gray',labels = False,ticks = False,grid = False,domain = False,domainCap='round',title='',titleFontWeight=100,titleAngle=0,titlePadding=40 )),

    color = alt.Color("shooting_team:N",scale = custom_palette,legend = None),
    opacity=alt.condition(
        alt.datum.winner=="winner",  # Condition on the 'winner' attribute
        alt.value(0.5),      # If true, opacity = 1
        alt.value(0)     # If false, opacity = 0.5
    ),
    ).properties(view=alt.ViewConfig(strokeWidth=0),title = '')
    return background_chart

def obtain_max_difference(team_data):
    team_data_agg = team_data.groupby(by=['shooting_team','qtr'])['count'].sum().reset_index()
    max_difference = 0
    for qtr in team_data_agg['qtr'].unique():
        team_data_agg_qtr = team_data_agg[team_data_agg['qtr']==qtr]
        max_difference_candidate = (team_data_agg_qtr['count'] - team_data_agg_qtr['count'].min()).max()
        if max_difference_candidate > max_difference:
            max_difference = max_difference_candidate
    return max_difference


def generate_total_quarter(team_data,quarter_num,custom_palette,variable):
    team_data = team_data[team_data['inside']]
    team_data_qi = team_data[team_data['qtr']==quarter_num]
    if team_data_qi.shape[0]==0:
        return empty_chart(team_data,10,10)
    team_data_qi = team_data_qi.groupby(by=['shooting_team'])[variable].sum().reset_index()
    team_data_qi['winner'] = team_data_qi[variable] == team_data_qi[variable].max()
    team_data_qi['winner'] = team_data_qi['winner'].apply(lambda x: 'winner' if x else 'loser')

    text_chart = alt.Chart(team_data_qi).mark_text(align='center',size = 12).encode(
    y = 'shooting_team:N',
    color = alt.Color("shooting_team:N",scale = custom_palette,legend = None),

    text = 'sum('+variable+'):N'
    ).properties(view=alt.ViewConfig(strokeWidth=0),title = '')
    return text_chart

def total_shots(team_data,custom_palette,variable):
    team_data = team_data[team_data['inside']]
    team_data_total = team_data.groupby(by=['shooting_team'])[variable].sum().reset_index()
    team_data_total['winner'] = team_data_total[variable] == team_data_total[variable].max()
    background_chart = alt.Chart(team_data_total).mark_rect(filled=True,align='center',size = 1000,).encode(
    y=alt.Y('shooting_team:N',axis = alt.Axis(labelPadding=5,labelColor='gray',titleColor = 'gray',labels = False,ticks = False,grid = False,domain = False,domainCap='round',title='',titleFontWeight=100,titleAngle=0,titlePadding=40 )),

    color = alt.Color("shooting_team:N",scale = custom_palette,legend = None),
    opacity=alt.condition(
        alt.datum.winner,  # Condition on the 'winner' attribute
        alt.value(0.2),      # If true, opacity = 1
        alt.value(0)     # If false, opacity = 0.5
    ),
    ).properties(view=alt.ViewConfig(strokeWidth=0),title = '')

    text_chart = alt.Chart(team_data_total).mark_text(align='center',size = 12).encode(
    y = 'shooting_team:N',
    color = alt.Color("shooting_team:N",scale = custom_palette,legend = None),

    text = 'sum('+variable+'):N'
    ).properties(view=alt.ViewConfig(strokeWidth=0),title = '')
    return background_chart + text_chart
    
def empty_chart(team_data,empty_WIDTH,empty_HEIGHT):
    empty_chart = alt.Chart(team_data).mark_text(align='center',size = 12).encode(
    ).properties(view=alt.ViewConfig(strokeWidth=0),height = empty_HEIGHT ,width = empty_WIDTH ,title = '')
    return empty_chart


def timeline_chart(team_data,custom_palette,WIDTH,HEIGHT,values):
    team_data = temporal_data_preprocessing(team_data,values)

    quarter_chart_width = WIDTH * 0.85 * 0.6 * 0.25 *0.77
    quarter_chart_height = HEIGHT* 0.65 * 0.6 *0.8
    quarter_total_WIDTH = WIDTH* 0.85 * 0.6 *0.1
    quarter_total_height = HEIGHT* 0.65 * 0.6 *0.1
    team_data_agg = team_data.groupby(by=['simple_timestamp','shooting_team','qtr','made_shot']).size().reset_index().rename(columns={0:'count'})
    team_data_agg['minute'] = (team_data_agg['qtr']-1)*10 + team_data_agg['simple_timestamp']//60
    team_data_agg['inside'] = team_data_agg.apply(lambda row: is_inside(row,values),axis = 1)
    q1_text =(generate_total_quarter_background(team_data_agg,1,custom_palette,'count') + generate_total_quarter(team_data_agg,1,custom_palette,'count')).properties(width=quarter_chart_width,height = quarter_total_height)
    q2_text =(generate_total_quarter_background(team_data_agg,2,custom_palette,'count') + generate_total_quarter(team_data_agg,2,custom_palette,'count')).properties(width=quarter_chart_width,height = quarter_total_height)
    q3_text =(generate_total_quarter_background(team_data_agg,3,custom_palette,'count') + generate_total_quarter(team_data_agg,3,custom_palette,'count')).properties(width=quarter_chart_width,height = quarter_total_height)
    q4_text =(generate_total_quarter_background(team_data_agg,4,custom_palette,'count') + generate_total_quarter(team_data_agg,4,custom_palette,'count')).properties(width=quarter_chart_width,height = quarter_total_height)

    limit = team_data_agg.groupby(by=['simple_timestamp','qtr','shooting_team'])['count'].sum().reset_index()['count'].max()
    
    q1 = (y_axis_reference(team_data_agg[team_data_agg['qtr']==1],limit)+quarter_chart_line(team_data_agg,1,custom_palette)).properties(width=quarter_chart_width,height = quarter_chart_height)
    q2 = (y_axis_reference(team_data_agg[team_data_agg['qtr']==2],limit)+quarter_chart_line(team_data_agg,2,custom_palette)).properties(width=quarter_chart_width,height = quarter_chart_height)
    q3 = (y_axis_reference(team_data_agg[team_data_agg['qtr']==3],limit)+quarter_chart_line(team_data_agg,3,custom_palette)).properties(width=quarter_chart_width,height = quarter_chart_height)
    q4 = (y_axis_reference(team_data_agg[team_data_agg['qtr']==4],limit)+quarter_chart_line(team_data_agg,4,custom_palette)).properties(width=quarter_chart_width,height = quarter_chart_height)

    q1_complete = alt.vconcat(q1,q1_text,spacing = 2,center = True)
    q2_complete = alt.vconcat(q2,q2_text,spacing = 2)
    q3_complete = alt.vconcat(q3,q3_text,spacing = 2)
    q4_complete = alt.vconcat(q4,q4_text,spacing = 2)
    total_chart = alt.vconcat(empty_chart(team_data_agg, quarter_total_WIDTH,quarter_chart_height
                              ),
                              total_shots(team_data_agg,custom_palette,'count').properties(
                                  width =quarter_chart_width*0.4,
                                  height = quarter_total_height,
                              ),spacing = 2)
    timeline  = alt.hconcat(q1_complete,q2_complete,q3_complete,q4_complete,spacing = 1)
    return alt.hconcat(timeline,total_chart,spacing = 5)


def create_point_difference_dataset(teams_data,values):
    team_data = temporal_data_preprocessing(team_data,values)
    team_data_agg = team_data.groupby(by=['simple_timestamp','shooting_team','qtr','made_shot'])['shot_value'].sum().reset_index().rename(columns={0:'count'})
    team_data_agg['inside'] = team_data_agg.apply(lambda row: is_inside(row,values),axis = 1)
    
def temporal_data_preprocessing_area(data):
    data['timestamp'] = 600 -  data['quarter_seconds_remaining'] 
    data['simple_timestamp'] = (data['timestamp']//60)*60
    data = data[data['qtr']<5]
    return data

def starting_point_difference_df(team_data):
    team_data = team_data[['game_id','timestamp','qtr','team1_score','team2_score']].drop_duplicates()
    team_data['quarter_timestamp'] = team_data['timestamp'] + (team_data['qtr']-1)*600

    
    team_data['simple_quarter_timestamp'] = (team_data['quarter_timestamp']//60)*60

    team_data['difference'] = team_data['team1_score'] - team_data['team2_score'] 
    filtered_data = team_data.loc[team_data.groupby(['simple_quarter_timestamp'])['difference'].transform(
        lambda x: abs(x).idxmax()
    )]
    filtered_data = filtered_data.drop_duplicates().reset_index()
    return filtered_data

def impute_winner(row):
    if row['difference']>0:
        return '1'
    if row['difference']<0:
        return '2'
    return '0'

def imputing_zero_values(filtered_data):
    # Find the indices where the sign changes
    sign_changes = (
        filtered_data['difference'].shift(1) * filtered_data['difference'] < 0
    ) 
    change_indices = sign_changes[sign_changes].index.tolist()

    # Insert new rows at the points of sign changes
    new_rows = []
    for idx in change_indices:
        if idx > 0:  # Ensure there's a previous row to compare
            # Compute the middle quarter_timestamp
            prev_ts = filtered_data.loc[idx - 1, 'simple_quarter_timestamp']

            curr_ts = filtered_data.loc[idx, 'simple_quarter_timestamp']
            mid_ts = (prev_ts + curr_ts) / 2
            
            # Append the new row
            new_rows.append({'simple_quarter_timestamp': mid_ts, 'difference': 0})

    # Create a new dataframe with the additional rows
    new_data = pd.concat(
        [filtered_data, pd.DataFrame(new_rows)],
        ignore_index=True
    ).sort_values(by='simple_quarter_timestamp').reset_index(drop=True)
    return new_data



def area_chart(new_data,WIDTH,HEIGHT):
    color_scale = alt.Scale(domain=["1","2",'0'],range=["#1b9e77","#d95f02",'gray'] )
    chart = alt.Chart(new_data).mark_area().encode(
        x=alt.X('simple_quarter_timestamp:Q', title='Minute',
                axis = None
                
                ),
        y=alt.Y('difference:Q', title='Point Difference', impute={'value': 0},
                            axis = alt.Axis(
                    grid = False,
                    ticks = False,
                    values = [0,new_data['difference'].max(),new_data['difference'].min()],
                    title = None,
                )
                
                ),
        color=alt.Color('winner:N',scale = color_scale,legend = None),
        opacity = alt.value(0.5)
    ).properties(
        width=WIDTH * 0.85 * 0.6  *0.87,
        height=HEIGHT* 0.65 * 0.6 *0.8
    )
    return chart
def vertical_line_charting(vertical_timestamp):
    vertical_line = alt.Chart(pd.DataFrame({'simple_quarter_timestamp': [vertical_timestamp]})).mark_rule(
        color='lightgray', strokeWidth=2
    ).encode(
        x='simple_quarter_timestamp'
    )
    return vertical_line


def point_difference_chart(data,team_1,team_1_location,team_2,team_2_location,WIDTH,HEIGHT,values,custom_palette):
    data = temporal_data_preprocessing_area(data)
    team_data = data[data['shooting_team'].isin([team_1,team_2])]
    team_data['team1_score'] = team_data.apply(lambda row: row['home_score'] if team_1_location=='Home' else row['away_score'],axis=1 )
    team_data['team2_score'] = team_data.apply(lambda row: row['home_score'] if team_2_location=='Home' else row['away_score'],axis=1 )
   
    filtered_data = starting_point_difference_df(team_data)
    new_data = imputing_zero_values(filtered_data)
    new_data['winner'] = new_data.apply(lambda row:impute_winner(row),axis = 1)
    new_data = new_data[['winner','qtr','simple_quarter_timestamp','difference']]
    chart = area_chart(new_data,WIDTH,HEIGHT)
    q12 = vertical_line_charting(600)
    q23 = vertical_line_charting(1200)
    q34 = vertical_line_charting(1800)
    team_data_points = temporal_data_preprocessing(team_data,values)
    team_data_points = team_data_points.groupby(by=['simple_timestamp','shooting_team','qtr'])['shot_value'].sum().reset_index()
    team_data_points['minute'] = (team_data_points['qtr']-1)*10 + team_data_points['simple_timestamp']//60
    team_data_points['inside'] = team_data_points.apply(lambda row: is_inside(row,values),axis = 1)
    
    quarter_chart_width = WIDTH * 0.85 * 0.6 * 0.25 *0.86
    quarter_chart_height = HEIGHT* 0.65 * 0.6 *0.6
    quarter_total_WIDTH = WIDTH* 0.85 * 0.6 *0.1
    quarter_total_height = HEIGHT* 0.65 * 0.6 *0.1

    q1_text =(generate_total_quarter_background(team_data_points,1,custom_palette,'shot_value') + generate_total_quarter(team_data_points,1,custom_palette,'shot_value')).properties(width=quarter_chart_width,height = quarter_total_height)
    q2_text =(generate_total_quarter_background(team_data_points,2,custom_palette,'shot_value') + generate_total_quarter(team_data_points,2,custom_palette,'shot_value')).properties(width=quarter_chart_width,height = quarter_total_height)
    q3_text =(generate_total_quarter_background(team_data_points,3,custom_palette,'shot_value') + generate_total_quarter(team_data_points,3,custom_palette,'shot_value')).properties(width=quarter_chart_width,height = quarter_total_height)
    q4_text =(generate_total_quarter_background(team_data_points,4,custom_palette,'shot_value') + generate_total_quarter(team_data_points,4,custom_palette,'shot_value')).properties(width=quarter_chart_width,height = quarter_total_height)
    total_chart = alt.vconcat(empty_chart(team_data_points, quarter_total_WIDTH,quarter_chart_height*1.35
                              ),
                              total_shots(team_data_points,custom_palette,'shot_value').properties(
                                  width =quarter_chart_width*0.4,
                                  height = quarter_total_height,
                              ),spacing = 2)
    
    q_text = alt.hconcat(q1_text,q2_text,q3_text,q4_text,spacing = 0)



    area_complete = (chart+ q12+q23+q34)
    chart = alt.vconcat(area_complete,q_text,spacing = 0).resolve_scale(x = 'independent',y = 'independent')
    return alt.hconcat(chart,total_chart,spacing = 0).resolve_scale(x = 'independent',y = 'independent')



def define_timeline_title(shot_result):
    if shot_result =='Accuracy':
        return 'Accuracy throughout the match'
    elif shot_result=='All':
        return 'Shots through the match'
    else:
        return shot_result+' shots throghout the match'

    # return alt.vconcat(area_complete,q_text,spacing = 5)