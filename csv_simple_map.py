import csv
import urllib.request
from datetime import datetime
from pathlib import Path
import csv
import os
import pandas as pd
import plotly.express as px

#https://www.casadei.com/en/shoes/high-boots/blade-black-1T000D125HHNAGU9000.html

today = datetime.today().strftime('%Y-%m-%d')
storage = Path(os.getcwd())
url = 'https://coronavirus.ohio.gov/static/COVIDSummaryData.csv'
new_file = str(today + '_data.csv')
path = Path(storage / new_file)
full_data = Path(storage / 'fulldata.csv')


def build_today_data():
	request = urllib.request.Request(url)
	response = urllib.request.urlopen(request)
	test = response.read().decode('utf-8')
	del response

	if not os.path.exists(Path(storage / new_file)):
		with open(Path(storage / new_file), mode='w+') as csv_file:
			csv_file.writelines(test)


def get_value(val_name):
	df = pd.read_csv(path)
	vals = df[val_name]
	num = len(vals)
	return str(vals[num-1])


def get_values():

	cases = get_value('Case Count').replace(',','').strip()
	hospitalizations = get_value('Hospitalized Count').replace(',','').strip()
	deaths = get_value('Death Count').replace(',','').strip()

	values = []
	values.append(today.strip())
	values.append(cases)
	values.append(hospitalizations)
	values.append(deaths)
	values = ','.join(values)
	return values


def get_headers():

	headers = []
	headers.append("Date".strip())
	headers.append("Cases".strip())
	headers.append("Hospitalizations".strip())
	headers.append("Deaths".strip())
	return headers


def already_run():

	if not os.path.exists(full_data):
		return False

	data = pd.read_csv(full_data)
	dates = data.Date
	return today in str(dates)


def update_data_file(headers, values):

	if not os.path.exists(full_data):
		with open(full_data, mode='w+') as csv_file:
			csv_file.writelines(headers)
			csv_file.writelines('\n')
			csv_file.writelines(values)
	else:
		with open(full_data, mode='a') as csv_file:
			csv_file.writelines('\n')
			csv_file.writelines(values)


def graph_stuff(headers_in):

	df_wide = pd.read_csv(full_data)
	
	value_variables = headers_in[1:]
	id_variable = ['Date']

	df_long = pd.melt(df_wide, id_vars=id_variable, value_vars=value_variables, value_name='People', var_name='Legend')
	fig = px.line(df_long, x='Date', y='People', title='Coronavirus Cases in Ohio', color='Legend')

	fig.show()


build_today_data()
headers = get_headers()
values = get_values()
new_headers = ','.join(headers)
if not already_run():
	update_data_file(new_headers, values)

graph_stuff(headers)

# for getting data by county fromt the data file
#print(df.groupby(['County']).count())