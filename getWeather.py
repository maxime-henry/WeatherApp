import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime

# import boto3




# s3 = boto3.resource(
#     service_name='s3',
#     region_name='eu-west-3',
#     aws_access_key_id='AKIAZ7LWH6KWW2KAZX6Z',
#     aws_secret_access_key='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'
# )

# Authentication #
user = 'mio_eame_sprxxxs_system '
password = 'mio_eame_sprxxxs_systemPASS98766!'
host = 'deawirbitt001.clwtglrkcnfi.eu-central-1.redshift.amazonaws.com'
port = 5439
dbname = 'mio'

start = datetime.now()
def get_weather(country):
    # Connection do database
    with psycopg2.connect("dbname={} host={} port={} user={} password={}".format(dbname, host, port, user, password)) as conn:
        with conn.cursor() as cur:
            print("fetching")
            # QUERY #
            cur.execute("""SELECT
            right(date,2) as day,
            substring(date,5,2) as month,
            lat,
            lon,
            avg(temperature_c_2_m_above_gnd_max) AS temperature_c_max,
            avg(temperature_c_2_m_above_gnd_min) AS temperature_c_min,
            avg(temperature_c_2_m_above_gnd_avg),
            avg(precipitation_total_grid_mm_surface_sum),
            avg(wind_speed_km_per_h_2_m_above_gnd_avg),
            
            avg(relative_humidity_pct_2_m_above_gnd_avg),
            avg(shortwave_radiation_w_per_m2_surface_sum)

                FROM spectrum_schema.mio171_weather_10x10_pivoted_archive AS mio171
                join (
                SELECT distinct dim.place_id
                FROM mio161_t_place_main AS main, mio161_t_place_dim dim
                where main.country_code =%s
                and main.place_guid = dim.place_guid
                and main.place_type = 'gris_10x10_gridcell'
                ) AS mio161
                ON mio171.place_id = mio161.place_id
                WHERE
                date BETWEEN '20170201' AND '20170930'
                OR date BETWEEN '20180201' AND '20180930'
                OR date BETWEEN '20190201' AND '20190930'
                OR date BETWEEN '20200201' AND '20200930'
                OR date BETWEEN '20210201' AND '20210930'

                GROUP BY 1,2,3,4
                ;
                """, (country,))
    # Fetch data #
            data = np.array(cur.fetchall())
            df = pd.DataFrame(data)

            df.columns= ['day',
                            'month',
                            'lat',
                            'lon',
                            'temperature_c_2_m_above_gnd_max',
                            'temperature_c_2_m_above_gnd_min',
                            'temperature_c_2_m_above_gnd_avg',
                            'precipitation_total_grid_mm_surface_sum',
                            'wind_speed_km_per_h_2_m_above_gnd_avg',
                            'relative_humidity_pct_2_m_above_gnd_avg',
                            'shortwave_radiation_w_per_m2_surface_sum'
                            ]
            df = df.sort_values(['day', 'month'], ascending=[True, True])
        
        print("done")

        return(df)

# data = get_weather('UA')

# print("data is here")
# print("saving csv ")

# end = datetime.now()
# data.to_csv("UA.csv")

# print("Let's send it to S3")
# s3.Bucket('weatherdataspr').upload_file(Filename='UA.csv', Key='UA.csv')
# print(data)

# print(end - start)




# 'shortwave_radiation_w_per_m2_surface_sum',
# avg(shortwave_radiation_w_per_m2_surface_sum),