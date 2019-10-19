# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    analize.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ibaran <ibaran@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2019/10/16 20:17:59 by ibaran            #+#    #+#              #
#    Updated: 2019/10/19 23:40:41 by ibaran           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import operator
import ipinfo
import socket
import itertools
import statistics as st
from time import sleep
from mpl_toolkits.basemap import Basemap


MAX_ERR = 5 # maximum amount of requests per session with non-success response
MAX_REQUESTS = 10 # maximum amount of requests per session with success response
MIN_DELTA = 3.0 # minimum average time spent on each page
SESSION_LENGTH = 1800 # length of session in seconds

good_bots_names = ["googlebot", "askjeeves", "digger", "lycos",
"msnbot", "inktomi, slurp", "yahoo", "nutch", "bingbot",
"bingpreview", "mediapartners-google", "proximic", "ahrefsbot",
"adsbot-google", "ezooms", "addthis.com", "facebookexternalhit",
"metauri", "feedfetcher-google", "paperlibot", "tweetmemebot",
"sogou web spider", "googleproducer", "rockmeltembedder",
"sharethisfetcher", "yandexbot", "rogerbot-crawler", "showyoubot",
"baiduspider", "sosospider", "exabot"]
# add botname that you trust to avoid blocking them (in lower case)
# for example 'dataprovider'

good_host_names = ["google", "askjeeves", "digger", "lycos",
"msn", "inktomi, slurp", "yahoo", "nutch", "bing",
"bingpreview", "proximic", "ahrefs","adsbot-google", "ezooms",
"addthis.com", "facebookexternalhit", "metauri",
"feedfetcher-google", "paperli", "tweetmeme", "sogou",
"rockmeltembedder", "sharethisfetcher", "yandex",
"rogerbot-crawler", "showyou", "baiduspider",
"sosospider", "exabot"]

# shape of dataframe used to hold access log information
data_form = pd.DataFrame(columns=['ip', 'hyphen', 'userid', 'date', 'method',
'destination', 'protocol', 'status', 'size', 'referer', 'agent',
'always_empty'])

# shape of dataframe used to hold error log information
#error_form = pd.DataFrame(columns=['date', 'ip', 'filename'])

#
# Getting the information from .log file and putting it
# into list of dictionaries
#
def log_reader(filename, mode):
	with open(filename) as f:
		log = f.read()
	if mode == 'access':
		r = re.compile(r'''(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
		\ (?P<hyphen>.+)\ (?P<userid>.+)\ \[(?P<date>.+)\]\ "(?P<method>.+)
		\ (?P<destination>.+)\ (?P<protocol>.+)"\ (?P<status>\d+)\ (?P<size>\d+)
		\ "(?P<referer>.+)"\ "(?P<agent>.+)"\ "(?P<always_empty>.+)"''', re.X)
	#elif mode == 'error':
	#	r = re.compile(r'\[(?P<date>.+)\] \[error\] \[client (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\] File does not exist: (?P<filename>.+)')
	return [all.groupdict() for all in r.finditer(log)]

#
# Function used to locate ip of request and build the map (not used yet)
#
def build_map(items):
	ips = {str() : [int(), int()]}
	for item in items:
		if item['ip'] in ips:
			ips[item['ip']][0] += 1
			if item['status'] != '200':
				ips[item['ip']][1] += 1
		else:
			ips[item['ip']] = [1, 0]
			if item['status'] != '200':
				ips[item['ip']][1] = 1

	#THIS IS USED TO LOCATE IPs
	data = pd.DataFrame(columns=['latitude', 'longitude', 'ip', 'num', 'err'])
	not_located = list()
	access_token = 'd172b1fedf7feb' # token used to get access to ipinfo tool
	for ip in ips:
		try:
			handler = ipinfo.getHandler(access_token)
		except:
			not_located.append(ip)
			continue		
		details = handler.getDetails(ip)
		location = details.loc.split(',')
		print(location)
		if location[0] or location[1]:
			data = data.append(pd.DataFrame({
				'latitude': [float(location[0])],
				'longitude': [float(location[1])],
				'ip': [ip],
				'num': [ips[ip][0]],
				'err': [ips[ip][1]]
			}), ignore_index = True)
		else:
			not_located.append(ip)
	data = data.sort_values(by='num', ascending=False)
	print(data)
	#print(not_located)
	max_req = max(data.num)
	print(data.latitude.min() - 3 , data.latitude.max() + 3)
	print(data.longitude.min() - 3 , data.longitude.max() + 3)
	m = Basemap(llcrnrlon = -160, llcrnrlat = -75, urcrnrlon = 160,
		urcrnrlat = 80)
	m.fillcontinents(color = 'grey', alpha = 0.2, lake_color = 'grey')
	m.drawcoastlines(linewidth = 0.1, color = "white")
	plt.scatter(data['longitude'], data['latitude'], c = 1 / data['num'],
		s = 100 * data['num'] * (1 / max_req), cmap = 'viridis', alpha = 1)
	plt.show()

	return True

#
# Function used to filter good bots from all trafic
#
def filter_bots(data):
	good = data[data['agent'].str.contains('(?i)'+'|'.join(good_bots_names))]
	bad = data[~data['agent'].str.contains('(?i)'+'|'.join(good_bots_names))]
	return [good, bad]

#
# Filter good bots by host using reverse DNS lookup
#
def filter_by_host(good_bots):
	bad_bots = data_form
	for i, row in good_bots.iterrows():
		try:
			socket.gethostbyaddr(row['ip'])[0]
		except:
			bad_bots = bad_bots.append(row)
			good_bots = good_bots[good_bots['ip'] != row['ip']]
			continue
		bad = True
		for good_host_name in good_host_names:
			if good_host_name in socket.gethostbyaddr(row['ip'])[0].lower():
				bad = False
				break
		if bad:
			bad_bots = bad_bots.append(row)
			good_bots = good_bots[good_bots['ip'] != row['ip']]
	return [good_bots, bad_bots]

#
# Evaluate ip reputation depending on frquency of requests,
# time spent on each page and amount of error responses
#
def analyze_sessions(sessions, ip, status, details):
	access_token = 'd172b1fedf7feb'
	for session in sessions:
		if status == '200':
			if len(session) > MAX_REQUESTS:
				return False
		else:
			if len(session) > MAX_ERR:
				return False
		if st.mean(session) < MIN_DELTA:
			return False
		if details['destination'].str.contains('administrator', regex=False).any():
			handler = ipinfo.getHandler(access_token)
			details = handler.getDetails(ip)
			if details.country != 'AT':
				return False
	return True

#
# Function used to divide timedeltas into sessions
#
def divide_in_sessions(freq):
	return [list(y) for x, y in itertools.groupby(freq,
	lambda z: z >= SESSION_LENGTH) if not x]

#
# Function used to filter remaining trafic by the the frequency of requests
#
def filter_by_frequency(not_good_bots):
	bad_bots = data_form
	new = data.groupby('ip')
	for ip, group in new:
		if bad_bots['ip'].str.contains(ip).any():
			continue
		freq = list()
		gr_by_status = group.groupby('status')
		for status, inner_group in gr_by_status:
			prev_time = 0
			for i, row in inner_group.iterrows():
				if prev_time != 0:
					freq.append(int((row['date'] - prev_time).total_seconds()))
				prev_time = row['date']
			freq_in_sessions = divide_in_sessions(freq)
			# if ip == '106.38.241.181':
			# 	print(freq_in_sessions)
			if analyze_sessions(freq_in_sessions, ip, status, inner_group) == False:
				bad_bots = bad_bots.append(not_good_bots[not_good_bots['ip'] == ip])
				not_good_bots = not_good_bots[not_good_bots['ip'] != ip]
	return [not_good_bots, bad_bots]

if __name__ == '__main__':
	# redaing log file into dataframe
	# http://www.almhuette-raith.at/apache-log/access.log
	data = pd.DataFrame(log_reader("medium.log", "access"))
	# converting strings date to datetime type
	data['date'] = pd.to_datetime(data['date'], format='%d/%b/%Y:%H:%M:%S %z')

	#error = pd.DataFrame(log_reader("error.log", "error"))
	# http://www.almhuette-raith.at/apache-log/error.log

	# divide requests that have good bot name in agent field
	# (does't definitely mean it's a good bot)
	# and that don't have good bot name in agent field
	filtered = filter_bots(data)
	good_bots = filtered[0]
	not_good_bots = filtered[1]
	
	# filter good bots by the fact request is made
	# from ip hosted by trusted host or not
	filtered = filter_by_host(good_bots)
	good_bots = filtered[0] # FILNAL GOOD BOTS TRAFIC
	bad_bots = filtered[1] # NOT FINAL BAD BOTS TRAFIC
	
	# filter remaining trafic by the the frequency rules
	filtered = filter_by_frequency(not_good_bots)
	humans = filtered[0] # FINAL HUMAN TRAFIC
	bad_bots = bad_bots.append(filtered[1]) # FILNAL BAD BOTS TRAFIC

	## DEBUG
	print("TOTAL IPs:")
	data = data.groupby(['ip'])
	print(len(data))
	print("\nHUMANS:")
	humans = humans.groupby(['ip'])['destination'].apply(list).reset_index(name='destinations') #FINAL HUMAN TRAFIC
	for i, h in humans.iterrows():
		print(h['ip'])
	print("\nBAD BOTS:")
	bad_bots = bad_bots.groupby(['ip'])['destination'].apply(list).reset_index(name='destinations') #FINAL HUMAN TRAFIC
	for i, h in bad_bots.iterrows():
		print(h['ip'])
	print("\nGOOD BOTS:")
	good_bots = good_bots.groupby(['ip'])['destination'].apply(list).reset_index(name='destinations')
	for i, h in good_bots.iterrows():
		print(h['ip'])
	## END DEBUG
	exit(0)
	#print(count_requests_per_ip(not_good_bots))
	if build_map(bad_bots) == False:
		print("Can't locate ips")


# Frequency rules
# - general amount of requests
# - timedeltas between moving to another page
# - percentage of not-succeess responses
