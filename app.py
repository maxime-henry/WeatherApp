import streamlit as st  # Template
import pandas as pd
import plotly.express as px
from statistics import mean
# from getWeather import get_weather

st.set_page_config(layout="wide")

col1, col2 = st.columns(2)


with col1:
    st.title('Weather app')

with col2:
    st.image("Logo_SPR.jpg", width=150)

@st.cache(max_entries = 1)
def load_data(selected_country = 'FR'):
    # data = pd.read_csv('summarizedfebruary.csv')
    data = pd.read_csv("summarizedfebruary.zip")
    # data = get_weather(country=selected_country)
    data['year'] = 2020
    data['DATE'] = pd.to_datetime(data[['day', 'month','year']], dayfirst=True).dt.date
    return data

# Load the data ####################
data = load_data()


# Col names and selection of the good variable
col = data.columns.values.tolist()
col = col[3:9]
variable_choice = st.sidebar.selectbox('Selection of the variable', col)



# Perform the agregation 
@st.cache(max_entries = 1)
def do_the_aggregation(data, start,end,variable):
    ### Filtering #########################################
    temp = data.loc[(data['DATE']>= start) & (data['DATE']<= end)]

    temp=temp[['lat','lon', variable]]

    aggreg = temp.groupby(['lat', 'lon']).aggregate('mean').reset_index()
    
    return(aggreg)



#### DATE Selection ####################""
start_time = st.sidebar.select_slider('Start date',options=data['DATE'])


endlist = data[data['DATE']>start_time].DATE

end_time = st.sidebar.select_slider('End date',options=endlist)
########################################################

aggreg = do_the_aggregation(data, start= start_time, end = end_time, variable = variable_choice)



# country choice 

# selected_country = st.sidebar.selectbox("Select a country", options=['FR','TR'])


px.set_mapbox_access_token(open(".mapbox_token").read())

fig = px.scatter_mapbox(aggreg, lat=aggreg.lat, lon=aggreg.lon,     color=round(aggreg[variable_choice],2), size=round(abs(aggreg[variable_choice]),2),
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10,
                        hover_name  = variable_choice)


fig.update_layout(title="Map of " + variable_choice)

fig.update_layout(mapbox_style="open-street-map",
                mapbox_center_lon=mean(data['lon']), mapbox_center_lat=mean(data['lat']), mapbox_zoom=5)

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=800)


st.header('Map of '+ variable_choice )

st.plotly_chart(fig, use_container_width=True)
