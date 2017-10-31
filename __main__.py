import nsp          #NFL Suicide Pool
import defaults
import pdb

from urllib.request import urlopen

#pdb.set_trace()

#get the ELO ratings from the website
ELOTable    = nsp._getELO( defaults.ELO_url )
ELO         = nsp._cleanELOTable(ELOTable)
#print(ELO)

win_probs   = nsp._getPairwiseProbs(ELO, defaults.homeField)
#print(win_probs['Philadelphia'])

#get a data frame with the upcoming schedule, including ELO-implied win probabilities for the home team
schedule    = nsp._getSchedule(defaults.schedule_url, defaults.last_week)
schedule    = nsp._addWinProbsToSchedule(schedule, win_probs, defaults.schedule_ELO_name_mapping)
print(schedule)

#pdb.set_trace()
bestPicks = nsp.getBestPicks( schedule, defaults.used_teams, defaults.fixed_teams, defaults.last_week )
