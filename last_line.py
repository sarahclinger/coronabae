import os
import csv
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')

def line_search():
    with open('file.csv') as f:
        for line in f:

            if line.split(',')[0] == today:
                print('Whoa this is todays date ' + line.split(',')[0])
        # #pass
    #last_line = line





