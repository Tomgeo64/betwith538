
# from bs4 import BeautifulSoup
#
#
# soup = BeautifulSoup("<p>Some<b>bad<i>HTML")
# print(soup.prettify())
import pandas as pd
from tools import *


def make_sheet():
    df = pd.read_csv('F1.csv')
    dfcut = df[['HomeTeam', 'AwayTeam', 'MaxH', 'MaxD', 'MaxA', 'Date']]
    vessel = pd.DataFrame(columns=['teams', 'site', 'ev', 'outcome', 'win538', 'bookie%', 'date'])
    for index, n in dfcut.iterrows():
        home = (n['HomeTeam'])
        away = (n['AwayTeam'])
        teams = '(' + home +', ' + away + ')'
        line = pd.DataFrame(columns=['teams', 'site', 'ev', 'outcome', 'win538', 'bookie%', 'date'])
        line['site'] = ['football-data']

        line1 = line.copy()
        odds1 = get_538_odds(home, away, 1)
        line1['teams'] = [teams]
        line1['win538'] = [odds1]
        line1['outcome'] = [1]
        line1['bookie%'] = n['MaxH']
        line1['date'] = n['Date']
        line1['ev'] = get_ev(odds1, n['MaxH'])

        line2 = line.copy()
        odds2 = get_538_odds(home, away, 2)
        line2['teams'] = [teams]
        line2['win538'] = [odds2]
        line2['outcome'] = [2]
        line2['bookie%'] = n['MaxA']
        line2['date'] = n['Date']
        line2['ev'] = get_ev(odds2, n['MaxA'])

        line0 = line.copy()
        odds0 = get_538_odds(home, away, 0)
        line0['teams'] = [teams]
        line0['win538'] = [odds0]
        line0['outcome'] = [0]
        line0['bookie%'] = n['MaxD']
        line0['date'] = n['Date']
        line0['ev'] = get_ev(odds0, n['MaxD'])

        vessel = vessel.append(line1)
        vessel = vessel.append(line2)
        vessel = vessel.append(line0)

    simple_xl(vessel, 'F1.xlsx')


make_sheet()