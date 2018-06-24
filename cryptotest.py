import ccxt

class crypto(object):
	watchlist = {"BTC":"", "ETH":"", "EOS":"", "ADA":"", "IOTA":"", "NULS":"", "NEO":"", "SKY":"", "PAL":""}
	
	def __init__(self):
		self.build_market()

	def list_exchanges(self):
		n = [print(x) for x in ccxt.exchanges]
	def build_market(self):
		self.binance = ccxt.binance()
		self.coinbase = ccxt.coinbase()
		self.kucoin = ccxt.kucoin()

	def get_watchlist(self):
		for i in self.watchlist:
			try:
				self.watchlist[i] = self.binance.fetch_ticker(i+"/BTC")
			except:
				pass

	def query_watchlist(self, attribute):
		for i in self.watchlist:
			try:
				print(self.watchlist[i]["symbol"], self.watchlist[i]['info'][attribute])
			except TypeError:
				print(i)

	def list_attributes(self):
		for i in self.watchlist["ETH"]:
			print(i)
		print()
		for i in self.watchlist["ETH"]["info"]:
			print(i)

c = crypto()
c.get_watchlist()
print(c.watchlist)
c.query_watchlist("lastPrice")
c.list_attributes()