"""
Pickem ETL
Author: Gabe Baduqui

Scrape all Game-specific data elements for a given Game ID.
"""
import requests
import etl.extract.extract as ex
import etl.extract.cfb.scrape_game_page as cfb_game
import etl.extract.nfl.scrape_game_page as nfl_game
import etl.extract.mlb.scrape_game_page as mlb_game
import etl.extract.nba.scrape_game_page as nba_game
from bs4 import BeautifulSoup

def get_team_id(team_container_div: str, league: str, logfile: object):
    """Function that extracts the Team ID from the HREF attribute from a given Anchor Tag.
       Accepts `team_container_div`: <div> HTML Element String, `league`: String, `logfile`: Logfile Object
       Returns `team_id`: String"""
    # Example `team_container_div` string: '<div class="Gamestrip__Team--xxxx">...</div>'
    try:
        team_anchor_tag = team_container_div.find('div', class_='Gamestrip__TeamContainer').find('div', class_='Gamestrip__InfoLogo').find('a', href=True)
        team_href_attr = team_anchor_tag['href']

        if league.upper() == 'CFB':
            team_id = cfb_game.get_team_id(team_href_attr)
        if league.upper() == 'NFL':
            team_id = nfl_game.get_team_id(team_href_attr)
        if league.upper() == 'MLB':
            team_id = mlb_game.get_team_id(team_href_attr)
        if league.upper() == 'NBA':
            team_id = nba_game.get_team_id(team_href_attr)
        
        logfile.write(f'{team_id}\n')
    except Exception as e:
        team_id = '0'
        logfile.write(f'{e}\n')
    return team_id

def get_away_team_id(gamestrip: str, league: str, logfile: object):
    """Function that scrapes the Away Team ID from a given 'Gamestrip' DIV tag.
       Accepts `gamestrip`: <div> HTML Element String, `league`: String, `logfile`: Logfile Object
       Returns `team_id`: String"""
    # Example `gamestrip` string: '<div class="Gamestrip relative overflow-hidden college-football Gamestrip--xl Gamestrip--post bb">...</div>'
    logfile.write(f'away_team_id: ')
    away_team_container = gamestrip.find('div', class_='Gamestrip__Team--left')
    team_id = get_team_id(away_team_container, league, logfile)
    return team_id

def get_home_team_id(gamestrip: str, league: str, logfile: object):
    """Function that scrapes the Home Team ID from a given 'Gamestrip' DIV tag.
       Accepts `gamestrip`: <div> HTML Element String, `league`: String, `logfile`: Logfile Object
       Returns `team_id`: String"""
    # Example `gamestrip` string: '<div class="Gamestrip relative overflow-hidden college-football Gamestrip--xl Gamestrip--post bb">...</div>'
    logfile.write(f'home_team_id: ')
    home_team_container = gamestrip.find('div', class_='Gamestrip__Team--right')
    team_id = get_team_id(home_team_container, league, logfile)
    return team_id


def get_box_score_table(gamestrip: str):
    """Function that scrapes the Box Score from a given 'Gamestrip' DIV tag.
       Accepts `gamestrip`: <div> HTML Element String
       Returns `box_score_table`: <tbody> HTML Element String"""
    # Example `gamestrip` string: '<div class="Gamestrip relative overflow-hidden college-football Gamestrip--xl Gamestrip--post bb">...</div>'
    try:
        box_score_container = gamestrip.find('div', class_='Gamestrip__Overview').find('div', class_='Gamestrip__Table').find('div', class_='Table__Scroller').find('table')
        box_score_table = box_score_container.find('tbody', class_='Table__TBODY')
    except:
        box_score_table = None
    return box_score_table

def get_box_score(box_score_quarters: list):
    """Function that extracts the score from each quarter of a given box score
       Accepts `box_score_quarters`: List
       Returns `box_score`: Dictionary"""
    box_score = {}
    box_score['1'] = box_score_quarters[1].text
    box_score['2'] = box_score_quarters[2].text
    box_score['3'] = box_score_quarters[3].text
    box_score['4'] = box_score_quarters[4].text

    if len(box_score_quarters) == 7:
        box_score['overtime'] = box_score_quarters[5].text
    else:
        box_score['overtime'] = 0

    box_score['total'] = box_score_quarters[-1].text
    return box_score


def get_away_box_score(gamestrip: str, logfile: object):
    """Function that scrapes the Away Team Box Score from a given 'Gamestrip' DIV tag.
       Accepts `gamestrip`: <div> HTML Element String
       Returns `away_box_score`: Dictionary"""
    # Example `gamestrip` string: '<div class="Gamestrip relative overflow-hidden college-football Gamestrip--xl Gamestrip--post bb">...</div>'
    away_box_score = {}
    try:
        box_score_tbody = get_box_score_table(gamestrip)
        away_box_score_quarters = box_score_tbody.find_all('tr')[0].find_all('td')
        away_box_score = get_box_score(away_box_score_quarters)
    except:
        away_box_score = {'1': 0, '2': 0, '3': 0, '4': 0, 'overtime': 0, 'total': 0}     
    logfile.write(f'away_box_score: {away_box_score}\n')
    return away_box_score

def get_home_box_score(gamestrip: str, logfile: object):
    """Function that scrapes the Home Team Box Score from a given 'Gamestrip' DIV tag.
       Accepts `gamestring`: <div> HTML Element String
       Returns `home_box_score`: Dictionary"""
    # Example `gamestrip` string: '<div class="Gamestrip relative overflow-hidden college-football Gamestrip--xl Gamestrip--post bb">...</div>'
    home_box_score = {}
    try:
        box_score_tbody = get_box_score_table(gamestrip)
        home_box_score_quarters = box_score_tbody.find_all('tr')[1].find_all('td')
        home_box_score = get_box_score(home_box_score_quarters)          
    except:
        home_box_score = {'1': 0, '2': 0, '3': 0, '4': 0, 'overtime': 0, 'total': 0}
    logfile.write(f'home_box_score: {home_box_score}\n')
    return home_box_score


def get_stadium(information: str, logfile: object):
    """Function that scrapes the Stadium Name from a given 'GameInfo' Section tag.
       Accepts `information`: <section> HTML Element String, `logfile`: File object
       Returns `stadium_name: String`"""
    # Example `information` string: '<section class="Card GameInfo">...</section>
    try:
        stadium_name = information.find('div', class_='GameInfo__Location').text
        logfile.write(f'stadium_name: {stadium_name}\n')
    except Exception as e:
        stadium_name = ''
        logfile.write(f'stadium_name: {e}\n')
    return stadium_name

def get_location(information: str, logfile: object):
    """Function that scrapes the City and State from a given 'GameInfo' Section tag.
       Accepts `information`: <section> HTML Element String, `logfile`: File object
       Returns `location`: String"""
    # Example `information` string: '<section class="Card GameInfo">...</section>
    try:
        location = information.find('span', class_='Location__Text').text
        logfile.write(f'location: {location}\n')
    except Exception as e:
        location = ''
        logfile.write(f'location: {e}\n')
    return location

def get_timestamp(information: str, logfile: object):
    """Function that scrapes the Game Date and Time from a given 'information' DIV tag.
       Accepts `information`: <div> HTML Element String, `logfile`: File object
       Returns `game_timestamp`: String"""
    # Example `information` string: '<section class="Card GameInfo">...</section>
    try:
        game_timestamp = information.find('div', class_='GameInfo__Meta').find_all('span')[0].text
        logfile.write(f'game_timestamp: {game_timestamp}\n')
    except Exception as e:
        game_timestamp = ''
        logfile.write(f'game_timestamp: {e}\n')
    return game_timestamp

def get_tv_coverage(information: str, logfile: object):
    """Function that scrapes the TV Coverage Channel from a given 'information' DIV tag.
       Accepts `information`: <div> HTML Element String, `logfile`: File object
       Returns `tv_coverage`: String"""
    # Example `information` string: '<section class="Card GameInfo">...</section>
    try:
        tv_coverage = information.find('div', class_='GameInfo__Meta').find_all('span')[1].text
        logfile.write(f'tv_coverage: {tv_coverage}\n')
    except Exception as e:
        tv_coverage = ''
        logfile.write(f'tv_coverage: {e}\n')
    return tv_coverage

def get_betting_line(information: str, logfile: object):
    """Function that scrapes the Betting Line from a given 'information' DIV tag.
       Accepts `information`: <div> HTML Element String, `logfile`: File object
       Returns `betting_line`: String"""
    # Example `information` string: '<section class="Card GameInfo">...</section>
    try:
        betting_line = information.find('div', class_='GameInfo__BettingItem line').text
        logfile.write(f'betting_line: {betting_line}\n')
    except Exception as e:
        betting_line = ''
        logfile.write(f'betting_line: {e}\n')
    return betting_line

def get_betting_over_under(information: str, logfile: object):
    """Function that scrapes the Betting Over/Under from a given 'information' DIV tag.
       Accepts `information`: <div> HTML Element String, `logfile`: File object
       Returns `betting_over_under`: String"""
    # Example `information` string: '<section class="Card GameInfo">...</section>
    try:
        betting_over_under = information.find('div', class_='GameInfo__BettingItem ou').text
        logfile.write(f'betting_over_under: {betting_over_under}\n')
    except Exception as e:
        betting_over_under = ''
        logfile.write(f'betting_over_under: {betting_over_under}\n')
    return betting_over_under

def get_stadium_capacity(information: str, logfile: object):
    """Function that scrapes the Stadium Capacity from a given 'information' DIV tag.
       Accepts `information`: <div> HTML Element String, `logfile`: File object
       Returns `stadium_capacity`: String"""
    # Example `information` string: '<section class="Card GameInfo">...</section>
    try:
        stadium_capacity = information.find('div', class_='Attendance__Capacity').text
        logfile.write(f'stadium_capacity: {stadium_capacity}\n')
    except Exception as e:
        stadium_capacity = 0
        logfile.write(f'stadium_capacity: {e}\n')
    return stadium_capacity

def get_attendance(information: str, logfile: object):
    """Function that scrapes the Game Attendance from a given 'information' DIV tag.
       Accepts `information`: <div> HTML Element String, `logfile`: File object
       Returns `attendance`: String"""
    # Example `information` string: '<section class="Card GameInfo">...</section>
    try:
        attendance = information.find('div', class_='Attendance__Numbers').text
        logfile.write(f'attendance: {attendance}\n')
    except Exception as e:
        attendance = ''
        logfile.write(f'attendance: {e}\n')
    return attendance


def get_away_winning_probability(matchup: str, logfile: object):
    """Function that scrapes the winning probability percentage of the Away Team for a given 'matchup' DIV tag.
       Accepts `matchup`: <div> HTML Element String, `logfile`: File object
       Returns `win_pct`: String"""
    # Example `matchup` string: '<div class="matchupPredictor">...</div>'
    try:
        away_win_pct = matchup.find('div', class_='matchupPredictor__teamValue--b').text
        logfile.write(f'away_win_pct: {away_win_pct}\n')
    except Exception as e:
        away_win_pct = ''
        logfile.write(f'away_win_pct: {e}\n')
    return away_win_pct

def get_home_winning_probability(matchup: str, logfile: object):
    """Function that scrapes the winning probability percentage of the Away Team for a given 'matchup' DIV tag.
       Accepts `matchup`: <div> HTML Element String, `logfile`: File object
       Returns `win_pct`: String"""
    # Example `matchup` string: '<div class="matchupPredictor">...</div>'
    try:
        home_win_pct = matchup.find('div', class_='matchupPredictor__teamValue--a').text
        logfile.write(f'home_win_pct: {home_win_pct}\n')
    except Exception as e:
        home_win_pct = ''
        logfile.write(f'home_win_pct: {e}\n')
    return home_win_pct


def get_game_data(league: str, game_id: str, logfile: object):
    """Function that scrapes the webpage of a given Game ID and extracts needed data fields.
       Accepts `game_id`: String, `espn_game_url`: String, `logfile`: File Object
       Returns `game_data`: Dictionary"""
    print(f'~~ Scraping {league.upper()} GameID {game_id} data')
    logfile.write(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nScraping {league.upper()} GameID {game_id} data\n')

    if league.upper() == 'CFB':
        espn_game_url = f'https://www.espn.com/college-football/game/_/gameId/{game_id}'
    else:
        espn_game_url = f'https://www.espn.com/{league.lower()}/game/_/gameId/{game_id}'

    game_resp = requests.get(espn_game_url, headers=ex.custom_header)
    game_soup = BeautifulSoup(game_resp.content, 'html.parser')

    # Instantiate `game_data` dictionary
    game_data = {
        'game_id': game_id,
        'league': league
    }

    # Instantiate Gamestring Container and scrape data fields
    try:
        gamestrip_div = game_soup.find('div', class_='Gamestrip')
        away_team_id = get_away_team_id(gamestrip_div, league, logfile)
        home_team_id = get_home_team_id(gamestrip_div, league, logfile)
        game_data['away_team'] = away_team_id
        game_data['home_team'] = home_team_id

        if away_team_id == '0':
            print(f'~~~~ Could not extract Away Team ID for GameID: {game_id}')
        if home_team_id == '0':
            print(f'~~~~ Could not extract Home Team ID for GameID: {game_id}')

        if league in ['CFB', 'NFL']:
            game_data['away_team_box_score'] = get_away_box_score(gamestrip_div, logfile)
            game_data['home_team_box_score'] = get_home_box_score(gamestrip_div, logfile)
        else:
            game_data['away_team_box_score'] = None
            game_data['home_team_box_score'] = None
        
    except:
        print(f'~~~~ Could not find Gamestrip Container for GameID: {game_id}')
        logfile.write(f'~~~~ Could not find Gamestrip Container for Game ID: {game_id}\n')
    
    # Instantiate Information Section and scrape data fields
    info_section = game_soup.find('section', class_='GameInfo')
    game_data['stadium'] = get_stadium(info_section, logfile)
    game_data['location'] = get_location(info_section, logfile)
    game_data['game_timestamp'] = get_timestamp(info_section, logfile)
    game_data['tv_coverage'] = get_tv_coverage(info_section, logfile)
    game_data['betting_line'] = get_betting_line(info_section, logfile)
    game_data['betting_over_under'] = get_betting_over_under(info_section, logfile)
    game_data['stadium_capacity'] = get_stadium_capacity(info_section, logfile)
    game_data['attendance'] = get_attendance(info_section, logfile)
    
    # Instantiate Matchup Container and scrape data fields
    try: 
        matchup_div = game_soup.find('div', class_='matchupPredictor')
        game_data['away_win_pct'] = get_away_winning_probability(matchup_div)
        game_data['home_win_pct'] = get_home_winning_probability(matchup_div)
    except:
        game_data['away_win_pct'] = None
        game_data['home_win_pct'] = None
        logfile.write(f'away_win_pct: None\n')
        logfile.write(f'home_win_pct: None\n')

    logfile.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')

    return game_data