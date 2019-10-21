# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    analize.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ibaran <ibaran@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2019/10/16 15:17:59 by ibaran            #+#    #+#              #
#    Updated: 2019/10/21 19:14:56 by ibaran           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import re
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import operator
import ipinfo
import socket
import itertools
import statistics as st
import matplotlib.patches as mpatches
from mpl_toolkits.basemap import Basemap

#	Algorithm:
#	1. reading a log file into a data frame from a copy of
#		http://www.almhuette-raith.at/apache-log/access.log
#	2. converting date strings to DateTime type
#	3. dividing requests depending on if they have 
#		good bot name in agent field (doesn't definitely mean
#		it's a good bot) or not
#	4. check the list of good bots depending on if
#		the request is made from an IP hosted by a trusted host or not
#	5. filter the traffic which is not created by good bots
#		depending on the following rules:
#			- the general amount of requests (ignoring requests made
#				by a page to get its sources)
#			- time deltas between moving to another page
#			- percentage of not-success responses
#			- the volume of traffic coming from an unexpected location

# TODO
# Manage single requests
# Remove double IPs if header changes
# to black:
# 51.15.109.127

MAX_ERR = 5 # maximum amount of requests per session with a non-success response
MAX_REQUESTS = 10 # maximum amount of requests per session with success response
MIN_DELTA = 3.0 # minimum average time spent on each page
SESSION_LENGTH = 1800 # length of a session in seconds
MAX_SAME_ORIGIN = 3 # maximum of IPs of the same subnet

DATE_FORMAT = '%d/%b/%Y:%H:%M:%S %z'

# add botname that you trust to avoid blocking them (in lower case)
# for example 'dataprovider'
good_bots_names = ["googlebot", "askjeeves", "digger", "lycos",
	"msnbot", "inktomi, slurp", "yahoo", "nutch", "bingbot",
	"bingpreview", "mediapartners-google", "proximic", "ahrefsbot",
	"adsbot-google", "ezooms", "addthis.com", "facebookexternalhit",
	"metauri", "feedfetcher-google", "paperlibot", "tweetmemebot",
	"sogou web spider", "googleproducer", "rockmeltembedder",
	"sharethisfetcher", "yandexbot", "rogerbot-crawler", "showyoubot",
	"baiduspider", "sosospider", "exabot"]

good_host_names = [
	"google", "askjeeves", "digger", "lycos",
	"msn", "inktomi, slurp", "yahoo", "nutch", "bing",
	"bingpreview", "proximic", "ahrefs","adsbot-google", "ezooms",
	"addthis.com", "facebookexternalhit", "metauri",
	"feedfetcher-google", "paperli", "tweetmeme", "sogou",
	"rockmeltembedder", "sharethisfetcher", "yandex",
	"rogerbot-crawler", "showyou", "baiduspider",
	"sosospider", "exabot"
	]

# add bad referrers addresses to add them to bad bots list 
bad_referers = [
	'site.ru'
	]

# shape of the data frame used to hold access log information
data_form = pd.DataFrame(columns=[
	'ip', 'hyphen', 'userid', 'date',
	'method', 'destination', 'protocol', 'status',
	'size', 'referer', 'agent', 'always_empty',
	'explain'
	])

# Getting the information from a .log file and putting it
# into a list of dictionaries which will be later converted
# into a pandas data frame
def log_reader(filename, mode):
	print("Reading source file")
	with open(filename) as f:
		log = f.read()
	r = re.compile(r'''(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
		\ (?P<hyphen>.+)\ (?P<userid>.+)\ \[(?P<date>.+)\]\ "(?P<method>.+)
		\ (?P<destination>.+)\ (?P<protocol>.+)"\ (?P<status>\d+)\ (?P<size>\d+)
		\ "(?P<referer>.+)"\ "(?P<agent>.+)"\ "(?P<always_empty>.+)"''', re.X)
	return [all.groupdict() for all in r.finditer(log)]

# Locating IP addresses
def fill_location_data(grouped, color):
	data = pd.DataFrame(columns=['latitude', 'longitude', 'size', 'color'])
	not_located = list()
	access_token = 'd172b1fedf7feb' # token used to get access to ipinfo tool
	handler = ipinfo.getHandler(access_token)
	for ip, group in grouped:
		try:
			details = handler.getDetails(ip)
		except:
			not_located.append(ip)
			continue
		location = details.loc.split(',')
		if location[0] or location[1]:
			data = data.append(pd.DataFrame({
				'latitude': [float(location[0])],
				'longitude': [float(location[1])],
				'size': group.shape[0],
				'color': color
				}), ignore_index=True)
		else:
			not_located.append(ip)
	return [data, not_located]

# Function used to locate the IP of requests and build the map
def build_map(bad_bots, good_bots, human_req):
	print("Building a map of IP groups")
	data = pd.DataFrame(columns=['latitude', 'longitude', 'size', 'color'])

	bad = fill_location_data(bad_bots, 'red')
	good = fill_location_data(good_bots, 'orange')
	humans = fill_location_data(human_req, 'green')
	
	data = data.append(bad[0], ignore_index=True)
	data = data.append(good[0], ignore_index=True)
	data = data.append(humans[0], ignore_index=True)
	
	if len(bad[1] + good[1] + humans[1]) != 0:
		print("Couldn't locate", len(bad[1] + good[1] + humans[1]), "IPs")

	plt.subplots(figsize=(20,10))
	m = Basemap(llcrnrlon=-160, llcrnrlat=-75, urcrnrlon=160,
				urcrnrlat=80, resolution='c')
	m.fillcontinents(color='grey', alpha=0.2, lake_color='grey')
	m.drawcoastlines(linewidth=0.1, color="white")
	m.drawcountries(color='white')

	plt.scatter(data.longitude, data.latitude, c=data.color,
				s=25, alpha=0.8)
					
	green_patch = mpatches.Patch(color='green', label='Humans')
	orange_patch = mpatches.Patch(color='orange', label='Good bots')
	red_patch = mpatches.Patch(color='red', label='Bad bots')
	plt.legend(handles=[green_patch, orange_patch, red_patch])
	
	plt.savefig('map.png', bbox_inches='tight')
	print("The map was saved to file 'map.png'")

# Function used to filter the traffic by header depending on
# if there is a good bot name or not
def filter_by_header(data):
	print("Filtering data by header")
	good = data[data['agent'].str.contains('(?i)' + '|'.join(good_bots_names))]
	bad = data[~data['agent'].str.contains('(?i)' + '|'.join(good_bots_names))]
	return [good, bad]

# Filter good bots depending on if the IP address originates
# from a trusted host using reverse DNS lookup
def filter_by_host(good_bots):
	print("Filtering data by host")
	bad_bots = data_form
	for i, row in good_bots.iterrows():
		try:
			socket.gethostbyaddr(row['ip'])[0]
		except:
			bad_bots = bad_bots.append(good_bots[good_bots['ip'] == row['ip']])
			good_bots = good_bots[good_bots['ip'] != row['ip']]
			bad_bots.loc[bad_bots.ip == row['ip'], 'explain'] = 'HOST_NOT_MATCH'
			continue
		bad = True
		for good_host_name in good_host_names:
			if good_host_name in socket.gethostbyaddr(row['ip'])[0].lower():
				bad = False
				break
		if bad:
			bad_bots = bad_bots.append(good_bots[good_bots['ip'] == row['ip']])
			good_bots = good_bots[good_bots['ip'] != row['ip']]
			bad_bots.loc[bad_bots.ip == row['ip'], 'explain'] = 'HOST_NOT_MATCH'
	return [good_bots, bad_bots]

# Function used to divide time deltas into sessions
def divide_in_sessions(freq):
	return 

# Evaluate IP reputation depending on the frequency of requests,
# time spent on each page, amount of error responses,
# referrer, visited files, and the location if
# the administrator page is a destination
def analyze_sessions(sessions, ip, status, details):
	access_token = 'd172b1fedf7feb'
	if details['destination'].str.contains('robots.txt', regex=False).any():
		return 'ROBOTS_TXT'
	if details['referer'].str.contains('(?i)'+'|'.join(bad_referers)).any():
		return 'BAD_REFERER'
	if details['destination'].str.contains('administrator', regex=False).any():
		handler = ipinfo.getHandler(access_token)
		details = handler.getDetails(ip)
		if details.timezone.find('Europe') == -1: return 'ADMIN_BAD_ORIGIN'
	for session in sessions:
		if status == '200':
			if len(session) > MAX_REQUESTS: return 'MAX_REQUESTS'
		else:
			if len(session) > MAX_ERR: return 'MAX_ERR'
		if st.mean(session) < MIN_DELTA: return 'MIN_DELTA'
	return 'OK'

# Function used to filter traffic by the frequency of requests
def filter_by_frequency(not_good_bots):
	print("Filtering data by sessions behaviour")
	bad_bots = data_form
	new = data.groupby('ip')
	for ip, group in new:
		if bad_bots['ip'].str.contains(ip).any():
			continue
		gr_by_status = group.groupby('status')
		for status, inner_group in gr_by_status:
			details = (inner_group[~inner_group['referer'].str
						.contains('almhuette-raith.at')])
			details = (details[~details['destination'].str
						.contains('favicon.ico')])
			freq = list()
			prev_time = 0
			for i, row in details.iterrows():
				if prev_time != 0:
					freq.append(int((row['date'] - prev_time).total_seconds()))
				prev_time = row['date']
			freq_in_sessions = [
				list(y) for x, y in itertools.groupby(freq,
				lambda z: z >= SESSION_LENGTH) if not x
				]
			res = analyze_sessions(freq_in_sessions, ip, status, details)
			if res != 'OK':
				to_append = not_good_bots[not_good_bots['ip'] == ip]
				to_append = to_append.assign(explain=res)
				bad_bots = bad_bots.append(to_append)
				not_good_bots = not_good_bots[not_good_bots['ip'] != ip]
	return [not_good_bots, bad_bots]

# Function used to filter traffic depending on
# if it comes from a similar and unexpected origin
def filter_by_origin(not_good_bots):
	print("Filtering data by origin")
	bad_bots = data_form
	same_origins = data_form
	for i, row in not_good_bots.iterrows():
		splt = row['ip'].split('.')[0:3]
		origin = '.'.join(splt)
		to_find_in = not_good_bots[not_good_bots.ip != row['ip']]
		if to_find_in['ip'].str.contains( origin ).any():
			same_origins = same_origins.append(row)
	for i, same_origin in same_origins.iterrows():
		splt = same_origin['ip'].split('.')[0:3]
		origin = '.'.join(splt)
		origins = same_origins[same_origins['ip'].str.contains(origin)]
		if origins['ip'].count() > MAX_SAME_ORIGIN \
		and not bad_bots['ip'].str.contains(origin).any():
			origins = origins.assign(explain = 'UNTRUSTED_ORIGIN')
			bad_bots = bad_bots.append(origins)
			not_good_bots = not_good_bots[~not_good_bots['ip']
											.str.contains(origin)]
	return [not_good_bots, bad_bots]

# Function used to output the result to a file
def output_to_file(data, bad_bots, good_bots, humans):
	print("Writing data to file 'result.txt'")
	data = data.groupby(['ip'])
	f = open("result.txt", "w+")
	f.write("Total amount of IPs analyzed: " + str(len(data)) + "\n\n")
	f.write("IPs trafic of which is concidered as human-like:\n")
	for ip, group in humans:
		f.write(ip + "\n")
	f.write("\nIPs trafic of which is concidered as bad-bots-like:\n")
	for ip, group in bad_bots:
		f.write(ip.ljust(20) + str(group['explain'].iloc[0]) + "\n")
	f.write("\nIPs trafic of which is concidered as good-bots-like:\n")
	for ip, group in good_bots:
		f.write(ip + "\n")
	f.close()

if __name__ == '__main__':
	data = data_form
	data = data.append(pd.DataFrame(log_reader("short.log", "access")),
						sort=False)
	data['date'] = pd.to_datetime(data['date'], format=DATE_FORMAT)

	filtered = filter_by_header(data)
	good_bots = filtered[0]
	not_good_bots = filtered[1]

	filtered = filter_by_host(good_bots)
	good_bots = filtered[0]						# FILNAL GOOD BOTS TRAFIC
	bad_bots = filtered[1]

	filtered = filter_by_frequency(not_good_bots)
	not_good_bots = filtered[0]
	bad_bots = bad_bots.append(filtered[1])

	filtered = filter_by_origin(not_good_bots)
	humans = filtered[0]						# FILNAL HUMAN TRAFIC
	bad_bots = bad_bots.append(filtered[1])		# FILNAL BAD BOTS TRAFIC

	bad_bots = bad_bots.groupby(['ip'])
	good_bots = good_bots.groupby(['ip'])
	humans = humans.groupby(['ip'])

	output_to_file(data, bad_bots, good_bots, humans)
	build_map(bad_bots, good_bots, humans)