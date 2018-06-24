
# TODO
# Add pageination to putlocker.lookup
# Fix media url extraction for putlockerplus
# Add cast and share functons 
# Add url layout recognition (automatic recognition of key page elements)
# Add media player source selection i.e. megaupload, vidto
# Add close webdriver

import time

class putlocker(object):
	import requests_html
	from selenium import webdriver
	import re

	session = requests_html.HTMLSession()
	

	@classmethod
	def lookup(self, query="None", url=None, obj="item"):
		""" 
		Searches a webpage for objects of a particular class 
		returning their text and links.
		"""
		query=query.replace(' ', "+")
		if url is None:
			url = 'http://'+self.prefix+self.site+"/"+self.search+query+self.postfix 	
		r = self.session.get(url)
		result = r.html.find('.'+obj, first=False)
		resultsList = [[x.text, x.absolute_links] for x in result]
		return(resultsList)

	@classmethod
	def pop_mediaplayer(self, url, cover=None, content=None):
		""" Retruns a video players media url """
		chrome_options = self.webdriver.ChromeOptions().add_argument('headless')
		driver = self.webdriver.Chrome(chrome_options=chrome_options)
		action = self.webdriver.common.action_chains.ActionChains(driver)
		# url = 'http://www.'+self.site+"/"+self.watch+"/"+name+self.postfix
		driver.get(url)

		if cover is not None:
			cover = driver.find_element_by_class_name(cover)
			action.move_to_element(cover).click(cover).perform()	
		
		content = driver.find_element_by_class_name(content)
		videourl = self.re.search("(?P<url>https?://[^\s]+)", content.get_attribute('innerHTML')).group("url").strip('\"')

		return(videourl)

	@classmethod
	def pick_url(self, options):
		""" provides a menu of enumerated options """
		print("Please choose:")
		for idx, element in enumerate(options):
			try:
				element = element[0]
			except:
				pass
			if len(element) <= 3:
				element = "Episode "+element
			print("{}) {}".format(idx+1,element))
		i = input("Enter number: ")
		
		try:
			if 0 < int(i) <= len(options):
				try:
					print(options[int(i)-1][2])
				except:
					pass
				return options[int(i)-1][1]
		except:
		    pass
		return None

	@classmethod
	def atoi(self, text):
		return(int(text) if text.isdigit() else text)

	@classmethod
	def natural_keys(self, text):
		return([ self.atoi(c) for c in self.re.split('(\d+)', text) ])

	@classmethod
	def pick_series(self, options):
		""" provides a menu of enumerated options """
		options = [x for x in options]
		options.sort(key=self.natural_keys)
		print("Please choose:")
		for idx, element in enumerate(options):
			element = element.split("?")[1].replace("=", " ")
			print("{}) {}".format(idx+1,element))
		i = input("Enter number: ")
		try:
			return options[int(i)-1]
		except:
			return(None)

	@classmethod
	def pl_net_split(self, options):
		for idx, element in enumerate(options):

			series = [ x for x in element[1] if "series" in x ]
			if series:
				element[1] = series
				videoType = "Series"
			movie = [ x for x in element[1] if "movie" in x ]
			if movie:
				element[1] = movie
				videoType = "Movie"	
			episode = [ x for x in element[1] if "/episode" in x ]
			if episode:
				element[1] = episode
				videoType = "Episode "+str(idx+1)

			try:
				element.append(element[0].split(":")[1]) # appends the blurb
				element[0] = element[0].split(":")[0] # removes the blurb from the title
			except:
				pass

			element[0] = element[0].split("EPS")[0]
			element[0] = videoType+" "+element[0]
			resultwords  = [word for word in element[0].split() if word.lower() not in ["imdb","sd","hd"]]
			element[0] = ' '.join(resultwords)


		return(options)

	@classmethod
	def pl_net(self, query):
		self.prefix = ""
		self.site = "putlockers.net"
		self.search = "search?s="
		self.watch = "watch"
		self.postfix = ""
		
		media = [x for x in self.lookup(query=query, obj="featuredItems")]
		media = self.pl_net_split(media)
		url = self.pick_url(media)[0]
	
		episodes = [x for x in self.lookup(url=url, obj="featuredItems")][0]

		if [x for y in episodes for z in y for x in z if query in z]:
			series = [x for x in self.lookup(url=url, obj="movies-letter")][0][1]
			if len(series) >= 1:
				url = self.pick_series(series)
				episodes = [x for x in self.lookup(url=url, obj="featuredItems")]
			url = self.pick_url(self.pl_net_split(episodes))[0]
			# url = self.pop_url(url)
		
		url = self.pop_mediaplayer(url, cover='ds_seriesplay', content='videoPlayer')
	
		url = url.split("?")[0]+"?src=mirror3"
		return(url)
	
	@classmethod
	def pl_plus_split(self, options):
		for idx, element in enumerate(options):
			
			series = [ x for x in element[0].split() if "season" in x.lower() ]
			episode = [ x for x in element[1] if "episode" in x.lower() ]
			if series:
				videoType = "Series"
			elif episode:
				videoType = "Episode "+str(idx+1)
				element[0] = ""
			else:
				videoType = "Movie"	

			element[0] = videoType+" "+element[0]

		return(options)

	@classmethod
	def pl_plus(self, query):
		self.prefix = "www."
		self.site = "putlockers.plus"
		self.search = "search-movies/"
		self.watch = "watch"
		self.postfix = ".html"
		self.sources = [""]
		
		url = [x for x in self.lookup(query=query, obj="item")]
		url = self.pick_url(self.pl_plus_split(url))
		url = str(url).strip('{\'}')

		episodes = [x for x in self.lookup(url=url, obj="episode_series_link")]
		if len(episodes) >= 1:
			self.pick_url(self.pl_plus_split(episodes))
			url = str(url).strip('{\'}')
		return(url)

	@classmethod
	def close_session(self):
		pass

	@classmethod
	def cast(self, url):
		if input("Cast video? y/n").lower() == "y":  
			pass

	@classmethod		
	def view(self, url):
		if input("View video? y/n").lower() == "y": 
			driver = self.webdriver.Chrome()
			driver.get(url)

			action = putLocker.webdriver.common.action_chains.ActionChains(driver)
			action.click().perform()
			time.sleep(8)
			driver.switch_to.window(window_name=driver.window_handles[1])
			driver.close()
			driver.switch_to.window(window_name=driver.window_handles[0])
			action.click().perform()


class Series(putlocker):
	"""docstring for ClassName"""
	def __init__(self, name, info):
		self.title = name
		self.info = info
		self.episodes = ""

# class episode(putlocker):
# 	"""docstring for ClassName"""
# 	def __init__(self, arg):
# 		super(ClassName, self).__init__()
# 		self.arg = arg

# class movie(putlocker):
# 	"""docstring for ClassName"""
# 	def __init__(self, arg):
# 		super(ClassName, self).__init__()
# 		self.arg = arg
		



putLocker = putlocker()
while True:
	query = input("Search for a film or tv show: ")
	url = putLocker.pl_net(query)
	if url:
		putlocker.cast(url)
		putlocker.view(url)
