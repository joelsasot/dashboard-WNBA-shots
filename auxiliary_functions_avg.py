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

def add_inside_data(data,values):
    data = temporal_data_preprocessing(data,values)
    data['minute'] = (data['qtr']-1)*10 + data['simple_timestamp']//60
    data['inside'] = data.apply(lambda row: is_inside(row,values),axis = 1)
    return data

def filter_data_avg(data,H2H_mode,shot_result, shot_value,values):
    data = add_inside_data(data,values)
    if shot_value!='All':
        data = data[data['max_value']==shot_value]
    if shot_result == 'Made':   
        data = data[data['made_shot']]
    elif shot_result == 'Missed':
        data = data[~data['made_shot']]
    elif shot_result == 'Accuracy':
        pass
    return data