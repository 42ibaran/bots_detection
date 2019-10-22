# Bot detection script

## About
This program is created to analyze apache web-server log and detect bot traffic in it. All data is divided into 3 groups: humans, good bots and bad bots. After the execution of the program, the result.txt file is created. After creating the output file with a list of IP addresses, all IPs are located and a map is built to visualize the obtained data.

## Setup
From the directory run:
```
docker image build -t bot_detection:1.0 . && docker run -it --mount type=bind,source="$(pwd)",target=/usr/src/app bot_detection:1.0
```
If you want to specify the filename that has to be analyzed, set the environment variable:
```
docker run -it --mount type=bind,source="$(pwd)",target=/usr/src/app -e LOG_FILENAME='filename' bot_detection:1.0
```

## short.log
This file contains the last 10000 lines from the original access.log file that can be reached at http://www.almhuette-raith.at/apache-log/access.log. To get the original file run:
```
wget http://www.almhuette-raith.at/apache-log/access.log
```
To save last lines into short.log file run:
```
tail -n <number> access.log > short.log
```

## result.txt
This file contains a list of analyzed IP addresses grouped by the origin of the traffic. For the traffic that is determined as bad-bots-like the reason of the desition is mentioned:

1. ADMIN_BAD_ORIGIN: the user tried to connect to the administrator page from an IP that is not located in Europe (as the website is located in Austria)

2. ROBOT_TXT: the user requested to get the file robots.txt but the http-header either doesn't mention that the request is made by a bot or the bot name is not trusted

3. BAD_REFERER: referrer of the request is in the black-list

4. MIN_DELTA: an average gap between the user's request is too short

5. UNTRUSTED_ORIGIN: the user's requests are made from the IP group that was used by bad bots

6. HOST_NOT_MATCH: http-header of the request contains a name of a trusted bot but the IP address doesn't match with the list of trusted hosts

7. SHORT_SESSIONS: the user lands on the website rarely and leaves shortly after

## Algorithm explanation:

1. Reading a log file into a data frame from a copy of http://www.almhuette-raith.at/apache-log/access.log

2. Dividing requests depending on if they have good bot name in agent field (doesn't definitely mean it's a good bot) or not

3. Checking the list of good bots depending on if the request is made from an IP hosted by a trusted host or not

4. Filter the traffic which is not created by good bots depending on the following rules:

	- length and frequency of sessions
	- web referrer
	- time deltas between moving to other pages
	- the volume of traffic coming from an untrusted origin
	- relations between visited pages and the origin of requests
	- visited files

5. Grouping all traffic by IP addresses and building the map
