import requests
import json
import pandas as pd
from pandas import DataFrame
from openpyxl import Workbook


def make_odds_list(sport_key):
    # An api key is emailed to you when you sign up to a plan
    api_key = '4e643cb3d36ffff4a2d6d7c6a4e78771'

    # First get a list of in-season sports
    sports_response = requests.get('https://api.the-odds-api.com/v3/sports', params={
        'api_key': api_key
    })
    sports_json = json.loads(sports_response.text)

    if not sports_json['success']:
        print(
            'There was a problem with the sports request:',
            sports_json['msg']
        )

    else:
        print()
        print(
            'Successfully got {} sports'.format(len(sports_json['data'])),
            'Here\'s the first sport:'
        )
        print(sports_json['data'][0])


    # To get odds for a specific sport, use the sport key from the last request
    #   or set sport to "upcoming" to see live and upcoming across all sports


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
        # odds_json['data'] contains a list of live and
        #   upcoming events and odds for different bookmakers.
        # Events are ordered by start time (live events are first)
        print()
        print(
            'Successfully got {} events'.format(len(odds_json['data'])),
            'Here\'s the first event:'
        )
        odds_list = []
        for match in odds_json['data']:
            team1 = match['home_team']
            sitesList = match['sites']  # List of betting sites

            bestOdds = 0
            for x in sitesList:
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
                odds_list.append([teams, name, odds])
        # for x in odds_json['data']:
        #     print(x)
        # Check your usage

        print()
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])
        return odds_list


def get_538_odds(team1, team2, winner):
    # Get odds given 2 teams, winner 1 means team 1 wins, 0 means draw, 2 means team 2
    df = pd.read_csv('spi_matches_latest.csv')
    dfcut = df[['team1','team2','prob1', 'prob2', 'probtie']]
    newteam1 = fix_538(team1)
    newteam2 = fix_538(team2)
    rows = dfcut.loc[(dfcut['team1'] == newteam1) & (dfcut['team2'] == newteam2)]

    if rows.empty:
        print("STILL EMPTY")
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
    bestList = []
    for x in odds_list:
        team1, team2 = x[0]

        win5381 = get_538_odds(team1, team2, 1)
        win5382 = get_538_odds(team1, team2, 2)
        if len(x[2]['h2h']) == 3:
            win5380 = get_538_odds(team1, team2, 0)
            ev0 = get_ev(win5380, x[2]['h2h'][2])
            ev_list.append([x[0], x[1], ev0, 0, win5380, x[2]['h2h'][2]])

        ev1 = get_ev(win5381, x[2]['h2h'][0])
        ev2 = get_ev(win5382, x[2]['h2h'][1])

        ev_list.append([x[0], x[1], ev1, 1, win5381, x[2]['h2h'][0]])  # 1 is outcome, 1 = team 1 wins.
        ev_list.append([x[0], x[1], ev2, 2, win5382, x[2]['h2h'][1]])

        # if team1 == 'Sheffield United':
        #     print(team2)
        #     print(ev1)
        #     print(win5381)
        #     print(x[2]['h2h'][0])
        #     print(x[2]['h2h'][1])
        #     # print(x[2]['h2h'][2])
    highest = 0
    for x in ev_list:
        if(x[2]>highest):
            highest = x[2]
            best = x
        if x[2] == -100:  # broken predictions
            print(x)
    evdf = DataFrame(ev_list, columns=['teams','site','EV','outcome','win538','bookie%'])
    result = evdf.sort_values(['EV'], ascending=False)
    return result


def simple_xl(result):
    result.to_excel('fixedNames.xlsx')
    print("printed to xl")


def get_ev(win538, odds):
    if odds is None:
        return 0
    if win538 is None:
        return 0
    return (win538 * odds * 100) - 100


def many_sports():
    df1 = do_sport('soccer_epl')
    df2 = (do_sport('soccer_australia_aleague'))
    df3 = (do_sport('soccer_brazil_campeonato'))
    df4 = (do_sport('soccer_denmark_superliga'))
    df5 = (do_sport('soccer_efl_champ'))
    df6 = (do_sport('soccer_england_league1'))
    df7 = (do_sport('soccer_england_league2'))
    df8 = (do_sport('soccer_france_ligue_one'))
    df9 = (do_sport('soccer_france_ligue_two'))
    df10 = (do_sport('soccer_germany_bundesliga'))
    df11 = (do_sport('soccer_germany_bundesliga2'))
    df12 = (do_sport('soccer_italy_serie_a'))
    # df11 = (do_sport('soccer_italy_serie_b'))
    df13 = (do_sport('soccer_mexico_ligamx'))
    df14 = (do_sport('soccer_netherlands_eredivisie'))
    df15= (do_sport('soccer_portugal_primeira_liga'))
    df16= (do_sport('soccer_russia_premier_league'))
    df17= (do_sport('soccer_spain_la_liga'))
    df18= (do_sport('soccer_spl'))
    df19= (do_sport('soccer_switzerland_superleague'))
    df20 = (do_sport('soccer_turkey_super_league'))

    with pd.ExcelWriter('bigManyUSA.xlsx') as writer:
        df1.to_excel(writer, sheet_name='epl')
        df2.to_excel(writer, sheet_name='australia1')
        df3.to_excel(writer, sheet_name='brazil')
        df4.to_excel(writer, sheet_name='denmark')
        df5.to_excel(writer, sheet_name='efl champ')
        df6.to_excel(writer, sheet_name='england1')
        df7.to_excel(writer, sheet_name='england2')
        df8.to_excel(writer, sheet_name='france1')
        df9.to_excel(writer, sheet_name='france2')
        df10.to_excel(writer, sheet_name='germany1')
        df11.to_excel(writer, sheet_name='germany2')
        df12.to_excel(writer, sheet_name='italy1')
        df13.to_excel(writer, sheet_name='mexico')
        df14.to_excel(writer, sheet_name='netherlands')
        df15.to_excel(writer, sheet_name='portugal')
        df16.to_excel(writer, sheet_name='russia')
        df17.to_excel(writer, sheet_name='spain')
        df18.to_excel(writer, sheet_name='spl')
        df19.to_excel(writer, sheet_name='switz')
        df20.to_excel(writer, sheet_name='turkey')

def fix_538(team):
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


many_sports()



