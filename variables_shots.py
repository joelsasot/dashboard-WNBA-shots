import altair as alt
import pandas as pd
import altair as alt
import geopandas as gpd

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import base64

import base64
from io import BytesIO
from PIL import Image

from typing import Literal

import streamlit as st

left_3point_lane = [(0,0),(0,14),(5,14),(5,0)]
right_3point_lane = [(45,0),(45,14),(50,14),(50,0)]

left_2point_polygon = [(5,0),(5,14),(19,9.2),(19,0)]
right_2point_polygon = [(45,0),(45,14),(31,9.2),(31,0)]

behind_hoop = [(19,0),(19,4),(31,4),(31,0)]

left_under_hoop = [(19,0),(19,11.5),(25,11.5),(25,0)]
right_under_hoop = [(25,0),(25,11.5),(31,11.5),(31,0)]

left_front_hoop = [(19,11.5),(19,19),(25,19),(25,11.5)]
right_front_hoop = [(25,11.5),(25,19),(31,19),(31,11.5)]

left_2point_side = [(5,14),(17.5,23.77),(19,19),(19,9.2)]
right_2point_side = [(45,14),(33.5,23.77),(31,19),(31,9.2)]

central_2point = [(19,19),(17.5,23.77),(33.5,23.77),(31,19)]

left_3point_side = [(0,14),(0,47),(17.5,23.77),(5,14)]
right_3point_side = [(50,14),(45,14),(33.5,23.77),(50,47)]

left_3point_outer = [(17.5,23.77),(0,47),(25,47),(25,25)]
right_3point_outer = [(50,47),(25,47),(25,25),(33.5,23.77)]

zones = [['Right 2-point side',
 'Left 2-point polygon',
 'Right under hoop',
 'Left under hoop',
 'Left 3-point side',
 'Left 2-point side',
 'Right 3-point outer',
 'Right front hoop',
 'Right 3-point lane',
 'Right 3-point side',
 'Behind hoop',
 'Left 3-point lane',
 'Central 2-point',
 'Left 3-point outer',
 'Left front hoop',
 'Right 2-point polygon']]

highlight_courtzone_on_hover = alt.selection_point(fields=['zone_name'],empty='none',on = "mouseover")  

behind_hoop_text_loc = pd.DataFrame({'lon':[1.25],'lat':[42.02],'zone_name':['Behind hoop'],})
central_text_loc = pd.DataFrame({'lon':[1.25],'lat':[42.22],'zone_name':['Central 2-point'],})

left_lane_text_loc = pd.DataFrame({'lon':[1.025],'lat':[42.07],'zone_name':['Left 3-point lane'],})
right_lane_text_loc = pd.DataFrame({'lon':[1.475],'lat':[42.07],'zone_name':['Right 3-point lane'],})

left_polygon_text_loc = pd.DataFrame({'lon':[1.12],'lat':[42.0451],'zone_name':['Left 2-point polygon'],})
right_polygon_text_loc = pd.DataFrame({'lon':[1.38],'lat':[42.0451],'zone_name':['Right 2-point polygon'],})

left_2side_text_loc = pd.DataFrame({'lon':[1.13],'lat':[42.155],'zone_name':['Left 2-point side'],})
right_2side_text_loc = pd.DataFrame({'lon':[1.37],'lat':[42.155],'zone_name':['Right 2-point side'],})

left_3side_text_loc = pd.DataFrame({'lon':[1.07],'lat':[42.25],'zone_name':['Left 3-point side'],})
right_3side_text_loc = pd.DataFrame({'lon':[1.43],'lat':[42.25],'zone_name':['Right 3-point side'],})

left_front_text_loc = pd.DataFrame({'lon':[1.22],'lat':[42.1525],'zone_name':['Left front hoop'],})
right_front_text_loc = pd.DataFrame({'lon':[1.28],'lat':[42.1525],'zone_name':['Right front hoop'],})

left_under_text_loc = pd.DataFrame({'lon':[1.22],'lat':[42.0775],'zone_name':['Left under hoop'],})
right_under_text_loc = pd.DataFrame({'lon':[1.28],'lat':[42.0775],'zone_name':['Right under hoop'],})

left_outer_text_loc = pd.DataFrame({'lon':[1.17],'lat':[42.37],'zone_name':['Left 3-point outer'],})
right_outer_text_loc = pd.DataFrame({'lon':[1.34],'lat':[42.37],'zone_name':['Right 3-point outer'],})

custom_text_locations = pd.concat([
    behind_hoop_text_loc,
    central_text_loc,

    left_lane_text_loc,
    right_lane_text_loc,

    left_polygon_text_loc,
    right_polygon_text_loc,

    left_2side_text_loc,
    right_2side_text_loc,

    left_3side_text_loc,
    right_3side_text_loc,

    left_front_text_loc,
    right_front_text_loc,

    left_under_text_loc,
    right_under_text_loc,

    left_outer_text_loc,
    right_outer_text_loc,
])

quarter_chart_width = 150
quarter_chart_height= 110


def custom_divider():
    st.markdown(
        """
        <hr style="margin: 0px 0;"/>
        """, 
        unsafe_allow_html=True
    )
MARGINS = {
    "top": "1.875rem",
    "bottom": "0",
}

STICKY_CONTAINER_HTML = """
<style>
div[data-testid="stVerticalBlock"] div:has(div.fixed-header-{i}) {{
    position: sticky;
    {position}: {margin};
    background-color: white;
    z-index: 999;
}}
</style>
<div class='fixed-header-{i}'/>
""".strip()

# Not to apply the same style to multiple containers
count = 0



def sticky_container(
    *,
    height: int | None = None,
    border: bool | None = None,
    mode: Literal["top", "bottom"] = "top",
    margin: str | None = None,
):
    if margin is None:
        margin = MARGINS[mode]

    global count
    html_code = STICKY_CONTAINER_HTML.format(position=mode, margin=margin, i=count)
    count += 1

    container = st.container(height=height, border=border)
    container.markdown(html_code, unsafe_allow_html=True)
    return container