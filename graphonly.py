import csv
from datetime import datetime
import requests
import os
from bs4 import BeautifulSoup 
import pandas as pd
import plotly.express as px

URL = 'https://odh.ohio.gov/wps/portal/gov/odh/know-our-programs/Novel-Coronavirus' 
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
storage = '/Users/brandon/Dev/coronabae/'

# get the numbers and their descriptions
results = soup.find_all(class_='odh-ads__item-title')
descriptions = soup.find_all(class_='odh-ads__item-summary')

today = datetime.today().strftime('%Y-%m-%d')

# create the header and the data lines
lines2today = today + ','
lines2 = [lines2today]
header = 'Date,'

for n, d in zip(results,descriptions):
    header += d.text.strip() + ","
    lines2.append(n.text.strip() + ',')

header += '\n'



# add the new data


path = storage + 'file.csv'

df_wide = pd.read_csv(path)

value_variables = ['Confirmed Cases in Ohio', 'Persons Under Investigation* in Ohio', 'Negative PUIs** in Ohio']
id_variable = ['Date']

#making the data "tidy"
df_long=pd.melt(df_wide, id_vars=id_variable, value_vars=value_variables)

#graph the data
fig = px.line(df_long, x='Date', y='value', title='Coronavirus Cases in Ohio', color='variable')

#px.write_html(fig, file='hello_world.html', auto_open=True)
#px.offline.plot(figure, "file.html")
with open('plotly_graph.html', 'w') as f:
    f.write(fig.to_html(include_plotlyjs='cdn'))

fig.show()


