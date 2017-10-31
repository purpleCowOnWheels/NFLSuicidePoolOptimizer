used_teams      = []
homeField       = 65            #https://fivethirtyeight.com/datalab/introducing-nfl-elo-ratings/
nUnfixed        = 4             #how many games at the end of the season should not get fixed out immediately (to avoid finding local max)
nBest           = 50            #how maybe of the top paths should be considered in convergence calculation
fixAt           = 0.7           #what percent of nBest must match before fixing out a pick
valMethod       = 'hyperbolic'  #linear or hyperbolic. Hyperbolic will heavily favor paths that survive the first few weeks
last_week       = 17            #last week included in the optimization. generally leave at 17 and change valMethod
fixed_teams     = {}            #{ '9': 'Seattle Seahawks'}
                                #Use this to manually fix out a team. names come from keys of schedule_ELO_name_mapping

ELO_url         = 'https://projects.fivethirtyeight.com/2017-nfl-predictions/'
schedule_url    = 'https://www.pro-football-reference.com/years/2017/games.htm'

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