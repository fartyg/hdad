#! /usr/bin/env python
import requests
import pandas as pd

script = 'Hockeydad (hdad)'
version = 'v0.21'
season = '20202021'

#Documentation on NHL api: https://gitlab.com/dword4/nhlapi
domain = 'https://statsapi.web.nhl.com'
api = 'api/v1'
view = 'teams'
subview = 'roster'
modifier = f'stats?stats=statsSingleSeason&season={season}'
unwantedkeys = ('positionCode', 'positionAbbreviation', 'id', 'link', \
                'active', 'alternateCaptain', 'rosterStatus', 'teamLink', \
                'teamId', 'primaryNumber', 'firstName', 'lastName', \
                'currentTeam', 'primaryPosition')

def call(url):
    r = requests.get(url)
    return r.json()

def get_teams():
    url = f'{domain}/{api}/{view}'
    jr = call(url)

    keys = 0
    teams = {}
    for team in jr['teams']:
        keys = keys + 1
        values = (team['link'], team['name'])
        teams[keys] = values

    return teams

def pick_team(teams):
    inpmsg = '\nChoose a team number...\n>>> '

    while True:
        choice = int(input(inpmsg))
        if choice in teams.keys():
            break
        else:
            print('Invalid input. Please try again.')

    teamlink = teams[choice][0]
    teamname = teams[choice][1]
    return teamlink, teamname

def get_players(teamlink):
    url = f'{domain}/{teamlink}/{subview}'
    jr = call(url)
    roster = jr['roster']

    players = {}
    for player in roster:
        keys = int(player['jerseyNumber'])
        values = player['person']
        players[keys] = values

    return players

def pick_player(players, teamname):
    inpmsg = f'\nChoose a jersey number in {teamname}...\n>>> '
    while True:
        choice = int(input(inpmsg))
        if choice in players.keys():
            break
        else:
            print(f'No number {choice} found in {teamname}')

    pname = players[choice]['fullName']
    print(f'\n{pname} chosen.')

    playerlink = players.get(choice)['link']
    return playerlink

def player_info(playerlink):
    url = f'{domain}/{playerlink}'
    jr = call(url)

    players = jr['people'][0]
    ct = players['currentTeam']
    curteam = {f'team{k.title()}': v for k, v in ct.items()}

    ppos = players['primaryPosition']
    primpos = {f'position{k.title()}': v for k, v in ppos.items()}

    info = {**players, **curteam, **primpos}
    return info

def player_stats(playerlink):
    url = f'{domain}/{playerlink}/{modifier}'
    jr = call(url)

    st = jr['stats'][0]
    sp = st['splits'][0]
    stats =  sp['stat']

    return stats

def display(info, stats):
    merge = {**info, **stats}
    clean = {k: v for k, v in merge.items() \
            if not k.startswith(unwantedkeys)}

    df = pd.DataFrame.from_dict(clean, orient='index')
    output = str(df).split('\n', 1)[1]

    print(f'Displaying data...\n\n{output}')
    return None


try :

    print(f'Starting {script} {version}\n')
    
    teams = get_teams()
    for k,v in teams.items():
        print(f'Team {k}: {v[1]}')
    
    teamlink, teamname = pick_team(teams)
    players = get_players(teamlink)
    
    while True:
        playerlink = pick_player(players, teamname)
        info = player_info(playerlink)
        stats = player_stats(playerlink)
        display(info, stats)

    
except KeyboardInterrupt:
    print('\nInterrupt signal received. Exiting.')
    exit()

except Exception as e:
    raise
