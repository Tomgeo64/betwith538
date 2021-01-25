import pandas as pd
import requests
import json
from sportradar import Soccer
import time
from fix538 import fix_538
import dateutil.parser
from main import update_538
from tools import *


def evaluate(filename, newfilename, dateSwap):
    update_538()
    print("Here!")
    predToEval = xlsx_to_df(filename)
    winList = []
    winningsList = []
    for index, n in predToEval.iterrows():
        # print(n['ev'])
        if type(n['ev']) is not float:
            print(n['ev'])
            print("Here ev above")
            winList.append(-1)
            winningsList.append(0)
            continue
        teams = n['teams'].split(",")
        # team1 = teams[0][:-1]
        # team1 = team1[2:]
        # team2 = teams[1][:-2]
        # team2 = team2[2:]
        team1 = teams[0][2:-1]
        team2 = teams[1][2:-2] # Working for ne games

        date = n['date']
        if dateSwap:
            parts = date.split('/')
            print(parts)
            day = parts[0]
            month = parts[1]
            year = parts[2]
            date = year + '-' + month + '-' + day
        res = get_538_results(team1, team2, date)

        winnings = 0
        if res == n['outcome']:
            winnings = 100 * n['bookie%'] - 100
        if res != n['outcome']:
            winnings = -100
        winList.append(res)
        winningsList.append(winnings)
    predToEval['win'] = winList
    predToEval['winnings'] = winningsList
    simple_xl(predToEval, newfilename)


def get_538_results(team1, team2, date, ):
    newteam1 = fix_538(team1)
    newteam2 = fix_538(team2)
    matches538 = pd.read_csv('spi_matches_latest.csv') # changing for historical results to spi_matches
    dfcut = matches538[['team1', 'team2', 'score1', 'score2', 'date']]
    dateTrim = date[:-10]
    rows = dfcut.loc[(dfcut['team1'] == newteam1) & (dfcut['team2'] == newteam2)]
    if rows.empty:
        print("No matches found")
        print(newteam1)
        print(newteam2)
        return -1
    if len(rows) > 1:
        day = dateTrim[-2:]
        allButDay = dateTrim[:-2]
        tomorrow = int(day) + 1
        tomorrowStr = allButDay + str(tomorrow)
        yesterday = int(day) - 1
        yesterdayStr = allButDay + str(yesterday)
        rows2 = rows.loc[(rows['date'] == dateTrim)] #  or (rows['date'] == tomorrowStr) or (rows['date'] == yesterdayStr)
        rows3 = rows.loc[(rows['date'] == tomorrowStr)]
        rows4 = rows.loc[(rows['date'] == yesterdayStr)]
        rows2 = rows2.append(rows3)
        rows2 = rows2.append(rows4)
        for index, n in rows2.iterrows():
            if n['date'] == dateTrim:
                print("Timezone fixed")
        if len(rows2) != 1:
            print('%%%%%%%%%%%%%')
            print(newteam1, newteam2, yesterdayStr)
            print("multiple, or no games found wtf")
            print(rows2)
            print("*************************************")
            return -1
    else:
        rows2 = rows.copy()
    if rows2.iloc[0]['score1'] == rows2.iloc[0]['score2']:
        return 0
    if rows2.iloc[0]['score1'] > rows2.iloc[0]['score2']:
        return 1
    if rows2.iloc[0]['score1'] < rows2.iloc[0]['score2']:
        return 2
    return -1

evaluate('bestInTen1Sheet.xlsx', '101sheetEval.xlsx', False)
