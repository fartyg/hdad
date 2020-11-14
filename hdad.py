#! /usr/bin/env python
import requests
import pandas as pd

script = 'Hockeydad (hdad)'
version = 'v0.2'

#Documentation on NHL api: https://gitlab.com/dword4/nhlapi
domain = 'https://statsapi.web.nhl.com'
api = '/api/v1'
view = '/teams'
subview = '/roster'
modifier = '/stats?stats=statsSingleSeason&season=20192020'
unwantedkeys = ('positionCode', 'positionAbbreviation', 'id', 'link', \
                'active', 'alternateCaptain', 'rosterStatus', 'teamLink', \
                'teamId', 'primaryNumber', 'firstName', 'lastName', \
                'currentTeam', 'primaryPosition')

def call(url):
    r = requests.get(url)
    return r.json()

def get_teams():
    url = domain + api + view
    jr = call(url)
    keys = 0
    teamdict = {}
    for team in jr['teams']:
        keys = keys + 1
        links = team['link']
        names = team['name']
        values = (links, names)
        teamdict[keys] = values
    return teamdict

def pick_team(teamdict):
    teaminp = int(input('\nChoose a team number...\n>>> '))
    print(str(teamdict[teaminp][1]) + ' chosen.')
    teamlink = teamdict[teaminp][0]
    return teamlink

def player_by_jersey(teamlink):
    jninp = input('\nChoose a jersey number...\n>>> ')
    url = domain + teamlink + subview
    jr = call(url)
    roster = jr['roster']
    jndict = {}
    for item in roster:
        keys = item['jerseyNumber']
        values = item['person']
        jndict[keys] = values
    jndict = jndict.get(jninp)
    return jndict['link']

def player_info(playerlink):
    url = domain + playerlink
    jr = call(url)
    players = jr['people'][0]
    curteam = players['currentTeam']
    curteam = {f'team{k.title()}': v for k, v in curteam.items()}
    primpos = players['primaryPosition']
    primpos = {f'position{k.title()}': v for k, v in primpos.items()}
    info = {**players, **curteam, **primpos}
    return info

def player_stats(playerlink):
    url = domain + playerlink + modifier
    jr = call(url)
    stats = jr['stats'][0]
    splits = stats['splits'][0]
    stats =  splits['stat']
    return stats

def display(info, stats):
    merge = {**info, **stats}
    clean = {k: v for k, v in merge.items() \
            if not k.startswith(unwantedkeys)}
    df = pd.DataFrame.from_dict(clean, orient='index')
    output = str(df).split('\n',1)[1]
    print('Displaying data...')
    print('\n' + output)

#Run
print(script + ' ' + version + '\n')
teamdict = get_teams()
for k,v in teamdict.items():
    print('Team ' + str(k) + ': ' + str(v[1]))

teamlink = pick_team(teamdict)

while True:
    try:
        playerlink = player_by_jersey(teamlink)
        info = player_info(playerlink)
        stats = player_stats(playerlink)
        display(info, stats)
    except KeyboardInterrupt:
        print('\nInterrupt signal received. Exiting.')
        break
    except KeyError:
        print('Invalid input. Please try again...')
