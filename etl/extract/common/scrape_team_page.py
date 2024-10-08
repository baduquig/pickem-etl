"""
Pickem ETL
Author: Gabe Baduqui

Scrape all Team-specific data elements for a given Team ID
"""
import requests
import etl.extract.extract as ex
import etl.extract.cfb.scrape_team_page as cfb_team
import etl.extract.nfl.scrape_team_page as nfl_team
import etl.extract.common.scrape_team_color_codes as colors
from bs4 import BeautifulSoup
from datetime import datetime

today = datetime.now().date()
season_start = datetime(2024, 8, 24).date()

def get_logo_url(league: str, team_id: str, logfile: object):
    """Function that extracts the ESPN url to a given team's PNG image logo
       Accepts `league`: String, team_id`: String, `logfile`: File Object
       Returns `logo_url`: String"""
    if league.upper() == 'CFB':
        logo_url = f'https://a.espncdn.com/combiner/i?img=/i/teamlogos/ncaa/500/{team_id}.png'
    else:
        logo_url = f'https://a.espncdn.com/combiner/i?img=/i/teamlogos/{league.lower()}/500/{team_id}.png'
    logfile.write(f'logo_url: {logo_url}\n')
    return logo_url

def get_clubhouse_header_span(clubhouse_div: str):
    """Function that scrapes and returns the <H1> tag storing the team name and mascot
       Accepts `clubhose_div`: <div> HTML Element String
       Returns `header_span`: <span> HTML Element String"""
    # Example `clubhouse_div` string: '<div class="ClubhouseHeader__Main">...</div>'
    try:
        header_h1 = clubhouse_div.find('h1', class_='ClubhouseHeader__Name')
        header_span = header_h1.find('span', class_='flex')
    except:
        header_span = ''
    return header_span

def get_team_name(clubhouse_div: str, logfile: object):
    """Function that scrapes the team name from a given ClubhouseHeader DIV tag
       Accepts `clubhouse_div`: <div> HTML Element String, `logfile`: File Object
       Returns `team_name`: String"""
    # Example `clubhouse_div` string: '<div class="ClubhouseHeader__Main">...</div>'
    header_span = get_clubhouse_header_span(clubhouse_div)
    try:
        team_name_span = header_span.find_all('span')[0]
        team_name = team_name_span.text
        logfile.write(f'team_name: {team_name}\n')
    except Exception as e:
        team_name = ''
        logfile.write(f'team_name: {e}\n')
    return team_name

def get_team_mascot(clubhouse_div: str, logfile: object):
    """Function that scrapes the team name from a given ClubhouseHeader DIV tag
       Accepts `clubhouse_div`: <div> HTML Element String, `logfile`: File Object
       Returns `team_name`: String"""
    # Example `clubhouse_div` string: '<div class="ClubhouseHeader__Main">...</div>'
    header_span = get_clubhouse_header_span(clubhouse_div)
    try:
        team_mascot_span = header_span.find_all('span')[1]
        team_mascot = team_mascot_span.text
        logfile.write(f'team_mascot: {team_mascot}\n')
    except Exception as e:
        team_mascot = ''
        logfile.write(f'team_mascot: {e}\n')
    return team_mascot


def get_conference_name(standings_section: str, logfile: object):
    """Function that scrapes the header of the a given TeamStandings SECTION tag and extracts the conference name
       Accepts `standings_section`: <section> HTML Element String, `logfile`: File Object
       Returns `conference_name`: String"""
    # Example `standings_section String: '<section class="Card TeamStandings">...</section>'`
    try:
        section_header = standings_section.find('div', class_='Card__Header__Title__Wrapper')
        conference_name = section_header.find('h3').text
        logfile.write(f'conference_name: {conference_name}\n')
    except Exception as e:
        conference_name = ''
        logfile.write(f'conference_name: {e}\n')
    return conference_name

def get_team_standing_row(conference_standing_rows: str, team_name: str):
    """Function that extracts the the <tr> tag storing the conference and overall records for the current team being scraped
       Accepts `conference_standing_rows`: List of <tr> HTML Element Strings, `team_name`: String
       Returns `team_standing_row`: <tr> HTML Element String"""
    # Example `conference_standing_rows` list: ['<tr class="Table__TR Table__TR--sm Table__even" data-idx="n">...</tr>', ....]
    team_standing_row = ''
    try:
        for row in conference_standing_rows:
            row_anchor = row.find_all('td', class_='Table__TD')[0].find('a')
            anchor_text = row_anchor.text
            class_name = row_anchor['class']
            bolded_class = 'AnchorLink fw-bold'

            if ((anchor_text == team_name) or (class_name == bolded_class)):
                team_standing_row = row
    except:
        team_standing_row = ''
    return team_standing_row

def get_conference_record(league: str, team_standing_row: str, logfile: object):
    """Function that extracts the conference record from a given TR tag
       Accepts `league`: String, `team_standing_row`: <tr> HTML Element String, `logfile`: File Object
       Returns `conference_record`: String"""
    # Example `team_standing_row` string: '<div class="Table__TR Table__TR--sm Table__even">...</div>'
    if league.upper() == 'CFB':
        conf_record = cfb_team.get_conference_record(team_standing_row)
    else:
        conf_record = ''
    logfile.write(f'conf_record: {conf_record}\n')
    return conf_record

def get_overall_record(league: str, team_standing_row: str, logfile: object):
    """Function that extracts the overall record from a given TR tag
       Accepts `league`: String, `team_standing_row`: <tr> HTML Element String, `logfile`: File Object
       Returns `overall_record`: String"""
    # Example `team_standing_row` string: '<div class="Table__TR Table__TR--sm Table__even">...</div>'
    if league.upper() == 'CFB':
        overall_record = cfb_team.get_overall_record(team_standing_row)
    else:
        overall_record = nfl_team.get_overall_record(team_standing_row, league)
    logfile.write(f'overall_record: {overall_record}\n')
    return overall_record


def get_team_data(league: str, team_id: str, logfile: object):
    """Function that scrapes the webpage of a given Team and extracts the needed data fields.
       Accepts `league`: String, team_id`: String, `espn_team_url`: String `logfile`: File Object
       Returns team_data: Dictionary"""
    print(f'~~ Scraping {league.upper()} TeamID {team_id} data')
    logfile.write(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nScraping {league.upper()} TeamID {team_id} data\n')

    # Scrape HTML from HTTP request to the URL above and store in variable `page_soup`
    if league.upper() == 'CFB':
        espn_team_url = f'https://www.espn.com/college-football/team/_/id/{team_id}'
    else:
        espn_team_url = f'https://www.espn.com/{league.lower()}/team/_/name/{team_id}'

    team_resp = requests.get(espn_team_url, headers=ex.custom_header)
    team_soup = BeautifulSoup(team_resp.content, 'html.parser')

    # Instantiate `team_data` dictionary
    team_data = {
        'team_id': team_id,
        'league': league
    }

    # Instantiate Clubhouse Container and scrape data fields
    try:
        clubhouse_div = team_soup.find('div', class_='ClubhouseHeader').find('div', class_='ClubhouseHeader__Main')
        team_data['name'] = get_team_name(clubhouse_div, logfile)
        team_data['mascot'] = get_team_mascot(clubhouse_div, logfile)
        #team_data['primary_color'], team_data['secondary_color'], team_data['accent_color'] = colors.get_team_colors(team_data['name'], team_data['mascot'], logfile)
        team_data['primary_color'], team_data['secondary_color'], team_data['accent_color'] = '', '', ''
        team_data['logo_url'] = get_logo_url(league, team_id, logfile)
    except Exception as e:
        logfile.write(f'Could not find `ClubhouseHeader__Main` DIV: {e} for Team {team_id}\n')

    # Instantiate Team Standings Section and scrape data fields
    try:
        standings_section = team_soup.find('section', class_='TeamStandings')
        team_data['conference_name'] = get_conference_name(standings_section, logfile)

        if today >= season_start:
            standings_tables = standings_section.find('div', class_='Wrapper Card__Content').find_all('div', class_='ResponsiveTable') 
            standings_rows = []
            for standings_table in standings_tables:
                standings_table.find('div', class_='Table__ScrollerWrapper').find('div', class_='Table__Scroller').find('table')
                standings_rows = standings_table.find('tbody').find_all('tr')
                team_standing_row = get_team_standing_row(standings_rows, team_data['name'])
                if team_standing_row != '' and team_standing_row is not None:
                    break        
            team_data['conference_record'] = get_conference_record(league, team_standing_row, logfile)
            team_data['overall_record'] = get_overall_record(league, team_standing_row, logfile)
        else:
            team_data['conference_record'] = '0-0'
            team_data['overall_record'] = '0-0'

    except Exception as e:
        logfile.write(f'Could not find `TeamStandings` DIV: {e} for Team {team_id}\n')
    
    logfile.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')

    return team_data
