import streamlit as st  # Template
import pandas as pd
import plotly.express as px
from statistics import mean
import datetime
import boto3
# from getWeather import get_weather

st.set_page_config(layout="wide")

col1, col2 = st.columns(2)

s3 = boto3.resource(
    service_name='s3',
    region_name='eu-west-3',
    aws_access_key_id=st.secrets.db_credentials.aws_access_key_id,
    aws_secret_access_key=st.secrets.db_credentials.aws_secret_access_key
)

with col1:
    st.title('Weather app')

with col2:
    st.image("Logo_SPR.jpg", width=150)


# country choice 

selected_country = st.sidebar.selectbox("Select a country", options=['TR','FR','ES','HU','UA' ], help = "Select the coutry you need the data from")

@st.cache(max_entries = 1)
def load_data(country):
    obj = s3.Bucket('weatherdataspr').Object(country +'.csv').get()
    data = pd.read_csv(obj['Body'], index_col=0)

    # data = get_weather(country)
    data['year'] = 2020
    data['DATE'] = pd.to_datetime(data[['day', 'month','year']], dayfirst=True).dt.date
    # # data = pd.read_csv('summarizedfebruary.csv')
    # data = pd.read_csv("FR.zip")
    
    return data

# Load the data ####################

data = load_data(country = selected_country)



# Col names and selection of the good variable
col = data.columns.values.tolist()
col = ['temperature_c_2_m_above_gnd_max',
                            'temperature_c_2_m_above_gnd_min',
                            'temperature_c_2_m_above_gnd_avg',
                            'precipitation_total_grid_mm_surface_sum',
                            'wind_speed_km_per_h_2_m_above_gnd_avg',
                            'relative_humidity_pct_2_m_above_gnd_avg',
                            'shortwave_radiation_w_per_m2_surface_sum'
                            ]
variable_choice = st.sidebar.selectbox('Selection of the variable', col, help = "Select the weather variable that you want to be displayed on the map")

aggregation = st.sidebar.radio("Choose the aggregation", ("Average", 'Sum'))

#### DATE Selection ####################""
start_time =  st.sidebar.date_input(label= "Start date", value=datetime.date(2020,2,1), min_value=datetime.date(2020,2,1), max_value=datetime.date(2020,9,30))

end_time =  st.sidebar.date_input(label= "End date", value=datetime.date(2020,9,30), min_value=start_time, max_value=datetime.date(2020,9,30))

########################################################


# Perform the agregation 
@st.cache(max_entries = 1)
def do_the_aggregation(data, start,end,variable, aggregation):
    ### Filtering #########################################
    temp = data.loc[(data['DATE']>= start) & (data['DATE']<= end)]

    temp=temp[['lat','lon', variable]]
    temp[variable] = temp[variable].astype(float).round(2)
    
    if aggregation == 'Average' :
        aggreg = temp.groupby(['lat', 'lon']).aggregate('mean').reset_index()
    if aggregation == 'Sum':
        aggreg = temp.groupby(['lat', 'lon']).aggregate('sum').reset_index()
    
    return(aggreg)



# st.write(data.sample(10))


aggreg = do_the_aggregation(data, start= start_time, end = end_time, variable = variable_choice, aggregation=aggregation)


px.set_mapbox_access_token(open(".mapbox_token").read())

fig = px.scatter_mapbox(aggreg, lat=aggreg.lat, lon=aggreg.lon, color=round(aggreg[variable_choice],2), size=round(abs(aggreg[variable_choice]),2),
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10,
                        hover_name  = variable_choice)


fig.update_layout(title="Map of " + variable_choice)

fig.update_layout(mapbox_style="open-street-map",
                mapbox_center_lon=mean(data['lon']), mapbox_center_lat=mean(data['lat']), mapbox_zoom=5)

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=800)


st.header('Map of '+ variable_choice )

st.plotly_chart(fig, use_container_width=True)

