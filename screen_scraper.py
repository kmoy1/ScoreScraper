import requests
import sys
from bs4 import BeautifulSoup
import re
from pandas import DataFrame
from datetime import datetime

def de_tag(raw_html):
	"""Removes tags from HTML."""
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

def team_names(soup_title):
	team_names = soup_title.split()[:3]
	away_team = team_names[0]
	home_team = team_names[2]
	return [away_team, home_team]

def teams_list(soup_title):
	"""Returns lists of teams for each play from soup.title. Assumes soup.string as input."""
	teams = []
	names = team_names(soup_title)
	all_logos = soup.find_all('img', class_='team-logo')
	logo_ref, logos_rest =  all_logos[:2], all_logos[2:]
	for logo in logos_rest:
		if logo == logo_ref[0]:
			teams.append(names[0])
		elif logo == logo_ref[1]:
			teams.append(names[1])
	return teams 

def abstime(time):
	"""Converts a time, in format XX:XX, to absolute time."""
	FMT = '%M:%S'
	tdelta = datetime.strptime('20:00', FMT) - datetime.strptime(time, FMT)
	return str(tdelta)[2:]

def times_list(soup_times):
	"""Returns [[1st half times], [second half times]]."""
	html_str_times = list(map(str, soup_times))#convert all bs4 tags to strings
	no_tag_times = list(map(de_tag, html_str_times)) #remove all tags from time stamps. 
	abs_times = list(map(abstime, no_tag_times))
	return split_halves(abs_times)

def split_halves(times, time_string='20:00'):
	"""Returns a 2-list list: [[1sthalf],[2ndhalf]] split by time_string (first occurrences go into first half). times must be a list of strings."""
	half1 = []
	half2 = []
	half2_index = 0
	for i in range(len(times)-1):
		half1.append(times[i])
		if times[i] == time_string and times[i+1] != time_string:
			half1.append(times[i])
			half2_index = i+1
			break
	for x in range(half2_index, len(times)-1):
		half2.append(times[x])
	return [half1, half2]

def plays_list(soup_plays):
	"""Returns a list of plays."""
	html_str_plays = list(map(str, soup_plays))
	no_tag_plays = list(map(de_tag, html_str_plays))
	return no_tag_plays

def scores_list(soup_scores):
	"""Return a list of scores."""
	html_str_scores = list(map(str, soup_scores))
	no_tag_scores = list(map(de_tag, html_str_scores))
	return no_tag_scores

def halves_list(rows_h1, rows_h2):
	"""Return a list of only two possible elements: '1st half' or '2nd half'"""
	halves = []
	for i in range(rows_h1):
		halves.append('1st half')
	for x in range(rows_h2):
		halves.append('2nd half')
	return halves

url = 'http://www.espn.com/mens-college-basketball/playbyplay?gameId=401082730'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser') #contains HTML of webpage

teams = teams_list(soup.title.string)
times = times_list(soup.find_all('td', class_='time-stamp'))
concat_times = times[0] + times[1]
num_rows = len(times)
plays = plays_list(soup.find_all('td', class_='game-details'))
scores = scores_list(soup.find_all('td', class_='combined-score'))
halves = halves_list(len(times[0]), len(times[1]))
game_table = DataFrame({'Half': halves, 'Time': concat_times, 'Team': teams, 'Play': plays, 'Score': scores})
names = team_names(soup.title.string)
file_name = names[0] + 'v' + names[1]+ 'boxscore.xlsx'
game_table.to_excel(file_name, 'sheet1', index=False)