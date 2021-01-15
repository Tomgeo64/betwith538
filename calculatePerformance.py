import pandas as pd
import requests
import json
from sportradar import Soccer
import time

api_key = 'jtsepvs94e4k62f78vrpxwmm'


def xlsx_to_df(filename):
    return pd.read_excel(filename)

# Sporstradar API currently broken I think.
def add_score(df):
    # Create an instance of the Sportradar Soccer API class
    sr = Soccer.Soccer(api_key)
    # Get a list of all tournaments
    # tournaments = sr.get_tournaments().json()
    matches = sr.get_daily_results(year=2019, month=1, day=9)
    print(matches.text)
    matches_json = json.loads(matches.text)
    print(len(matches.text))
    # Get info on the 2018 World Cup (Teams, Rounds, etc.)
    # worldcup = sr.get_tournament_info(tournaments['tournaments'][4]['id']).json()
    # Get more information on each team in the World Cup
    teams = []
    team_counter = 0
    matchesdf = pd.DataFrame(data=matches)
    for col in matchesdf.columns:
        print("Iterated")
        print(col)
    # for group in worldcup['groups']:
    #     for team in group['teams']:
    #         team_counter += 1
    #         team_id = team['id']
    #         team_name = team['name']
    #         print("({}): {}, {}".format(team_counter, team_name, team_id))
    #         try:
    #             teams.append(sr.get_team_profile(team_id).json())
    #         except Exception as e:
    #             print("Error: {}".format(e))
    #         time.sleep(5)  # wait 5 seconds before next API call

    # Save the team data to a .json file
    print("Saving the data...", end="", flush=True)
    with open("world_cup_team_data.json", "w") as outfile:
        json.dump(teams, outfile)
    print(" Done.")




add_score(xlsx_to_df('bestWeekFixed.xlsx'))
