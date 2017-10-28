used_teams  = []
last_week   = 17
ELO_url     = 'https://projects.fivethirtyeight.com/2017-nfl-predictions/'
homeField   = 65    #https://fivethirtyeight.com/datalab/introducing-nfl-elo-ratings/

schedule_url = 'https://www.pro-football-reference.com/years/2017/games.htm'

schedule_ELO_name_mapping = {
    'Arizona Cardinals': 'Arizona',
    'Atlanta Falcons': 'Atlanta',
    'Baltimore Ravens': 'Baltimore',
    'Buffalo Bills': 'Buffalo',
    'Carolina Panthers': 'Carolina',
    'Chicago Bears': 'Chicago',
    'Cincinnati Bengals': 'Cincinnati',
    'Cleveland Browns': 'Cleveland',
    'Dallas Cowboys': 'Dallas',
    'Denver Broncos': 'Denver',
    'Detroit Lions': 'Detroit',
    'Green Bay Packers': 'Green Bay',
    'Houston Texans': 'Houston',
    'Indianapolis Colts': 'Indianapolis',
    'Jacksonville Jaguars': 'Jacksonville',
    'Kansas City Chiefs': 'Kansas City',
    'Los Angeles Chargers': 'L.A. Chargers',
    'Los Angeles Rams': 'L.A. Rams',
    'Miami Dolphins': 'Miami',
    'Minnesota Vikings': 'Minnesota',
    'New York Giants': 'N.Y. Giants',
    'New York Jets': 'N.Y. Jets',
    'New England Patriots': 'New England',
    'New Orleans Saints': 'New Orleans',
    'Oakland Raiders': 'Oakland',
    'Philadelphia Eagles': 'Philadelphia',
    'Pittsburgh Steelers': 'Pittsburgh',
    'San Francisco 49ers': 'San Francisco',
    'Seattle Seahawks': 'Seattle',
    'Tampa Bay Buccaneers': 'Tampa Bay',
    'Tennessee Titans': 'Tennessee',
    'Washington Redskins': 'Washington',
}