import pandas as pd
import re
import timestring
import pdb
from os import system
from random import sample
from requests import get
from datetime import date, datetime
from numpy import concatenate, prod
#sys.path.append( 'C:/Users/danie/Dropbox/Projects/EntityResolution' )
#from ClassEntityResolution import *

def _getELO(ELO_url):
    web         = get(ELO_url)
    ELOTable    = pd.read_html(web.text)[0] # Returns list of all tables on page
    ELOCol      = ('Unnamed: 0_level_0', 'Unnamed: 0_level_1', 'elo ratingelo')
    TeamCol     = ('playoff chances', 'playoff chances', 'team')
    ELOTable    = ELOTable[[ELOCol, TeamCol]]
    ELOTable.columns = ['ELO', 'Team']
    return(ELOTable)

def _cleanELOTable(ELOTable):
    ELO = {}
    regex = '[\-0-9]'
    for index, row in ELOTable.iterrows():
        this_team        = re.sub( regex,'',row.Team ).rstrip()
        ELO[ this_team ] = {'ELO': float(row.ELO), 'Team': this_team}
    #    print( re.sub( regex,'',row.Team ).rstrip() )
    return(ELO)

def _getPairwiseProbs(ELO, homeField):
    for homeTeam in ELO.keys():
        for awayTeam in ELO.keys():
            #https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
            ELODiff = ELO[awayTeam]['ELO'] - ( ELO[homeTeam]['ELO'] + 65 )
            ELO[homeTeam][awayTeam] = 1 / (1 + 10**(ELODiff / 400)) 
    return(ELO)

def _getSchedule(schedule_url, last_week):
    web         = get(schedule_url)
    schedule    = pd.read_html(web.text)[0]
    schedule    = schedule[['Week', 'Date', 'Winner/tie', 'Loser/tie']]
    year_str    = str(date.today().year)
    schedule['Date']    = schedule['Date'].apply(lambda x: timestring.Date(''.join([x, ' ', year_str])))
    schedule.columns    = ['Week', 'Date', 'Visitor', 'Home']
    schedule            = schedule[ (schedule.Week != 'Week') & (date.today() <= schedule.Date) ]
    schedule['Week']    = pd.to_numeric( schedule.Week, errors = 'ignore' )
    schedule            = schedule[ (schedule.Week <= last_week) ]
    return(schedule)

def _addWinProbsToSchedule(schedule, winProbs, name_map):
    schedule['hProb']       = schedule.apply(lambda row: winProbs[name_map[row.Home]][name_map[row.Visitor]], axis=1)
    schedule['favorite']    = schedule.apply(lambda row: row.Home if row.hProb > 0.5 else row.Visitor, axis = 1 )
    schedule['fProb']       = schedule.apply(lambda row: max( row.hProb, 1 - row.hProb ), axis = 1 )
    schedule                = schedule.sort_values(['Week','fProb'], ascending = [1,0])
    return( schedule )

def getPicks( schedule, these_used_teams, last_week ):
    #a function to pick a possible set of team selections to be evaluated
    probs = []
    weeks = set( schedule.Week )
    for week in weeks:
        #pick a winner in a given week
        #candidates are all favorites
        this_schedule   = schedule[schedule.Week == week ]
        this_schedule   = this_schedule[~schedule.favorite.isin(these_used_teams)]
        candidates      = set(this_schedule.favorite)
        if( week == last_week ):
            #take the best remaining probability
            these_used_teams.append(this_schedule.favorite.iloc[0])
            probs.append(this_schedule.fProb.iloc[0])
        else:
            this_team = sample(candidates, 1)[0]
            these_used_teams.append(this_team)
            probs.append(float(this_schedule.fProb[this_schedule.favorite == this_team]))
    return(pickPath( these_used_teams, probs, prod(probs)))

def getBestPicks( schedule, used_teams, last_week ):
    bestPicks   = []
    found       = False
    counter     = 0
    fixedTeams  = []
    last_winner = datetime.now()
    
    while not found:
        #get a path and add it to the set of tested paths
        #pdb.set_trace()
        if ( datetime.now() - last_winner ).seconds >= 2:
            found = True
            
        these_used_teams = used_teams[:]
        thisPath    = getPicks( schedule, these_used_teams, last_week )
        bestPicks.append(thisPath)
        
        #restrict down to the 10 best paths
        bestPicks.sort()
        bestPicks = bestPicks[:10]
        
        if thisPath in bestPicks:
            system('cls||clear')
            print( '######## BEST PATHS START ########\n')
            for path in bestPicks:
                print( path, '\n' )
            print( '######## BEST PATHS END ########\n')
            last_winner = datetime.now()
        elif counter % 1000 == 0:
            print('Number of paths tested: ', str(counter))
        counter+=1

class pickPath:
    def __init__(
        self,
        picks   = [ ], #array of team names of picked winners
        probs   = [ ], #probabilities of winning assocaited with each pick
        surv    = 0,   #total survival probability
    ):
        self.picks  = picks
        self.probs  = probs
        self.surv   = surv
    
    def __lt__(self, other):
         return(self.surv < other.surv)
    
    def __str__(self):
        return( ', '.join( self.picks ) )
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return( self.picks == other.picks )
        else:
            return( False )
    
    def __ne__(self, other):
        return( not __eq__(self, other) )