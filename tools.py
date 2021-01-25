import pandas as pd
import urllib
import urllib.request
from fix538 import *

def update_538():
    urllib.request.urlretrieve("https://projects.fivethirtyeight.com/soccer-api/club/spi_matches_latest.csv", "spi_matches_latest.csv")
    print("Done downloading from 538")

def simple_xl(result, name):
    result.to_excel(name)
    print("printed to xl")


def xlsx_to_df(filename):
    return pd.read_excel(filename)


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


def get_ev(win538, odds):
    if odds is None:
        return 0
    if win538 is None:
        return 0
    # Basically % return on bet, or expected return for $100 bet. Same thing.
    return (win538 * odds * 100) - 100
