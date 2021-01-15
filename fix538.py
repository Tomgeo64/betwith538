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
        'Gent': 'KAA Gent',
        'SV Zulte-Waregem': 'SV Zulte Waregem',
        'Oostende': 'KV Oostende',
        'Cercle Brugge KSV': 'Cercle Brugge',
        'Royal Antwerp': 'Antwerp',
        'Beerschot Wilrijk': 'KFCO Beerschot-Wilrijk',
        'Sint Truiden': 'St. Truidense',
        'Charleroi': 'Sporting de Charleroi',
        'Royal Excel Mouscron': 'Mouscron-Peruwelz',
        'Molde FK': 'Molde',
        'Salzburg':'FC Salzburg',
        'Granada CF': 'Granada',
        'Maccabi Tel Aviv FC': 'Maccabi Tel-Aviv',
        'Royal Antwerp FC': 'Antwerp',
        'Krasnodar': 'FC Krasnodar',
        'BSC Young Boys': 'Young Boys',
        'Tottenham Hotspur FC': 'Tottenham Hotspur',
        'Slavia Praha': 'Slavia Prague',
        'Roma': 'AS Roma',
        'Borussia Mönchengladbach': 'Borussia Monchengladbach',
        'SS Lazio': 'Lazio',
        'Bayern München': 'Bayern Munich',
        'Ankaragücü': 'Ankaragucu',
        'SPAL': 'Spal',
        'Pescara': 'US Pescara',
        'Venezia': 'F.B.C Unione Venezia',
        'Leuven': 'OH Leuven',
        'Pordenone': 'Pordenone Calcio',
        'TSG 1899 Hoffenheim': 'TSG Hoffenheim',
        'SSC Napoli': 'Napoli',
        'Leverkusen': 'Bayer Leverkusen',
        'Leicester City FC': 'Leicester City'

    }
    if team in translateTo538:
        return translateTo538[team]
    else:
        return team
