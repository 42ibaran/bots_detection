# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    watch.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ibaran <ibaran@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2019/10/21 21:46:47 by ibaran            #+#    #+#              #
#    Updated: 2019/10/21 21:47:49 by ibaran           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import webbrowser
import pyinotify

class ModHandler(pyinotify.ProcessEvent):
	# evt has useful properties, including pathname
	def process_IN_CLOSE_WRITE(self, evt):
		webbrowser.open('http://www.almhuette-raith.at/apache-log/access.log')

handler = ModHandler()
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch('watch.log', pyinotify.IN_CLOSE_WRITE)
notifier.loop()
