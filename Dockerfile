# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Dockerfile                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ibaran <ibaran@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2019/10/21 18:40:57 by ibaran            #+#    #+#              #
#    Updated: 2019/10/22 00:25:07 by ibaran           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

FROM		debian
ENV 		LOG_FILENAME=""

WORKDIR		/usr/src/app
RUN			apt-get -y update && apt-get -y upgrade && \
			apt-get -y install python3-pip libgeos-dev git
RUN			pip3 --version
RUN			pip3 install pandas matplotlib ipinfo ip2geotools \
			pyinotify
RUN			pip3 install -U git+https://github.com/matplotlib/basemap.git

CMD			[ "python3", "analize.py" ]

# to build the image run:
# docker image build -t bot_detection:1.0 . 
# to run the container run:
# docker run -it --mount type=bind,source="$(pwd)",target=/usr/src/app \
# bot_detection:1.0

# You can set the name of the file that is supposed to be analyzed
# by assigning the environment variable LOG_FILENAME:
# docker run -it --mount type=bind,source="$(pwd)",target=/usr/src/app \
# -e LOG_FILENAME='filename' bot_detection:1.0
