import streamlit as st  # Template
import pandas as pd
import plotly.express as px
from statistics import mean

st.set_page_config(layout="wide")

st.title('Weather app')


@st.cache
def load_data():
    # data = pd.read_csv('summarizedfebruary.csv')
    data = pd.read_csv("summarizedfebruary.zip")
    data['year'] = 2020
    data['DATE'] = pd.to_datetime(data[['day', 'month','year']], dayfirst=True).dt.date
    return data

data = load_data()



# st.subheader('Selection of the variable')
col = data.columns.values.tolist()
col = col[3:9]
variable_choice = st.sidebar.selectbox('Selection of the variable', col)


#### DATE Selection ####################""
start_time = st.sidebar.select_slider('Start date',options=data['DATE'])


endlist = data[data['DATE']>start_time].DATE

end_time = st.sidebar.select_slider('End date',options=endlist)
########################################################

### Filtering #########################################
temp = data.loc[(data['DATE']>= start_time) & (data['DATE']<= end_time)]

temp=temp[['lat','lon', variable_choice]]

aggreg = temp.groupby(['lat', 'lon']).aggregate('mean').reset_index()




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
