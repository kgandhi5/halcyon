import pandas as pd
import numpy as np
import scipy as sp
import json, requests
from pandas.io.json import json_normalize
import feedparser
from geopy.geocoders import Nominatim
from math import cos, asin, sqrt


def update_map(form):
    addresss = form.address.data
    radius = form.radius.data
    types_req = form.incident_type.data

    def query_site(url, params):
        # Queries the Water Quality Sample Data of data.austintexas.gov.
        # A json document is returned by the query.
        r = requests.get(url, params)
        print("Requesting", r.url)

        if r.status_code == requests.codes.ok:
          return r.json()
        else:
          r.raise_for_status()

    base_url = 'https://data.austintexas.gov/resource/5h38-fd8d.json?$where=sr_status_date%20between%20%272017-12-09T00:00:00.000%27%20and%20%272017-12-10T17:00:00.000%27'
    params = {}
    data = query_site(base_url, params)
    df = json_normalize(data)
    concerns =['DRFLOOD1','DRFLOODG','DRFLOODR','ACBITE2',
    	   'ACCOYTE','ACLOANIM','ACLONAG','COAACBAT','COAACDA','COAACDD','COYOCOMP','WILDEXPO']
    animal = ['ACBITE2','ACCOYTE','ACLOANIM','ACLONAG','COAACBAT','COAACDA','COAACDD','COYOCOMP','WILDEXPO']
    flood = ['DRFLOOD1','DRFLOODG','DRFLOODR']
    df_concerns = df.loc[df['sr_type_code'].isin(concerns)]
    df_concerns= df_concerns[df_concerns['sr_status_desc']!='Closed']
    df_concerns = df_concerns.reset_index(drop=True)
    df_concerns['Type']=np.where(df_concerns['sr_type_code'].isin(animal),'animal','flood')
    df_concerns= df_concerns[['sr_location','sr_department_desc','sr_type_desc','sr_location_lat','sr_location_long','Type']]

    df_concerns = df_concerns.rename(columns={'sr_location': 'Address', 'sr_department_desc':'Department',
    					  'sr_type_desc':'Description','sr_location_lat': 'Latitude',
    					  'sr_location_long':'Longitude'
    					  })


    url = "http://www.ci.austin.tx.us/fact/fact_rss.cfm"
    feeds = feedparser.parse(url )
    feeds['entries']
    incident = {}
    department=[]
    Address=[]
    Latitude=[]
    Longitude=[]
    Description=[]
    for i in range(len(feeds['entries'])):
        fir_list = feeds['entries'][i]['summary'].split('|')
        department.append(fir_list[0])
        Address.append(fir_list[1])
        Latitude.append(fir_list[2])
        Longitude.append(fir_list[3])
        Description.append(fir_list[4])
    incident['Department']=department
    incident['Address']=Address
    incident['Latitude']=Latitude
    incident['Longitude']=Longitude
    incident['Description']=Description
    incident['Type']= 'fire'
    df_incident = pd.DataFrame(incident)


    problems = [df_concerns,df_incident]
    df_final = pd.concat(problems)
    df_final['Latitude'] = pd.to_numeric(df_final['Latitude'], errors='coerce')
    df_final['Longitude'] = pd.to_numeric(df_final['Longitude'], errors='coerce')
    df_final = df_final.reset_index(drop=True)

    #addresss = '109 W Gamble St, Austin, Tx, 98989'
    geolocator = Nominatim()
    location = geolocator.geocode(addresss)
    lat = location.latitude
    lon = location.longitude

    def distance_geocode(lat1, lon1, lat2, lon2):
        p = 0.017453292519943295     #Pi/180
        a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 7918 * asin(sqrt(a)) #2*R*asin...

    df_final['Distance']=0.0
    for i in range(len(df_final.index)):
        df_final['Distance'][i]=distance_geocode(df_final['Latitude'][i],df_final['Longitude'][i],lat,lon)
    #radius = 3.0
    df_final = df_final[df_final['Distance']<=radius]
    df_final = df_final.reset_index(drop=True)

    #types_req = ['animal','fire','flood']
    df_final = df_final.loc[df_final['Type'].isin(types_req)]
    df_final = df_final.reset_index(drop=True)

    def df_to_geojson(df, properties, lat, lon):
        geojson = {'type':'FeatureCollection', 'features':[]}
        for _, row in df.iterrows():
            feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                           'coordinates':[]}}
            feature['geometry']['coordinates'] = [row[lon],row[lat]]
            for prop in properties:
                feature['properties'][prop] = row[prop]
            geojson['features'].append(feature)
        return geojson
    
    cols = ['Address', 'Department','Description','Type']
    geojson = df_to_geojson(df_final, cols,'Latitude','Longitude')

    return geojson

