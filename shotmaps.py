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


def impute_court_zone(row):
    x = row['coordinate_x']
    y = row['coordinate_y']
    point = (x,y)
    if row['max_value']==3:
        if is_point_inside_polygon(point,left_3point_lane) or is_point_inside_polygon(point,left_2point_polygon):
            return 'Left 3-point lane'
        if is_point_inside_polygon(point,right_3point_lane) or is_point_inside_polygon(point,right_2point_polygon):
            return 'Right 3-point lane'
        
        if is_point_inside_polygon(point,left_3point_side) or is_point_inside_polygon(point,left_2point_side):
            return 'Left 3-point side'
        if is_point_inside_polygon(point,right_3point_side) or is_point_inside_polygon(point,right_2point_side):
            return 'Right 3-point side'
        
        if is_point_inside_polygon(point,left_3point_outer):
            return 'Left 3-point outer'
        if is_point_inside_polygon(point,right_3point_outer):
            return 'Right 3-point outer'
        if x<=25: return 'Left 3-point outer'
        if 25<x: return 'Right 3-point outer'
    if row['max_value']==2:
        if is_point_inside_polygon(point,left_2point_polygon):
            return 'Left 2-point polygon'
        if is_point_inside_polygon(point,right_2point_polygon):
            return  'Right 2-point polygon'
        
        if is_point_inside_polygon(point,left_2point_side):
            return 'Left 2-point side'
        if is_point_inside_polygon(point,right_2point_side):
            return 'Right 2-point side'
        
        if is_point_inside_polygon(point,left_under_hoop):
            return 'Left under hoop'
        if is_point_inside_polygon(point,right_under_hoop):
            return 'Right under hoop'
        
        if is_point_inside_polygon(point,left_front_hoop):
            return 'Left front hoop'
        if is_point_inside_polygon(point,right_front_hoop):
            return 'Right front hoop'
        
        if is_point_inside_polygon(point,central_2point):
            return 'Behind hoop'
        if is_point_inside_polygon(point,behind_hoop):
            return 'Central 2-point'
        if x <=17.5: return 'Left 2-point side'
        if 33.5<=x: return 'Right 2-point side'
        if 17.5<x and x<33.5: return 'Central 2-point'

def is_point_inside_polygon(point, polygon):
    """
    Determine if a point is inside a polygon using the ray-casting algorithm.
    
    Args:
    - point: Tuple (x, y) representing the coordinates of the point.
    - polygon: List of tuples [(x1, y1), (x2, y2), ..., (xn, yn)] representing the vertices of the polygon.
    
    Returns:
    - True if the point is inside the polygon, False otherwise.
    """
    x, y = point
    n = len(polygon)
    inside = False

    # Iterate over the edges of the polygon
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]  # Wrap around to the first vertex at the end
        
        # Check if the point is on an edge or if the ray crosses this edge
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside

    return inside


def fill_empty_zones(team_data,zones):
    # Get unique made_shot values
    made_shot_values = team_data['made_shot'].unique()
    for zone in zones:
        for made_shot in made_shot_values:
            # Check if this combination exists
            if not ((team_data['zone_name'] == zone) & (team_data['made_shot'] == made_shot)).any():
                # Append row with count 0 if missing
                team_data = pd.concat([team_data, pd.DataFrame({'zone_name': [zone], 'made_shot': [made_shot], 'count': [0]})], ignore_index=True)

    return team_data

def create_shotmap_opacity(team_data,team_color,geoloc):
    team_data_agg = team_data.groupby(by='zone_name')['count'].sum().reset_index()
    max_value = team_data.groupby(by='zone_name')['count'].sum().reset_index()['count'].max()
    shotmap = alt.Chart(geoloc).mark_geoshape(
    stroke='transparent',
    strokeWidth=1
    ).encode(
        color = alt.value(team_color),
        opacity=alt.Opacity('count:Q', legend = None, scale=alt.Scale(domain=[0, max_value], range=[0, 1])),
        # tooltip='null'

    ).project(
    type='identity', reflectY=True
).transform_lookup(
        lookup='properties.zone_name',
        from_=alt.LookupData(team_data_agg, 'zone_name', ['count'])
    ).properties(view=alt.ViewConfig(strokeWidth=0))
    return shotmap

def create_base_chart(geoloc):
    base_chart =  alt.Chart(geoloc).mark_geoshape(
    fill='transparent',
    stroke='lightgray',
    strokeWidth=2,
    opacity = 0.3,
    # tooltip='null'
    ).encode().properties(view=alt.ViewConfig(strokeWidth=0))
    return base_chart


def create_highlight_chart(geoloc,highlight_on_hover):
    highlight_chart =  alt.Chart(geoloc).mark_geoshape(
        fill='transparent',
        # stroke='black',
        # strokeWidth=1
    # tooltip='null'

    ).encode(
            stroke=alt.condition(highlight_on_hover, alt.value("black"),alt.value("white")),
            opacity = alt.condition(highlight_on_hover, alt.value(1),alt.value(0.5)),
            strokeWidth = alt.condition(highlight_on_hover, alt.value(1),alt.value(0.2)),
    ).add_params(highlight_on_hover).properties(view=alt.ViewConfig(strokeWidth=0),title = '')
    return highlight_chart

def create_text_chart(team_data):
    
    text_chart = alt.Chart(team_data).mark_text(align='center',size = 12).encode(
    longitude = alt.X('lon:Q'),
    latitude = 'lat:Q',
    # opacity = alt.Opacity('count:Q', legend = None, scale=alt.Scale(domain=[0, max_value], range=[1, 1])),
    text = 'sum(count):N'
    ).properties(view=alt.ViewConfig(strokeWidth=0),title = '')
    return text_chart


def empty_chart(team_data,empty_HEIGHT,empty_WIDTH):
    empty_chart = alt.Chart(team_data).mark_text(align='center',size = 12).encode(
    ).properties(view=alt.ViewConfig(strokeWidth=0),height = empty_HEIGHT ,width = empty_WIDTH ,title = '')
    return empty_chart


def spatial_charts_concatenation(data,geoloc,team_1,team_2,H2H,WIDTH,HEIGHT,player_selection):
    if H2H:
        opacity = 'shared'
    else:
        opacity = 'independent'
    player_A,player_B = None,None
    if len(player_selection) == 1:
        player_A = player_selection[0] 
    if len(player_selection) == 2:
        player_A = player_selection[0] 
        player_B = player_selection[1] 
    player_1,player_2 = assign_players(player_A,player_B,team_1,team_2,data)
    highlight_on_hover = alt.selection_point(fields=['properties.zone_name'],empty='none',on = "mouseover")    
    team1_data = data[data['shooting_team']==team_1]
    team2_data = data[data['shooting_team']==team_2]
    if player_1!=None and player_2==None:
        spatial_shot_distribution_chart1 = spatial_shot_distribution(team1_data,geoloc,'#1b9e77',highlight_on_hover,WIDTH,HEIGHT,player_1)
        spatial_shot_distribution_chart2 = empty_chart(team2_data,WIDTH*0.85*0.25*0.9*470/500,WIDTH*0.85*0.25*0.9)
        return alt.hconcat(spatial_shot_distribution_chart1,spatial_shot_distribution_chart2,spacing = 0).properties(title = alt.TitleParams('Shotmap w/o freeshots',color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 25
                                                                                                              ))
    if player_2!=None and player_1==None:
        spatial_shot_distribution_chart1 = empty_chart(team1_data,WIDTH*0.85*0.25*0.9*470/500,WIDTH*0.85*0.25*0.9)
        
        spatial_shot_distribution_chart2 = spatial_shot_distribution(team2_data,geoloc,'#d95f02',highlight_on_hover,WIDTH,HEIGHT,player_2)
        return alt.hconcat(spatial_shot_distribution_chart1,spatial_shot_distribution_chart2,spacing = 0).properties(title = alt.TitleParams('Shotmap w/o freeshots',color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 25                                                                                                            ,subtitle = " ",subtitleColor='gray'
                                                                                                                                                                                                                                                                            ))
    spatial_shot_distribution_chart1 = spatial_shot_distribution(team1_data,geoloc,'#1b9e77',highlight_on_hover,WIDTH,HEIGHT,player_1)
    spatial_shot_distribution_chart2 = spatial_shot_distribution(team2_data,geoloc,'#d95f02',highlight_on_hover,WIDTH,HEIGHT,player_2)
    return alt.hconcat(spatial_shot_distribution_chart1,spatial_shot_distribution_chart2,spacing = 0).resolve_scale(opacity=opacity,y='shared').properties(title = alt.TitleParams('Shotmap w/o freeshots',color='black',fontSize = 18, fontWeight=600,anchor='start',dy = 25
                                                                                                                                            ,subtitle = "Hover over map for an easy zone comparison",subtitleColor='gray'
                                                                                                                                         
                                                                                                                                         ))
def spatial_shot_distribution(team_data,geoloc,color,highlight_on_hover,WIDTH,HEIGHT,player):
    # Free shots are removed
    team_data_wo_fs = team_data[team_data['max_value']!=1]
    team_data_wo_fs['zone_name'] = team_data_wo_fs.apply(impute_court_zone,axis = 1)
    team_data_wo_fs_byzone = team_data_wo_fs.groupby(by=['zone_name','made_shot']).size().reset_index().rename(columns = {0:'count'})
    # team_data_wo_fs_byzone = fill_empty_zones(team_data_wo_fs_byzone,zones)
    geoloc_text = gpd.read_file("court_zones_coordinates.geojson")

    team_geolocated = geoloc_text.merge(team_data_wo_fs_byzone,on='zone_name')

    base_chart = create_base_chart(geoloc)
    highlight_chart = create_highlight_chart(geoloc,highlight_on_hover)
    shotmap = create_shotmap_opacity(team_data_wo_fs_byzone,color,geoloc)
    custom_text_locations_team_valued = team_geolocated.merge(custom_text_locations, on='zone_name')
    text_chart = create_text_chart(custom_text_locations_team_valued)

    # base_chart = create_base_chart(team_geolocated)
    # highlight_chart = create_highlight_chart(team_geolocated)
    # shotmap = create_shotmap_opacity(team_geolocated,color)
    # custom_text_locations_team_valued = team_geolocated.merge(custom_text_locations, on='zone_name')
    # text_chart = create_text_chart(custom_text_locations_team_valued)
    # spatial_shot_distribution_chart = (shotmap ).properties(view=alt.ViewConfig(strokeWidth=0),title = '')
    team_name = team_data['shooting_team'].unique()[0]
    title_text = player if player != None else team_name
    spatial_shot_distribution_chart = (
                                   base_chart
                                   +
                                         highlight_chart
                                    +
                        shotmap+
                                         text_chart
                                         ).properties(view=alt.ViewConfig(strokeWidth=0), 
                                                      width = WIDTH*0.85*0.25*0.75,
                                                      height = WIDTH*0.85*0.25*0.9*470/500,
                        title = alt.TitleParams(
                            title_text,
                            anchor=  'middle',
                            fontSize=12,
                            color='gray',
                            dy = 40,
                        

                            
                        )




                                                      )
    # spatial_shot_distribution_chart = (shotmap + base_chart+ highlight_chart+text_chart).properties(view=alt.ViewConfig(strokeWidth=0),title = '')
    return spatial_shot_distribution_chart
    # spatial_shot_distribution_chart = (shotmap + base_chart+ highlight_chart+text_chart).properties(view=alt.ViewConfig(strokeWidth=0),title = '')

