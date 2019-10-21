# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Dockerfile                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ibaran <ibaran@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2019/10/21 18:40:57 by ibaran            #+#    #+#              #
#    Updated: 2019/10/21 21:54:38 by ibaran           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

FROM		debian

WORKDIR		/usr/src/app
RUN			apt-get -y update && apt-get -y upgrade && \
			apt-get -y install python3-pip libgeos-dev git \
			tcl-dev tk-dev python-tk python3-tk
RUN			pip3 --version
RUN			pip3 install pandas matplotlib ipinfo ip2geotools \
			pyinotify
RUN			pip3 install -U git+https://github.com/matplotlib/basemap.git

#CMD			[ "python3", "analize.py" ]

# from the directory run:
# docker image build -t bot_detection:1.0 . && docker container run -it \
# --mount type=bind,source="$(pwd)",target=/usr/src/app \ bot_detection:1.0
