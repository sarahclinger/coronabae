import csv
from datetime import datetime
import requests
import os
from bs4 import BeautifulSoup 
import pandas as pd
import plotly.express as px
from pathlib import Path
import re 
import codecs

#Constants
URL = 'https://coronavirus.ohio.gov/wps/portal/gov/covid-19/' 
storage = Path(os.getcwd())
today = datetime.today().strftime('%Y-%m-%d')

def line_analysis():
    if os.path.exists(Path(storage / 'ndata.csv')):
        df = pd.read_csv(Path(storage / 'ndata.csv'))
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
        if 'Info' not in d.text.strip() and "Dashboard" not in d.text.strip():
            header += d.text.strip() + ","
            lines2.append(n.text.strip() + ',')

    # checks if the file exists, and if not then makes it and sets the headers
    if not os.path.exists(Path(storage / 'ndata.csv')):
        with codecs.open(Path(storage / "ndata.csv"), mode='a+', encoding="utf-8") as csv_file:
            csv_file.writelines(header)
            csv_file.writelines('\n')

    # rewrite the headers as they may have changed
    with codecs.copen(Path(storage / "ndata.csv"), mode='r+', encoding="utf-8") as csv_file:
        csv_file.seek(0)
        csv_file.writelines(header)
        
    # add the new data
    with codecs.open(Path(storage / "ndata.csv"), mode='a', encoding="utf-8") as csv_file:
        #Crude Hack if the file didn't contain a new line before writing.
        csv_file.writelines('\n')
        for line in lines2:
            csv_file.writelines(line)
        csv_file.writelines('\n')

def get_county_info():
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find_all(class_='odh-ads__item-title')
    
    county_num = results[1].text.strip()
    text = soup.find_all(class_='odh-ads__super-script-item')[0].text.strip()
    counties = text[text.index(':') + 1:]
    counties_list = counties.split(',')

    count_info = {}
    for c in counties_list:
        county_info[c[:c.strip().index(' ')+1]]=re.findall(r'\d+', c)[0]
    
    if len(count_info) == int(county_num):
        return count_info
    else:
        return "Error: number of counties and county count don't match"


def header_titles():
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    headers = soup.find_all(class_='odh-ads__item-summary')

    titles = []
    for h in headers:
        if 'Info' not in h.text.strip() and "Dashboard" not in h.text.strip():
            titles.append(h.text.strip())
    return titles


path = Path(storage / 'ndata.csv')



def graph_stuff(titles):
    df_wide = pd.read_csv(path)
    value_variables = titles 
    id_variable = ['Date']

    #making the data "tidy"
    df_long=pd.melt(df_wide, id_vars=id_variable, value_vars=value_variables, value_name='People', var_name='Legend')

    #graph the data
    fig = px.line(df_long, x='Date', y='People', title='Coronavirus Cases in Ohio', color='Legend')

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        args=[{"visible": [False, True, True, True]}],
                        label=str([value_variables[0]]),
                        method="relayout"
                    ),
                    dict(
                        args=[{"visible": [True, False, True, True]}],
                        label=str([value_variables[1]]),
                        method="relayout"
                    ),
                    dict(
                        args=[{"visible": [True, True, False, True]}],
                        label=str([value_variables[2]]),
                        method="relayout"
                    ),
                    dict(
                        args=[{"visible": [True, True, True, False]}],
                        label=str([value_variables[3]]),
                        method="relayout"
                    )
                ]),
            pad={'r':10, 't':10},
            showactive = True,
            x=0.11,
            xanchor="left",
            y=1.1,
            yanchor="top"
            ),
        ]
    )

    #px.write_html(fig, file='hello_world.html', auto_open=True)
    #px.offline.plot(figure, "file.html")
    with open(Path('plotly_graph.html'), 'w') as f:
        f.write(fig.to_html(include_plotlyjs='cdn'))



    fig.show()

#Runtime
if line_analysis():
    page_get()


graph_stuff(header_titles())


