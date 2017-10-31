import pandas as pd
import re
import timestring
import pdb
import sys
from os import system
from random import sample
from requests import get
from datetime import date, datetime
from numpy import concatenate, prod, unique, dot
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

def getPicks( schedule, these_used_teams, these_fixed_teams, last_week ):
    #a function to pick a possible set of team selections to be evaluated
    probs = []
    
    #get unique, ordered list of remaining weeks in the season
    weeks = list( set( schedule.Week ) )
    weeks.sort()
    for week in weeks:
        #pick a winner in a given week
        
        remaining_weeks = max(weeks) - week + 1 #inclusive of this week
        
        #candidates are all favorites that have not been used or fixed to another week 
        this_schedule   = schedule[schedule.Week == week ]
        this_schedule   = this_schedule[~( schedule.favorite.isin(these_used_teams) ) ]
        favorites       = this_schedule.favorite[~this_schedule.favorite.isin(these_fixed_teams.values())]

        #additionally, if there are k candidates and N weeks remaining (inclusive of this week), we should only consider top N candidates as we cannot use up all the other candidates. Note that this_schedule is already sorted by fProb (desc).
        favorites       = favorites[:remaining_weeks]
        candidates      = set(favorites)
        #print( 'candidates: ', candidates )
        if str(week) in these_fixed_teams.keys():
            this_team = these_fixed_teams[str(week)]
        #elif( week == last_week ):
            #take the best remaining probability
            #this_team = this_schedule.favorite.iloc[0]
        else:
            this_team = sample(candidates, 1)[0]
        these_used_teams.append(this_team)
        probs.append(float(this_schedule.fProb[this_schedule.favorite == this_team]))
    return(pickPath( these_used_teams, probs, prod(probs)))

def getFixedTeams( bestPicks, weeks, fixAt = 0.7, nUnfixed = 5 ):
    if fixAt <= 0.5:
        sys.exit('fixing out at less than 50% can give odd results. Try something larger')
    fixed_teams = {}
    for week in weeks:
        #don't fix weeks with very few remaining choices or the last week will very quickly fix at the local max
        if max(weeks) - week + 1 <= nUnfixed:
            return(fixed_teams)
        
        #get all picks this week across all the bestPick paths
        picks_this_week = [season.picks[week - min(weeks) ] for season in bestPicks]
        uniq_picks_n    = unique(picks_this_week, return_counts = True)
        uniq_picks      = uniq_picks_n[0]
        uniq_counts     = uniq_picks_n[1]
        maxN            = max(uniq_counts)  #the most time any one team was picked
        if maxN >= (len(bestPicks)*fixAt // 1):
            #add the name of the team at this most common value to the fixed team list
            fixed_teams[str(week)] = list(uniq_picks)[list(uniq_counts).index(maxN)]
    return(fixed_teams) 

def printBestPicks( bestPicks, fixed_teams, printCount ):
        system('cls||clear')
        if printCount != '':
            print( printCount )
        print( 'Fixed Teams (', str(len(fixed_teams)), '): ' , fixed_teams)
        
def getBestPicks( schedule, used_teams, fixed_teams, last_week, nBest = 25, nUnfixed = 3, timeout = 120 ):
    bestPicks   = []
    counter     = 0
    printCount  = ''
    last_winner = datetime.now()
    
    while True:
        #get a path and add it to the set of tested paths
        if len( bestPicks ) < nBest:
            these_fixed_teams = dict(fixed_teams)
        else:
            prior_fixed_teams   = dict(these_fixed_teams)
            these_fixed_teams   = getFixedTeams(bestPicks, set(schedule.Week), nUnfixed = nUnfixed)

            #once all the other weeks are optimized, go ahead and solve the last few weeks
            if (len(these_fixed_teams)+nUnfixed) == len(set(schedule.Week)):
                these_fixed_teams   = getFixedTeams(bestPicks, set(schedule.Week), nUnfixed = 0)
        
        #if its not finding anything new or all paths are now fixed, quit
        if ( datetime.now() - last_winner ).seconds >= timeout:
            printBestPicks( bestPicks, these_fixed_teams, printCount)
            print(schedule[schedule.Week == min(schedule.Week)])
            break
        if len(these_fixed_teams) == len(set(schedule.Week)):
            printBestPicks( bestPicks, these_fixed_teams, printCount)
            print(schedule[schedule.Week == min(schedule.Week)])
            break

        #get a new set of picks and add them to the best picks list
        thisPath    = getPicks( schedule, used_teams[:], these_fixed_teams, last_week )
        bestPicks.append(thisPath)
        
        #restrict down to the 10 best paths
        bestPicks.sort(reverse = True)
        #pdb.set_trace()
        bestPicks = bestPicks[:nBest]
        
        #if the new path is in the remaining 10, print it
        if thisPath in bestPicks:
            printBestPicks( bestPicks, these_fixed_teams, printCount)
            last_winner = datetime.now()
        elif counter % 1000 == 0:
            printCount = ''.join( ['Number of paths tested: ', str(counter)] )
        counter+=1

class pickPath:
    def __init__(
        self,
        picks       = [ ],  #array of team names of picked winners
        probs       = [ ],  #probabilities of winning assocaited with each pick
        surv        = 0,    #total survival probability
        pathValue   = 0,      #determined from the value function valuePath from probs - allows weighing earlier games higher
    ):
        self.picks      = picks
        self.probs      = probs
        self.surv       = surv
        self.pathValue  = self.valuePath(valMethod = 'linear')
    
    def valuePath(self, valMethod = 'hyperbola'):
        #pdb.set_trace()
        if valMethod == 'hyperbola':
            return dot( self.probs, [1/x for x in range(1, len(self.probs)+1)])
        elif valMethod == 'linear':
            return prod(self.probs)
        else:
            sys.exit('Undefined valueType')
    
    def __lt__(self, other):
         return(self.pathValue < other.pathValue)
    
    def __str__(self):
        return( ', '.join( self.picks ) )
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return( self.picks == other.picks )
        else:
            return( False )
    
    def __ne__(self, other):
        return( not __eq__(self, other) )