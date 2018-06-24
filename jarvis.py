#!/usr/bin/env python




import os, sys, subprocess, _thread, queue
import time, readline, re

from flask import Flask, render_template
from flask_socketio import Namespace, SocketIO, send, emit
from flask_classful import FlaskView

from sqlobject import *

sqlhub.processConnection = connectionForURI('sqlite:/:memory:')

######################################################################################################### 
# 
# Tools
# 
#########################################################################################################   
def word_count(value):
    # Find all non-whitespace patterns.
    list = re.findall("(\S+)", value)
    # Return length of resulting list.
    return len(list)

def run_process(command):
	result=""
	
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	while process.poll() is None:
		output = process.stdout.readline().decode("utf-8")
		if word_count(output) >= 1 : result = result+output
	
	return(result)

def speak(speech):
	os.system("espeak -w /home/boejaker/bin/JARVIS/test.wav "+speech)
	return("/home/boejaker/bin/JARVIS/test.wav")


######################################################################################################### 
# 
# Home Network Super Class
# 
#########################################################################################################  
class homeNetwork(object):
	"""docstring for ClassName"""
	import socket
	import notify2
	notify2.init("JARVIS", mainloop=None)

	def __init__(self):
		self.localip = run_process("/home/boejaker/bin/JARVIS/castTools.sh ip")
		self.now_listening = now_listening_db.createTable()
		self.now_watching = now_watching_db.createTable()
		self.now_casting = cast_db.createTable()
		self.ip_objects = ip_object_db.createTable()
		self.user = user_db.createTable()
		self.activity = user_activity_db.createTable()

	def build(self):
		# Chromecast.build()
		self.spotify = Spotify()
		time.sleep(5)
		if self.spotify.update() is True:
			_thread.start_new_thread( self.spotify.deamon, ())
				
	@classmethod
	def get_ip(self):
		s = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		x = s.getsockname()[0]
		s.close()
		return(x)
	
	@classmethod
	def notification(self, title, message):
	    notice = self.notify2.Notification(str(title), str(message), "/home/boejaker/bin/spotify/coverart.jpeg")
	    notice.show()
	    return

	def automate(self):
		ipObject.map_ip()
		if self.spotify.update() is True:
			request_spotify_data("none")
			# if watching something, pause music if paying
		

######################################################################################################### 
# 
# IP Address Object
# 
#########################################################################################################  
class ipObject(homeNetwork):
	"""Stores, maintains and updates ip data as a seperate object"""
	netMap = ""
	ipo = {} # Lists all IP objects, keyed by mac address
	address = {} # Lists all IP object values, keyed by mac address


	def __init__(self, name, ip, mac, service):
		self.name = name
		self.ip = ip
		self.mac = mac
		self.service = service
		self.address[mac] = (name, ip, service)
		# start ip checking deamon

	@classmethod
	def register(self, name, ip, mac, service):
		self.ipo[mac] = self(name, ip, mac, service)
		return self.ipo[mac] 

	@classmethod
	def update_ip(self):
		for item in self.ipo.items():
			item[1].ip = run_process("/home/boejaker/bin/JARVIS/castTools.sh macip "+item[1].mac)
	
	@classmethod
	def map_ip(self):
		for ip in run_process("/home/boejaker/bin/JARVIS/castTools.sh ipscan").splitlines():
			trig = 0
			for item in self.ipo.items():
				if item[1].ip.rstrip() is ip.rstrip():
					trig = 1
			if trig == 0:
				mac = run_process("python /home/boejaker/bin/JARVIS/netstat.py "+ip).rstrip()
				self.register("unknown", ip, mac, "uknown")
		return(self.address)


######################################################################################################### 
# 
# Webserver Initialization
# 
#########################################################################################################  

def init_webserver(lan):
	# Dependancy check
	# Initialization
	global app, socketio
	app = Flask(__name__)
	socketio = SocketIO(app)
	_thread.start_new_thread( socketio.run, ( app, ),{'host':'0.0.0.0',} )

def init_ftp(lan):
	pass

def init_redirect(lan):
	pass

######################################################################################################### 
# 
# System Backup Tools
# 
#########################################################################################################  

class Backup(object):

	def __init__(self):
		self.updatePip
		self.updateApt

	def updatePip(self):
		os.system('pip3 --list | awk \'{print $1}\' > ./pipRestore.py')

	def updateApt(self):
		os.system('dpkg --get-selections > ./aptRestore.txt')

	def updateFiles(self):
		pass

	def restoreSys(self):
		os.system('dpkg --clear-selections ; sudo dpkg --set-selections < ./aptRestore.txt')
		os.system('x=\"$(cat ./pipRestore.py)\" ; for i in $x ; do sudo -H pip3 install \"$i\" ; done')

	def restoreFiles(self):
		pass

######################################################################################################### 
# 
# Spotify Superclass
# 
#########################################################################################################                 
class Spotify(homeNetwork):
	from colorthief import ColorThief
	import spotipy
	import spotipy.util as util
	import _pickle as cPickle
	import traceback

	updateFreq = 10

	def __init__(self):
		
		print("")
		print("Building Spotify client instance")

		self.username = "boejaker80"
		# self.ip = self.get_ip()
		self.port = "8888" # HTTP listener port for auth response
		
		token = self.util.prompt_for_user_token(self.username, scope = None, client_id = '72b81794a7fd44d99970fe3fb1abe7b1', client_secret = '57fdd417301e4a9389b0a67b1ab6ea77')
		self.client = self.spotipy.Spotify(auth=token)
		
		self.features = ["wallpaper_switcher", "notification", "playlist_trigger"]
		self.plTriggers = ["Deep", "Hype", "Chill", "Summer", "Work"]
		self.sTriggers = ["", ""]
		
		self.sl = song.sl
		# self.pl = playlist.build(self.client)
		self.np = {"now":song(None, self.client, None, None),"last":song(None, self.client, None, None)}
		self.que = queue.Queue(maxsize=1)
		self.state = queue.Queue(maxsize=1)
		
		print("Spotify client instance build complete")
		print("")

	def update(self):
		if self.now_playing() is not None:
			if "wallpaper_switcher" in self.features:
					self.coverart_wallpaper_switcher(self.np['now'])
			if self.que.full() is False:
				self.np['now'].color = self.getcolor(1)
				self.que.put(self.np['now'], False, 1)
			# self.progress =  self.np.track_info['progress_ms']
			# self.remianing = progress-self.np['now'].duration
			# print(self.remianing)
			return(True)	
		return(False)
	
	
	def now_playing(self):
		self.np['last'] = self.np['now']
		try:
			self.np['now'] = song.register(self.client, self.client.current_user_playing_track()['item']['id'])
		except:
			self.np['now'] = None
			self.user_active = False
			return(None)
		try:
			if self.np['now'].id == self.np['last'].id:
				return(None)
		except:
			pass
		self.np['now'].progress = self.client.current_user_playing_track()['progress_ms']
		return(self.np['now'])

	def display_now_playing(self):
		print("Now playing " + self.np['now'].name + " by " + str(self.np['now'].artists))
		plists = [x for x in playlist.cross_check(self.np['now'].id)]
		if plists:
			print("Playlists :")
			print(plists)
		else:
			print("This track does not feature in any playlists")

	def coverart_wallpaper_switcher(self, song):
		artUrl = song.artUrl
		os.system("wget -qO /home/boejaker/bin/spotify/coverart.jpeg "+artUrl)
		time.sleep(0.4)
		os.system("gsettings set org.gnome.desktop.background picture-uri file:///home/coverart.jpeg")
		time.sleep(0.1)
		os.system("gsettings set org.gnome.desktop.background picture-uri file:///home/boejaker/bin/spotify/coverart.jpeg")

	def song_trigger_action(self, song):
		return([ x for x in self.sTriggers if x.name == song.name ])

	def playlist_trigger_action(self, song):
		plcc = playlist.cross_check(song.id)
		return([ x for x in plcc for y in self.plTriggers if x == y ])

	def deamon(self):
		exit = False
		while exit == False:
			if self.update() is not False:
				self.display_now_playing()
				if "notification" in self.features:
					self.notification(self.np['now'].name, self.np['now'].artists)
				if "playlist_trigger" in self.features:
					self.playlist_trigger_action(self.np['now'])
				if "song_trigger" in self.features:
					self.song_trigger_action(self.np['now'])
			time.sleep(self.updateFreq)
	
	def mood_analysis(self):
		# valance
		# playlist
		pass
	
	def progress(self):
		self.np['now'].duration

	def db_write(self):
		pass

	def db_read(self):
		pass

	def save(self):
		"""save class as self.name.txt"""
		file = open('spotify.txt','wb')
		file.write(self.cPickle.dumps(self.__dict__))
		file.close()

	def load(self):
		"""try load self.name.txt"""
		file = open('spotify.txt','rb')
		dataPickle = file.read()
		file.close()
		return(self.cPickle.loads(dataPickle))

	@classmethod
	def getcolor(self, quality):
		color_thief = self.ColorThief('/home/boejaker/bin/spotify/coverart.jpeg')
		# get the dominant color
		dominant_color = '#%02x%02x%02x' % color_thief.get_color(quality=quality)
		return(dominant_color)

######################################################################################################### 
# 
# Song Object
# 
#########################################################################################################                 
class song(Spotify):

	# Object endpoint lists  
	sl = {}
	
	def __init__(self, data, client, idNo, updated):
		super()
		self.track_info = data
		self.client = client
		self.id = idNo
		if data is not None:
			self.name = self.track_info['name']
			self.artists = [artist['name'] for artist in self.track_info['album']['artists']]
			self.album = self.track_info['album']['name']
			self.artUrl = self.track_info['album']['images'][0]['url']
			self.popularity = self.track_info['popularity']
			self.duration = self.track_info['duration_ms']
			self.updated = updated
			self.progress = None
			self.features = ""
			self.analysis = ""
			self.save()


	@classmethod
	def register(self, client, idNo):
		try:
			obj = self.load(idNo)
			self.sl[idNo] = song(obj['track_info'], client, obj['id'], obj['updated'])
			
			if self.time.time()-self.sl[idNo].updated >= 900000: 
				data = client.track("spotify:track:"+idNo)
				# del self.sl[idNo]
				self.sl[idNo] = song(data, client, idNo, self.time.time())
				print("Updating "+self.sl[idNo].name+" by "+str(self.sl[idNo].artists))
			else:
				pass
				# print("Unpickling "+self.sl[idNo].name+" by "+str(self.sl[idNo].artists))

		except:
			for item in self.sl.items():
				if item[1].id == idNo:
					break
			else:
				try:
					data = client.track("spotify:track:"+idNo)
				except:
					pass

				self.sl[idNo] = song(data, client, idNo, time.time())
				print("New track "+self.sl[idNo].name+" by "+str(self.sl[idNo].artists))

		return(self.sl[idNo])

	def display(self, v=False):
		if v:
			print("%22s %40.60s %s" % (self.id, self.name, self.artists))
			print("%22s %40.60s" % ("Popularity: "+str(self.popularity), "Duration: "+str(self.duration)))
			print("%60.60s %s" % (self.artUrl, self.album))
			print()

		else:
			print("%22s %40.70s %s" % (self.id, self.name, self.artists))

	@classmethod
	def display_all(self, v=False):
		return([ i[1].display(v=v) for i in self.sl.items()])

	def crosscheck(self):
		return(playlist.cross_check(self.id))
	
	def features(self):
		pass

	def analyze(self):
		pass

	def save(self):
		"""save class as self.name.txt"""
		file = open("/home/boejaker/bin/spotify/data/tracks/"+self.id+'.txt','wb')
		file.write(self.cPickle.dumps(self.__dict__))
		file.close()

	@classmethod
	def load(self, name):
		"""try load self.name.txt"""
		file = open("/home/boejaker/bin/spotify/data/tracks/"+name+'.txt','rb')
		dataPickle = file.read()
		file.close()
		return(self.cPickle.loads(dataPickle))

######################################################################################################### 
# 
# Playlist Object
# 
#########################################################################################################                 
class playlist(Spotify):

	pl = {}
	username = "boejakerjaker80"

	def __init__(self, data, client, updated):
		self.data = data
		self.client = client
		self.name = self.data['name']
		self.owner = self.data['owner']
		self.id = self.data['id']
		self.tracks = self.client.user_playlist_tracks(self.username, self.id)
		self.trackNo = self.data['tracks']['total']
		self.updated = updated
		self.to = {}

		self.register_tracks(self.id)
		self.save()

	@classmethod
	def build(self, client): 
		print("Checking for playlist updates")
		playlists = client.user_playlists(self.username)
		for plist in playlists['items']:
			if plist['owner']['id'] == self.username and plist['name'] != "Rihanna - Stay 20syl. Remix" :
				upd = time.time()
				
				try: 	
					obj = self.load(plist['name'])
					if time.time()-obj['updated'] <= 10:
						upd = obj['updated']
						plist = obj['data']
						print("Updating "+plist['name'])	
					else:
						print("Unpickling "+plist['name'])	
				except:
					print("New playlist "+plist['name'])
		
				
				self.pl[plist['name']] = playlist(plist, client, upd)				

	
		return(self.pl)

	def register_tracks(self, playlistIdNo):
		results = self.client.user_playlist_tracks(self.username, playlistIdNo)
		tracks = results['items']

		# Loops to ensure I get every track of the playlist
		while results['next']:
			results = self.client.next(results)
			tracks.extend(results['items'])

		for item in tracks:
			self.to[item['track']['id']] = song.register(self.client, item['track']['id'])

	@classmethod
	def update():
		playlists = client.user_playlists(self.username)
		for plist in playlists['items']:
			if plist['owner']['id'] == self.username and plist['name'] != "Rihanna - Stay 20syl. Remix" :
				self.__init__(plist, client, time.time())

	def show_tracks(self):
		[ item[1].display() for item in self.to.items() ]	

	@classmethod
	def cross_check(self, trackIdNo):
		return([ x[1].name for x in self.pl.items() for i in x[1].to.items() if i[1].id == trackIdNo and i[1] != None ])

	@classmethod
	def suggest_playlist(self):
		pass

	def save(self):
		"""save class as self.name.txt"""
		file = open("/home/boejaker/bin/spotify/data/playlists/"+self.name+'.txt','wb')
		file.write(self.cPickle.dumps(self.__dict__))
		file.close()

	@classmethod
	def load(self, name):
		"""try load self.name.txt"""
		file = open("/home/boejaker/bin/spotify/data/playlists/"+name+'.txt','rb')
		dataPickle = file.read()
		file.close()
		return(self.cPickle.loads(dataPickle))


######################################################################################################### 
# 
# Notification
# 
#########################################################################################################  
class notification():
	"""docstring for ClassName"""
	def __init__(self):
		pass




######################################################################################################### 
# 
# Chromecast Tools
# 
#########################################################################################################  
class Chromecast(homeNetwork):
	"""docstring for ClassName"""
	from time import sleep
	import pychromecast
	from pychromecast.controllers.spotify import SpotifyController
	import pychromecast.controllers.dashcast as dc

	import spotify_token as st
	import spotipy

	chromecasts = {}
	cc = {}

	def __init__(self, cast): 
		self.cast = cast 
		if cast:
			self.mc = self.cast.media_controller 
			self.name = self.cast.device.friendly_name
			self.ip = self.cast.host
			self.mac = run_process("python /home/boejaker/bin/JARVIS/netstat.py "+self.ip).rstrip()
			# self.aa = self.cast.status.display_name
			# self.playbackStatus = self.cast.status.status_text

			self.ipProfile = ipObject.register(self.name, self.ip, self.mac, "chromecast")
			self.cast.wait()

	@classmethod
	def build(self):
		self.chromecasts = self.pychromecast.get_chromecasts()
		for name in [cc.device.friendly_name for cc in self.chromecasts] :
			self.cc[name] = next(cc for cc in self.chromecasts if cc.device.friendly_name == name)
			self.cc[name] = self(self.cc[name])

	def cast_local(self, file):
		mediatype = "audio/wav"
		port = "3333"
		ip = ipObject.get_ip()
		run_process("/home/boejaker/bin/JARVIS/castTools.sh server "+port)
		self.cast.wait()
		self.sleep(10) 
		self.mc.play_media("http://"+ip+":"+port+file, mediatype)
		return(ip+":"+port+file)


	def cast_media(self, address):
	# Function Description
		mediatype = "image/jpeg"
		self.mc.play_media("http://"+address, mediatype)

	def media_type():
		pass

	def volume(self):
		pass

	# def spotify(self, trackid):
	# 	access_token = self.st.start_session("boejakerjaker80", "adalovelace")[0]

	# 	client = self.spotipy.Spotify(auth=access_token)

	# 	sp = self.SpotifyController(access_token)
	# 	self.device.register_handler(sp)
	# 	sp.launch_app()

	# 	for device in devices_available['devices']:
	# 		if device['name'] == self.name and device['type'] == 'CastVideo':
	# 			device_id = device['id']
	# 			break

	# 	client.start_playback(device_id=device_id, uris=["spotify:track:"+trackid])

	def dashcast(self, url):

		d = self.dc.DashCastController()
		self.cast.register_handler(d)

		print()
		print(self.cast.device)
		self.cast.wait()
		print()
		print(self.cast.status)
		print()
		print(self.cast.media_controller.status)
		print()
		self.cast.wait()

		self.kill_app()

		d.load_url(url)

		self.cast.wait()

		return(self.cast.status)


	def kill_app(self):
		while not self.cast.is_idle:
		    print("Killing current running app")
		    self.cast.quit_app()
		    self.cast.wait()

	def active_app(self):
		self.aa = self.cast.status.display_name
		return(self.aa)

	def state(self):
		self.playbackStatus = self.cast.status.status_text
		return(self.playbackStatus)

######################################################################################################### 
# 
# Database Objects
# 
#########################################################################################################  
class now_listening_db(SQLObject, homeNetwork):
	"""docstring for ClassName"""
	title = StringCol(default=None)
	album = StringCol(default=None)
	artists = StringCol(default=None)
	arturl = StringCol(default=None)
	playlists = StringCol(default=None)
	popularity = IntCol(default=0)
	idNo = StringCol(default=None)

class now_watching_db(SQLObject, homeNetwork):
	"""docstring for ClassName"""
	title = StringCol(default=None)
	series = StringCol(default=None)
	cast = StringCol(default=None)
	arturl = StringCol(default=None)
	genre = StringCol(default=None)
	rating = IntCol(default=0)
	idNo = StringCol(default=None)

class cast_db(SQLObject, homeNetwork):
	name = StringCol(default=None)
	ip = StringCol(default=None)
	network = StringCol(default=None)
	active = StringCol(default=None)
	app = StringCol(default=None)
	content = StringCol(default=None)
	availible = StringCol(default=None)

class ip_object_db(SQLObject, homeNetwork):
	ip = StringCol(default=None)
	mac = StringCol(default=None)
	name = StringCol(default=None)
	network = StringCol(default=None)
	activity = StringCol(default=None)
	functions = StringCol(default=None)

class user_db(SQLObject, homeNetwork):
	username = StringCol(default=None)
	password = StringCol(default=None)
	spotify_username = StringCol(default=None)
	spotify_password = StringCol(default=None)
	devices = StringCol(default=None)

class user_activity_db(SQLObject, homeNetwork):
	"""docstring for ClassName"""
	username = StringCol(default=None)
	now_watching = StringCol(default=None)
	now_listening = StringCol(default=None)
	now_browsing = StringCol(default=None)
	now_editing = StringCol(default=None)
	now_sheduled = StringCol(default=None)
	active_devices = StringCol(default=None)
	current_network = StringCol(default=None)
	current_location = StringCol(default=None)
	activity = StringCol(default=None)
	

######################################################################################################### 
# 
# Main Program
# 
#########################################################################################################  
if __name__ == '__main__':

	# Globals - Currently used for persistant storage of FIFO data
	spotify_now_playing = {}
	soundcloud_now_playing = {}
	network_data = {}
	
	# Disables system lock/sleep
	os.system("xset s noblank")
	os.system("xset -dpms")
	os.system("gsettings set org.gnome.desktop.session idle-delay 0")
	os.system("gsettings set org.gnome.desktop.screensaver lock-enabled false")
	# Locks screen with admin password
	# _thread.start_new_thread( os.system, ("while true ; do if [ $(gksudo echo ; echo \"$?\") -eq 0 ] ; then break ; fi ; done",) )
	
	# Main setup
	lan = homeNetwork()
	lan.build()

	# Update ip address records
	# ipObject.map_ip()
	# print(ipObject.address)
	
	# Webserver setup
	init_webserver(lan)

	# Init recovery systems
	b = Backup()

	# Chromecast debug
	#########################
	
	# print(Chromecast.cc['Chromecast1328'].device.status)
	# print(Chromecast.cc['Chromecast1328'].cast_local(speak("hello world")))
	# try:
	# 	Chromecast.cc['Chromecast1328'].dashcast("https://"+ipObject.address['wlp2s0'][1]+":/5000/spotify/")
	# except:
	# 	pass
	# print(Chromecast.cc['Chromecast1328'].name)
	# print(Chromecast.cc['Chromecast1328'].ip)
	# print(Chromecast.cc['Chromecast1328'].active_app())
	# print(Chromecast.cc['Chromecast1328'].state())
	# print(Chromecast.cc['Chromecast1328'].mc.status)
	# print(Chromecast.cc['Chromecast1328'].device.status)
	# Chromecast.cc['Chromecast1328'].spotify("3iwVGwKn6ovuToG9Uh9BIh")
	# Chromecast.cc['Chromecast1328'].mc.stop

	######################################################################################################### 
	# 
	# Webserver Callbacks
	# 
	#########################################################################################################  
	@app.route("/")
	def indexPage():
		return(render_template('index.html'))

	@app.route("/settings/")
	def settingsPage():
		return(render_template('settings.html'))

	@app.route("/putlocker/")
	def putockerPage():
		return(render_template('putlocker.html'))

	@app.route("/rfcontrols/")
	def rfControlsPage():
		return(render_template('rfcontrols.html'))

	@app.route("/spotify/")
	def spotifyPage():
		return(render_template('spotifyhtml.html'))


	@socketio.on('request_spotify_data')
	def request_spotify_data(data):
		global spotify_now_playing
		if lan.spotify.que.empty() is False:
			q = lan.spotify.que.get(False, 1)
			spotify_now_playing={'title': q.name, 'artist': q.artists, 'playlists':q.crosscheck(), 'user':"boejakerjaker80", 'progress':str(q.progress), 'duration':str(q.duration), 'popularity':str(q.popularity), 'color':str(q.color)}
		socketio.emit('spotify_data', spotify_now_playing)

	@socketio.on('request_network_data')
	def request_network_data(data):
		global network_data
		socketio.emit('network_data', network_data)

	@socketio.on('putlocker_query')
	def putlocker_query(query):
		putlocker_results=""
		socketio.emit('putlocker_results', putlocker_results)
		pass

	######################################################################################################### 
	# 
	# System Maintenance & Shutdown
	# 
	#########################################################################################################		
	while True:
		lan.automate()
		try:
			time.sleep(1)
		except (KeyboardInterrupt, SystemExit):
			# This section kills/closes any operational threads servers or ports and retruns the system to a default (non server-like) state
			# Enables system lock/sleep
			os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 600")
			os.system("gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 600")
			os.system("gsettings set org.gnome.desktop.session idle-delay 600")
			os.system("gsettings set org.gnome.desktop.screensaver lock-enabled true")
			raise


