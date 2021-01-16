#! /usr/bin/env python
import requests
import pandas as pd

script = 'hdad'
version = 'v0.21'
prompt = '\n>>> '

# Documentation on NHL api: https://gitlab.com/dword4/nhlapi
domain = 'https://statsapi.web.nhl.com'
api = 'api/v1'
view = 'teams'
subview = 'roster'
season = '20202021'
mod = f'stats?stats=statsSingleSeason&season={season}'
exclude = ('positionCode', 'positionAbbreviation', 'id', 'link', \
            'active', 'alternateCaptain', 'rosterStatus', 'teamLink', \
            'teamId', 'primaryNumber', 'firstName', 'lastName', \
            'currentTeam', 'primaryPosition', 'teamName')

def call(url):
    r = requests.get(url)
    return r.json()

def get_teams():
    url = f'{domain}/{api}/{view}'
    r = call(url)

    keys = 0
    teams = {}
    for team in r['teams']:
        keys = keys + 1
        values = (team['link'], team['name'])
        teams[keys] = values

    return teams

def pick_team(teams):
    inpmsg = f'\nChoose a team number...{prompt}'

    while True:
        choice = int(input(inpmsg))
        if choice in teams.keys():
            break
        else:
            print(f'\nInvalid input. Please try again...')

    tname = teams[choice][1]
    print(f'{tname} chosen.')

    tlink = teams[choice][0]
    return tlink, tname

def get_players(tlink):
    url = f'{domain}/{tlink}/{subview}'
    r = call(url)
    roster = r['roster']

    players = {}
    for player in roster:
        keys = int(player['jerseyNumber'])
        values = player['person']
        players[keys] = values

    return players

def pick_player(players, tname):
    inpmsg = f'\nChoose a jersey number in {tname}...{prompt}'

    while True:
        choice = int(input(inpmsg))
        if choice in players.keys():
            break
        else:
            print(f'\nNo number {choice} in {tname}. Try again...')

    pname = players[choice]['fullName']
    print(f'{pname} chosen.')

    plink = players.get(choice)['link']
    return plink

def player_info(plink):
    url = f'{domain}/{plink}'
    r = call(url)

    players = r['people'][0]
    ct = players['currentTeam']
    curteam = {f'team{k.title()}': v for k, v in ct.items()}

    ppos = players['primaryPosition']
    primpos = {f'position{k.title()}': v for k, v in ppos.items()}

    info = {**players, **curteam, **primpos}
    return info

def player_stats(plink):
    url = f'{domain}/{plink}/{mod}'
    r = call(url)

    st = r['stats'][0]
    sp = st['splits'][0]
    stats = sp['stat']

    return stats

def create_output(info, stats):
    merge = {**info, **stats}
    clean = {k: v for k, v in merge.items() \
            if not k.startswith(exclude)}
    df = pd.DataFrame.from_dict(clean, orient='index')

    output = str(df).split('\n', 1)[1]
    return output


try:
    print(f'Starting {script} {version}\n')
    
    teams = get_teams()
    for k,v in teams.items():
        print(f'Team {k}: {v[1]}')
    
    tlink, tname = pick_team(teams)
    players = get_players(tlink)
    
    while True:
        plink = pick_player(players, tname)
        info = player_info(plink)
        stats = player_stats(plink)
        output = create_output(info, stats)
        print(output)

except KeyboardInterrupt:
    print('\nInterrupt signal received. Exiting.')
    exit()

except:
    raise
