import requests
import json
import pandas as pd
from pandas import DataFrame
from urllib.request import urlopen
import urllib
import urllib.request
from fix538 import fix_538
from datetime import datetime
import dateutil.parser
import pytz
import numpy as np
from datetime import datetime, timedelta


api_key = 'cc944894e170db9a6e45dde9536cf4c0'

def make_odds_list(sport_key, region):

    odds_response = requests.get('https://api.the-odds-api.com/v3/odds', params={
        'api_key': api_key,
        'sport': sport_key,
        'region': region,  # uk | us | eu | au
        'mkt': 'h2h',  # h2h | spreads | totals
        'oddsFormat': 'decimal',
        'dateFormat': 'iso'
    })

    odds_json = json.loads(odds_response.text)
    if not odds_json['success']:
        print(
            'There was a problem with the odds request:',
            odds_json['msg']
        )

    else:
        print()
        print(
            'Successfully got {} events'.format(len(odds_json['data'])),
            'From:' + sport_key
        )
        odds_list = []
        for match in odds_json['data']:
            team1 = match['home_team']
            sitesList = match['sites']  # List of betting sites
            date = match['commence_time']
            for x in sitesList:
                # Move home team into first slot to match 538. Odds must be moved as well.
                if match['home_team'] == match['teams'][1]:
                    team2 = match['teams'][0]
                    odds = x['odds']
                    temp = odds['h2h'][0]
                    odds['h2h'][0] = odds['h2h'][1]
                    odds['h2h'][1] = temp
                else:
                    team2 = match['teams'][1]
                    odds = x['odds']
                teams = team1, team2
                name = x['site_key']
                # Grab the things I care about.
                odds_list.append([teams, name, odds, date])

        # Check your usage
        print()
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])

        return odds_list


def get_538_odds(team1, team2, winner):
    # Get odds given 2 teams, winner means outcome
    df = pd.read_csv('spi_matches_latest.csv')
    dfcut = df[['team1', 'team2', 'prob1', 'prob2', 'probtie']]
    # Run dictionary on team names to make them readable.
    newteam1 = fix_538(team1)
    newteam2 = fix_538(team2)
    # Grab only rows with correct teams.
    rows = dfcut.loc[(dfcut['team1'] == newteam1) & (dfcut['team2'] == newteam2)]
    if rows.empty:
        # print("STILL EMPTY")  # this means somebodies name is broken and needs to be added to dictionary
        return 0
    if winner == 1:
        return rows.iloc[0]['prob1']
    if winner == 2:
        return rows.iloc[0]['prob2']
    if winner == 0:
        return rows.iloc[0]['probtie']


def do_sport(sport_key, region):
    odds_list = make_odds_list(sport_key, region)
    ev_list = []
    for x in odds_list:
        team1, team2 = x[0]
        # Grab odds from 528 csv
        win5381 = get_538_odds(team1, team2, 1)
        win5382 = get_538_odds(team1, team2, 2)
        if len(x[2]['h2h']) == 3:  # If ties are possible
            win5380 = get_538_odds(team1, team2, 0)
            ev0 = get_ev(win5380, x[2]['h2h'][2])
            ev_list.append([x[0], x[1], ev0, 0, win5380, x[2]['h2h'][2], x[3]])

        # Use the 2 variables to calculate EV
        ev1 = get_ev(win5381, x[2]['h2h'][0])
        ev2 = get_ev(win5382, x[2]['h2h'][1])
        # Make list of format (teams, site, EV, outcome, 538chance, bookie%, date)
        # outcome: 1 = team 1 wins. 2 = team 2 wins. 0 = draw.
        ev_list.append([x[0], x[1], ev1, 1, win5381, x[2]['h2h'][0], x[3]])
        ev_list.append([x[0], x[1], ev2, 2, win5382, x[2]['h2h'][1], x[3]])
    highest = 0
    for x in ev_list:
        if x[2] > highest:
            highest = x[2]
            best = x
        if x[2] == -100:  # broken predictions
            print(x)
            count = 1
    evdf = DataFrame(ev_list, columns=['teams', 'site', 'ev', 'outcome', 'win538', 'bookie%', 'date'])
    result = evdf.sort_values(['ev'], ascending=False, ignore_index=True)  # Sort
    return result


def simple_xl(result):
    result.to_excel('simple.xlsx')
    print("printed to xl")


def get_ev(win538, odds):
    if odds is None:
        return 0
    if win538 is None:
        return 0
    # Basically % return on bet, or expected return for $100 bet. Same thing.
    return (win538 * odds * 100) - 100


def many_sports(filename, minEv, region, maxPerEvent, maxLeagues, days, singleSheet):
    update_538()
    soccerList = get_in_season_soccer()
    maxCount = -1
    curRow = 0
    with pd.ExcelWriter(filename) as writer:
        for x in soccerList:
            if maxCount >= maxLeagues:
                return
            maxCount = maxCount + 1
            table = do_sport(x, region)
            minTable = exclude_in_progress(table, days)

            uniqueTeams = []
            for index, n in minTable.iterrows():
                if n['teams'] not in uniqueTeams:
                    uniqueTeams.append(n['teams'])
            cutTable = pd.DataFrame(columns=['teams', 'site', 'ev', 'outcome', 'win538', 'bookie%', 'date', 'devsFromMean', 'bookieMean','fixtureStdDev'])
            for y in uniqueTeams:
                rows = minTable.loc[(minTable['teams'] == y)]
                rows2 = bookie_std_dev(rows)
                # temp = rows2.nlargest(maxPerEvent, 'ev')
                temp = cap_bookies_per_outcome(rows2, maxPerEvent)
                cutTable = cutTable.append(temp)
            evCut = cutTable[cutTable['ev'] >= minEv]
            if evCut.empty:
                print("No matches for" + x + " met minimum EV")
                continue
            if singleSheet:
                evCut.to_excel(writer, sheet_name="sheet", startrow=curRow)
                curRow = curRow + len(evCut) + 1
            else:
                evCut.to_excel(writer, sheet_name=x)


def get_in_season_soccer():
    # Get all in season soccer
    sports_response = requests.get('https://api.the-odds-api.com/v3/sports', params={
        'api_key': api_key
    })
    sports_json = json.loads(sports_response.text)

    if not sports_json['success']:
        print(
            'There was a problem with the sports request:',
            sports_json['msg']
        )

    soccer_list = []
    for sport in sports_json['data']:
        if 'soccer' in sport['key']:
            soccer_list.append(sport['key'])
    print(soccer_list)
    return soccer_list


def update_538():
    urllib.request.urlretrieve("https://projects.fivethirtyeight.com/soccer-api/club/spi_matches_latest.csv", "spi_matches_latest.csv")
    print("Done downloading from 538")


def exclude_in_progress(df, daysAdd):
    my_date = datetime.now()
    cutTable = pd.DataFrame(columns=['teams', 'site', 'ev', 'outcome', 'win538', 'bookie%', 'date'])
    utc = pytz.UTC
    for index, n in df.iterrows():
        matchDate = dateutil.parser.parse(n['date'])
        currAware = utc.localize(my_date)
        maxDate = currAware + timedelta(days=daysAdd)
        if (matchDate > currAware) & (matchDate <= maxDate):
            cutTable = cutTable.append(n)
    return cutTable


def bookie_std_dev(df):
    temp = df.copy()
    out1 = df.loc[(df['outcome'] == 1)]
    out2 = df.loc[(df['outcome'] == 2)]
    out0 = df.loc[(df['outcome'] == 0)]
    stdDev1 = np.std(out1['bookie%'])
    stdDev2 = np.std(out2['bookie%'])
    stdDev0 = np.std(out0['bookie%'])
    mean1 = np.mean(out1['bookie%'])
    mean2 = np.mean(out2['bookie%'])
    mean0 = np.mean(out0['bookie%'])
    meanDict = {
        1: mean1,
        2: mean2,
        0: mean0
    }
    stdDevDict = {
        1: stdDev1,
        2: stdDev2,
        0: stdDev0
    }
    devMeanList = []
    meanList = []
    devList = []
    for index, x in df.iterrows():
        devMean = (x['bookie%'] - meanDict[x['outcome']]) / stdDevDict[x['outcome']]
        devMean = np.abs(devMean)
        devMeanList.append(devMean)
        meanList.append(meanDict[x['outcome']])
        devList.append(stdDevDict[x['outcome']])
    temp['devsFromMean'] = devMeanList
    temp['bookieMean'] = meanList
    temp['fixtureStdDev'] = devList
    return temp


def cap_bookies_per_outcome(rows, cap):
    rows1 = rows.loc[(rows['outcome'] == 1)]
    rows2 = rows.loc[(rows['outcome'] == 2)]
    rows0 = rows.loc[(rows['outcome'] == 0)]
    temp1 = rows1.nlargest(cap, 'ev')
    temp2 = rows2.nlargest(cap, 'ev')
    temp0 = rows0.nlargest(cap, 'ev')
    frames = [temp1, temp2, temp0]
    result = pd.concat(frames)
    return result


many_sports('newest.xlsx', 5, 'uk', 1, 100, 7, True)



