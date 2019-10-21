# Bot detection script

## About
This program is created to analyze apache web-server log and detect bot traffic in it. All data is divided into 3 groups: humans, good bots and bad bots. After execution of the program file result.txt is created. After creating an output file with a list of IP addresses, all IPs are located and a map is built to visualize the obtained data.

## Setup
from the directory run:
```
docker image build -t bot_detection:1.0 . && docker container run -it --mount type=bind,source="$(pwd)",target=/usr/src/app \ bot_detection:1.0
```

## short.log
This file contains the last 5000 lines from the original access.log file that can be reached at http://www.almhuette-raith.at/apache-log/access.log. To get the original file run:
```
wget http://www.almhuette-raith.at/apache-log/access.log
```
To save last n lines into short.log file run:
```
tail -n <n> access.log > short.log
```

## result.txt
This file contains a list of analyzed IP addresses grouped by the origin of the traffic. For the traffic the is determined as bad-bots-like the reason of  the desition is mentioned:

1. ADMIN_BAD_OROGIN: the user tried to connect to the administrator page from an IP that is not located in Europe (as the website is located in Austria)

2. ROBOT_TXT: the user requested to get the file robots.txt but the http-header either doesn't mention that the request is made by a bot or the bot name is not trusted

3. BAD_REFERER: referrer of the request is in the black-list

4. MAX_REQUESTS: the user made to many requests in one session

5. MAX_ERR: the user's requests led to too many not-success responses

6. MIN_DELTA: an average gap between the user's request is too small

7. UNTRUSTED_ORIGIN: the user's requests are made from the IP group, the sum of requests from which is suspiciously large

8. HOST_NOT_MATCH: http-header of the request contains a name of a trusted bot but the IP address doesn't match with the list of trusted bot hosts

## Algorithm explanation:

1. Reading a log file into a data frame from a copy of http://www.almhuette-raith.at/apache-log/access.log

2. Converting date strings to DateTime type

3. Dividing requests depending on if they have good bot name in agent field (doesn't definitely mean it's a good bot) or not

4. Checking the list of good bots depending on if the request is made from an IP hosted by a trusted host or not

5. Filter the traffic which is not created by good bots depending on the following rules:

    - the general amount of requests (ignoring requests made by a page to get its sources)
    - time deltas between moving to another page
    - percentage of not-success responses
    - the volume of traffic coming from an unexpected location

6. Grouping all traffic by IP addresses and building the map
