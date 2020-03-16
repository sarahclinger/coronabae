import csv
from datetime import datetime
import requests
import os
from bs4 import BeautifulSoup 
import pandas as pd
import plotly.express as px
from pathlib import Path

#Constants
URL = 'https://odh.ohio.gov/wps/portal/gov/odh/know-our-programs/Novel-Coronavirus' 
storage = Path(os.getcwd())
today = datetime.today().strftime('%#m/%#d/%Y')

def line_analysis():
    if os.path.exists(Path(storage / 'file.csv')):
        df = pd.read_csv(Path(storage / 'file.csv'))
        dates = df.Date
        return today not in str(dates)
    return True

def page_get():
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')


    # get the numbers and their descriptions
    results = soup.find_all(class_='odh-ads__item-title')
    descriptions = soup.find_all(class_='odh-ads__item-summary')


    # create the header and the data lines
    lines2today = today + ','
    lines2 = [lines2today]
    header = 'Date,'

    for n, d in zip(results,descriptions):
        header += d.text.strip() + ","
        lines2.append(n.text.strip() + ',')

    # checks if the file exists, and if not then makes it and sets the headers
    if not os.path.exists(Path(storage / 'file.csv')):
        with open(Path(storage / "file.csv"), mode='a+') as csv_file:
            csv_file.writelines(header)
            csv_file.writelines('\n')
        
    # add the new data
    with open(Path(storage / "file.csv"), mode='a') as csv_file:
        #Crude Hack if the file didn't contain a new line before writing.
        csv_file.writelines('\n')
        for line in lines2:
            csv_file.writelines(line)
        csv_file.writelines('\n')

path = Path(storage / 'file.csv')



def graph_stuff():
    df_wide = pd.read_csv(path)
    value_variables = ['Confirmed Cases in Ohio*', 'Persons Under Investigation** in Ohio', 'Negative PUIs*** in Ohio']
    id_variable = ['Date']

    #making the data "tidy"
    df_long=pd.melt(df_wide, id_vars=id_variable, value_vars=value_variables)

    #graph the data
    fig = px.line(df_long, x='Date', y='value', title='Coronavirus Cases in Ohio', color='variable')

    #px.write_html(fig, file='hello_world.html', auto_open=True)
    #px.offline.plot(figure, "file.html")
    with open(Path('plotly_graph.html'), 'w') as f:
        f.write(fig.to_html(include_plotlyjs='cdn'))

    fig.show()

#Runtime
if line_analysis():
    page_get()


graph_stuff()


