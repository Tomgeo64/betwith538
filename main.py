import requests
import json
import pandas as pd
from pandas import DataFrame
from urllib.request import urlopen
import urllib
import urllib.request

api_key = '4e643cb3d36ffff4a2d6d7c6a4e78771'

def make_odds_list(sport_key):

    odds_response = requests.get('https://api.the-odds-api.com/v3/odds', params={
        'api_key': api_key,
        'sport': sport_key,
        'region': 'us',  # uk | us | eu | au
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
            'From:'+ sport_key
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
        print("STILL EMPTY")  # this means somebodies name is broken and needs to be added to dictionary
        return 0
    if winner == 1:
        return rows.iloc[0]['prob1']
    if winner == 2:
        return rows.iloc[0]['prob2']
    if winner == 0:
        return rows.iloc[0]['probtie']


def do_sport(sport_key):
    odds_list = make_odds_list(sport_key)
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
    evdf = DataFrame(ev_list, columns=['teams', 'site', 'EV', 'outcome', 'win538', 'bookie%', 'date'])
    result = evdf.sort_values(['EV'], ascending=False, ignore_index=True)
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


def many_sports(filename):
    update_538()
    soccerList = get_in_season_soccer()
    with pd.ExcelWriter(filename) as writer:
        for x in soccerList:
            table = do_sport(x)
            table.to_excel(writer, sheet_name=x)


def fix_538(team):
    # There appears to no rhyme or reason for how 528, or the bookies name their teams. So we use this.
    translateTo538 = {
        "Besiktas JK": 'Besiktas',
        'Çaykur Rizespor': 'Caykur Rizespor',
        'Basaksehir': 'Istanbul Basaksehir',
        'Gazişehir Gaziantep': 'Gazisehir Gaziantep',
        'Torku Konyaspor': 'Konyaspor',
        'Dundee United': 'Dundee Utd',
        'Atlético Madrid': 'Atletico Madrid',
        'Elche CF': 'Elche',
        'CA Osasuna': 'Osasuna',
        'Cádiz CF': 'Cadiz',
        'Huesca': 'SD Huesca',
        'Valladolid': 'Real Valladolid',
        'Granada CF': 'Granada',
        'Sevilla': 'Sevilla FC',
        'FK Sochi': 'Sochi',
        'Tambov': 'FC Tambov',
        'FC Rotor Volgograd': 'FK Volgograd',
        'FK Rostov': 'Rostov',
        'FC Akhmat Grozny': 'Terek Grozny',
        'Nacional': 'C.D. Nacional',
        'CS Maritimo': 'Maritimo',
        'Famalicão': 'Famalicao',
        'Boavista Porto': 'Boavista',
        'Pacos de Ferreira': 'Pacos Ferreira',
        'Sporting Lisbon': 'Sporting CP',
        'Groningen': 'FC Groningen',
        'FC Twente Enschede': 'FC Twente',
        'RKC Waalwijk': 'RKC',
        'AZ Alkmaar': 'AZ',
        'Heracles Almelo': 'Heracles',
        'FC Zwolle': 'PEC Zwolle',
        'Sparta Rotterdam': 'Sparta',
        'FC Emmen': 'Emmen',
        'PSV Eindhoven': 'PSV',
        'Tigres': 'Tigres UANL',
        'Pumas': 'Pumas Unam',
        'América': 'Club América',
        'Hellas Verona FC': 'Verona',
        'Atalanta BC': 'Atalanta',
        'FC Internazionale': 'Internazionale',
        'Hamburger SV': 'Hamburg SV',
        '1. FC Heidenheim': '1. FC Heidenheim 1846',
        'Darmstadt 98': 'SV Darmstadt 98',
        'FC Würzburger Kickers': 'Würzburger Kickers',
        'Greuther Fürth': 'SpVgg Greuther Fürth',
        'Augsburg': 'FC Augsburg',
        'Union Berlin': '1. FC Union Berlin',
        'FC Koln': 'FC Cologne',
        'FSV Mainz 05': 'Mainz',
        'Rodez AF': 'Rodez',
        'USL Dunkerque': 'Dunkerque',
        'EA Guingamp': 'Guingamp',
        'FC Chambly': 'Chambly Thelle FC',
        'Châteauroux': 'Chateauroux',
        'SM Caen': 'Caen',
        'Saint Etienne': 'St Etienne',
        'Rennes': 'Stade Rennes',
        'Nîmes Olympique': 'Nimes',
        'Stade de Reims': 'Reims',
        'Dijon': 'Dijon FCO',
        'RC Lens': 'Lens',
        'Paris Saint Germain': 'Paris Saint-Germain',
        'Bolton Wanderers': 'Bolton',
        'Scunthorpe United': 'Scunthorpe',
        'Wigan Athletic': 'Wigan',
        'Birmingham City': 'Birmingham',
        'Blackburn Rovers': 'Blackburn',
        'Bournemouth': 'AFC Bournemouth',
        'Brondby IF': 'Brondby',
        'SonderjyskE': 'Sonderjyske',
        'OB Odense BK': 'Odense BK',
        'Vejle Boldklub': 'Vejle',
        'Bragantino-SP': 'Bragantino',
        'Atletico Goianiense': 'Atlético Goianiense',
        'Atletico Paranaense': 'Atlético Paranaense',
        'Gremio': 'Grêmio',
        'Newcastle Jets FC': 'Newcastle Jets',
        'Western Sydney Wanderers': 'Western Sydney FC',
        'Western United FC': 'Western United',
        'Newcastle United': 'Newcastle',
        'Wolverhampton Wanderers': 'Wolverhampton',
        'Wellington Phoenix FC': 'Wellington Phoenix',
        'Sao Paulo': 'São Paulo',
        'Nancy': 'AS Nancy Lorraine',
        'Pau FC': 'Pau',
        'VfL Osnabrück': 'VfL Osnabruck',
        'Vitesse Arnhem': 'Vitesse',
        'Rio Ave FC': 'Rio Ave',
        'Moreirense FC': 'Moreirense',
        'Arsenal Tula': 'FC Arsenal Tula',

    }
    if team in translateTo538:
        return translateTo538[team]
    else:
        return team


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


many_sports('usSoccerEV.xlsx')



