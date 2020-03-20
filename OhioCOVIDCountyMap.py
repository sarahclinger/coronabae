import os 
from bs4 import BeautifulSoup 
import requests 
import re
from datetime import datetime
import csv
import pandas as pd
import json 
import plotly.express as px 


today = today = datetime.today().strftime('%#m-%#d-%Y')
URL = 'https://coronavirus.ohio.gov/wps/portal/gov/covid-19/'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')


# change all of these paths as required -> they are all files that will be created through the script
info_path = 'C:/Users/andre/Desktop/fipsinfo-' + today + '.csv'
ohio_county_path = 'C:/Users/andre/Desktop/ohiocountyinfo.json'

# this is the included csv file that needs to be read for Ohio specific county info -> change this path to wherever you put it in the file system
fips_path = 'C:/Users/andre/Desktop/ohiofips.csv'

# this is the included json file that needs to be read for county info -> change this path to wherever you put it in the file system
country_county_path = 'C:/Users/andre/Desktop/countrycountyinfo.json'


# get the county names and number of cases from the site
def get_county_nums():

    results = soup.find_all(class_='odh-ads__item-title')
    county_num = results[1].text.strip()

    text = soup.find_all(class_='odh-ads__super-script-item')[0].text.strip()
    counties = text[text.index(':') + 1:]
    counties_list = counties.split(',')
    county_info = {}
    for c in counties_list:
        c = c.strip()
        county_info[c[:c.index(' ')]]=re.findall(r'\d+', c)[0]

    if len(county_info) == int(county_num):
        return county_info
    else:
        return 'number of counties reported and number of values did not match'
        

# create today's data file with fips, cases, and county name
def build_today_data(countyinfo):
    ohio_fips = pd.read_csv(fips_path)
    header = "fips,cases,name\n"
    lines = []
    id = 0
    for n,f in zip(ohio_fips.name, ohio_fips.fips):
        val = 0
        if n in countyinfo.keys():
            val = countyinfo[n]

        lines.append(str(id) + "," + str(f) + "," + str(val) + "," + n + '\n')
        id+=1

    if not os.path.exists(info_path):
        with open(info_path, 'w+') as csv_file:
            csv_file.writelines(header)
            csv_file.writelines(lines)


# build Ohio only GeoJSON by getting the Ohio only GeoJSON data from the country wide data
def build_ohio_geojson():

    with open(country_county_path,'r') as response:
        counties = json.load(response)

    data = []
    data.append("""{"type": "FeatureCollection", "features": [""")
    count = 0
    for l in counties["features"]:
        if int(l["properties"]["STATE"]) == 39:
            count += 1
            to_add = str(l)
            if count < 88:
                to_add += ","
            to_add = to_add.replace("'",'"')
            data.append(str(to_add))

    data.append("]}")

    with open(ohio_county_path,'w+') as f:
        for line in data:
            f.writelines(str(line))


# build and display the Ohio county map with COVID-19 cases
def build_and_display_map():

    with open(ohio_county_path,'r') as response:
        counties = json.load(response)

    data = []
    for l in counties["features"]:
        if int(l["properties"]["STATE"]) == 39:        
            data.append(l)

    df = pd.read_csv(info_path, dtype={'fips': str})

    fig = px.choropleth(df, geojson=counties, locations='name', color='cases', color_continuous_scale="Reds", range_color=(0,10), scope="usa", labels={'cases':'number of COVID-19 cases'}, featureidkey="properties.NAME")
    fig.update_layout(margin={"r":0,"t":1,"l":0,"b":0})
    fig.show()


county_numbers = get_county_nums()
build_today_data(county_numbers)
build_ohio_geojson()
build_and_display_map()