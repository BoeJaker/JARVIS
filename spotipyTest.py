#!/usr/bin/env python


######################################################################################################### 
# 
# 
# 
#########################################################################################################                 
class spotify(object):
	import os
	import spotify_token as st
	import spotipy
	import spotipy.util as util
	import _pickle as cPickle
	import traceback
	import time
	
	# Object endpoint lists  
	pl = {}
	sl = {}

	lastPlaying = {}
	nowPlaying = {}

	updateFreq = 10

	# Meta Variables
	mood = ""

	def __init__(self):
		
		print("")
		print("Building Spotify client instance")
		self.username = "boejaker80"
		self.ip = self.get_ip()
		self.port = "8888" # HTTP listener port for auth response
		self.token = self.util.prompt_for_user_token(self.username)
		self.client = self.spotipy.Spotify(auth=self.token)
		self.features = "wallpaper_switcher"
		self.pl = playlist.build(self.client)
		self.plTriggers = ["Deep", "Hype", "Chill", "Summer", "Work"]
		self.sTriggers = ["", ""]
		self.sl = song.sl
		self.np = {"now":song(None, self.client, None, None),"last":song(None, self.client, None, None)}
		self.socket = {}
		print("Spotify client instance build complete")
		print("")

	def update(self):
		if self.now_playing() is not None:
			# socketio.emit('data', self.socket_write(), namespace='/', broadcast=True)
			self.device = ""
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
		self.os.system("wget -qO /home/joseph/bin/spotify/coverart.jpeg "+artUrl)
		self.time.sleep(0.4)
		self.os.system("gsettings set org.gnome.desktop.background picture-uri file:///home/coverart.jpeg")
		self.time.sleep(0.1)
		self.os.system("gsettings set org.gnome.desktop.background picture-uri file:///home/joseph/bin/spotify/coverart.jpeg")

	def song_trigger_action(self, song):
		return([ x for x in self.sTriggers if x.name == song.name ])

	def playlist_trigger_action(self, song):
		plcc = playlist.cross_check(song.id)
		return([ x for x in plcc for y in self.plTriggers if x == y ])

	def deamon(self):
		exit = False
		while exit == False:
			if self.update() is not False:
				self.nowPlaying = self.np['now']
				self.display_now_playing()
				if "wallpaper_switcher" in self.features:
					self.coverart_wallpaper_switcher(self.np['now'])
				if "playlist_trigger" in self.features:
					self.playlist_trigger_action(self.np['now'])
				if "song_trigger" in self.features:
					self.song_trigger_action(self.np['now'])
			self.time.sleep(self.updateFreq)
	
	def mood_analysis(self):
		# valance
		# playlist
		pass
	
	def progress(self):
		self.np['now'].duration

	def socket_write(self):
		self.socket={'title': self.np['now'].name, 'artist': self.np['now'].artists, 'playlists':self.np['now'].crosscheck(), 'user':self.username, 'progress':str(self.np['now'].progress), 'duration':str(self.np['now'].duration), 'popularity':str(self.np['now'].popularity)}
		return(self.socket)

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

	@staticmethod
	def get_ip():
		import socket
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		ip = s.getsockname()[0]
		s.close()
		return(ip)

######################################################################################################### 
# 
# 
# 
#########################################################################################################                 
class song(spotify):

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

				self.sl[idNo] = song(data, client, idNo, self.time.time())
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
		file = open("/home/joseph/bin/spotify/data/tracks/"+self.id+'.txt','wb')
		file.write(self.cPickle.dumps(self.__dict__))
		file.close()

	@classmethod
	def load(self, name):
		"""try load self.name.txt"""
		file = open("/home/joseph/bin/spotify/data/tracks/"+name+'.txt','rb')
		dataPickle = file.read()
		file.close()
		return(self.cPickle.loads(dataPickle))

######################################################################################################### 
# 
# 
# 
#########################################################################################################                 
class playlist(spotify):

	pl = {}
	username = "boejaker80"

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
				upd = self.time.time()
				
				try: 	
					obj = self.load(plist['name'])
					if self.time.time()-obj['updated'] <= 10:
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
				self.__init__(plist, client, self.time.time())

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
		file = open("/home/joseph/bin/spotify/data/playlists/"+self.name+'.txt','wb')
		file.write(self.cPickle.dumps(self.__dict__))
		file.close()

	@classmethod
	def load(self, name):
		"""try load self.name.txt"""
		file = open("/home/joseph/bin/spotify/data/playlists/"+name+'.txt','rb')
		dataPickle = file.read()
		file.close()
		return(self.cPickle.loads(dataPickle))


######################################################################################################### 
# 
# Allows it to run as a standalone demo
# 
#########################################################################################################                 
if __name__ == '__main__':

	import _thread
	from flask import Flask, render_template
	from flask_socketio import Namespace, SocketIO, send, emit
	app = Flask(__name__)
	socketio = SocketIO(app)


	music = spotify()
	# print(music.__dict__)
	music.update()
	print(music.np['now'].progress)
	music.coverart_wallpaper_switcher(music.np['now'])
	print(music.playlist_trigger_action(music.np['now']))
	# song.display_all()
	music.pl['Deep'].show_tracks()
	print(music.np['now'].name)
	print(playlist.cross_check(music.np['now'].id))
	# music.sl['4MCU3lOwRiapFjE9kxiW0f'].display(v=True)


	@app.route("/")
	def indexPage():
		return(render_template('index.html'))

	@app.route("/spotify/")
	def spotifyPage():
		return(render_template('spotifyhtml.html'))
	
	@socketio.on('request_data')
	def send_data(data):
		socketio.emit('data', music.socket_write(), namespace='/', broadcast=True)

	_thread.start_new_thread(socketio.run, (app, ), {'host':"0.0.0.0",})


	music.deamon()

		
		