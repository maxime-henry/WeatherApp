import streamlit as st  # Template
import pandas as pd
import plotly.express as px
from statistics import mean
import datetime


st.set_page_config(layout="wide",initial_sidebar_state="expanded", page_title="Weather app", page_icon="☀") # Wide page 

# Two columns for wtitle and image 
col1, col2 = st.columns(2)

with col1:
    st.title('Weather app')
    st.caption("Data is compiled over 6 years (2016 - 2021)  \n Data is then averaged according to the date range selected on the sidebar ")
    # st.caption(" And averaged according to the date range selected on the sidebar")
with col2:
    st.image("data/Logo_SPR.jpg", width=150)


# country choice 
selected_country = st.sidebar.selectbox("Select a country", options=['ES_PT','ES','ZA','TR','PT'], help = "Select the coutry you need the data from")

@st.cache(max_entries = 1)
# Only working for turkey now
def load_data(country):
    if country=="ZA":
        data1 = pd.read_csv("data/ZA1.zip")
        data2 = pd.read_csv("data/ZA2.zip")
        data3 = pd.read_csv("data/ZA3.zip")
        data4 = pd.read_csv("data/ZA4.zip")
        data_temp= pd.concat([data1, data2], axis = 1)
        data_temp2= pd.concat([data3, data4], axis = 1)
        data= pd.concat([data_temp, data_temp2], axis = 1)
        converter = lambda x : 2021 if x < 9 else 2020
        data['year'] = data['month'].apply(converter)

        # data.to_csv("Bon_bug.csv")
    else:
        data = pd.read_csv(f"data/{country}.zip")
        data['year']= 2020
        
    # data = pd.read_csv("PT.csv")
    # data = get_weather(country)
    
    data['DATE'] = pd.to_datetime(data[['day', 'month','year']], dayfirst=True, errors='coerce').dt.date
    return data

# Load the data ####################
with st.spinner("We are loading millions of data points"):
    data = load_data(country = selected_country)



# Col names and selection of the good variable
col = ['temperature_c_2_m_above_gnd_max',
                            'temperature_c_2_m_above_gnd_min',
                            'temperature_c_2_m_above_gnd_avg',
                            'precipitation_total_grid_mm_surface_sum',
                            'wind_speed_km_per_h_2_m_above_gnd_avg',
                            'relative_humidity_pct_2_m_above_gnd_avg'
                            # 'GDD'
                            ]


# Select the weather variables
variable_choice = st.sidebar.selectbox('Selection of the variable', col, help = "Select the weather variable that you want to be displayed on the map")
# Select the aggregation 
aggregation = st.sidebar.radio("Select the aggregation", ("Average", 'Sum'))

#### DATE Selection ####################""

if selected_country != 'ZA':

    start_time =  st.sidebar.date_input(label= "Start date", value=datetime.date(2020,2,1), min_value=datetime.date(2020,2,1), max_value=datetime.date(2020,9,30))

    end_time =  st.sidebar.date_input(label= "End date", value=datetime.date(2020,9,30), min_value=start_time, max_value=datetime.date(2020,9,30))
else:
    start_time =  st.sidebar.date_input(label= "Start date", value=datetime.date(2020,10,1), min_value=datetime.date(2020,10,1), max_value=datetime.date(2021,7,30))

    end_time =  st.sidebar.date_input(label= "End date", value=datetime.date(2021,7,31), min_value=start_time, max_value=datetime.date(2021,7,31))

########################################################


# Perform the agregation 
@st.cache(max_entries = 1)
def do_the_aggregation(data, start,end,variable, aggregation):
    ### Filtering #########################################
    print(variable)
    # GDD data not in the zip file so imported here 
    # if variable == 'GDD':
    #     datatemp = pd.read_csv('GDD.csv')
    #     datatemp['year'] = 2020
    #     datatemp['DATE'] = pd.to_datetime(datatemp[['day', 'month','year']], dayfirst=True).dt.date
    #     temp = datatemp.loc[(datatemp['DATE']>= start) & (datatemp['DATE']<= end)]
    # else:
    temp = data.loc[(data['DATE']>= start) & (data['DATE']<= end)] 

    temp=temp[['lat','lon', variable]]
    temp[variable] = temp[variable].astype(float).round(2)
    
    if aggregation == 'Average' :
        aggreg = temp.groupby(['lat', 'lon']).aggregate('mean').reset_index()
    if aggregation == 'Sum':
        aggreg = temp.groupby(['lat', 'lon']).aggregate('sum').reset_index()
    return(aggreg)


# Do the aggregation 
with st.spinner("We are aggregating the data to display the map according to the data range you choosed.."):
    aggreg = do_the_aggregation(data, start= start_time, end = end_time, variable = variable_choice, aggregation=aggregation)




# machin = data.drop_duplicates()
# st.dataframe(machin)


# Create the map with mapbox ans poltly express
px.set_mapbox_access_token(open(".mapbox_token").read())

fig = px.scatter_mapbox(aggreg, lat=aggreg.lat, lon=aggreg.lon, color=round(aggreg[variable_choice],2), size=round(abs(aggreg[variable_choice]),2),
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10,
                        hover_name  = variable_choice, labels = aggreg[variable_choice])


fig.update_layout(title="Map of " + variable_choice)

fig.update_layout(mapbox_style="open-street-map",
                mapbox_center_lon=mean(data['lon']), mapbox_center_lat=mean(data['lat']), mapbox_zoom=5)

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=800)



# Display header
st.header('Map of '+ variable_choice)

st.text('Between ' + str(start_time.day) + ' '+ str(start_time.strftime('%B')) + ' and ' + str(end_time.day) + ' '+str(end_time.strftime('%B')))


# Dispay map 
st.plotly_chart(fig, use_container_width=True)


st.caption("Version 1.0.1 2022 - SPR EAME - maxime.henry@syngenta.com")
