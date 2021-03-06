from os.path import getsize
from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM
from urllib2 import urlopen
import time
import re
#------------------_EVT_ACTIONS----------------------#
ERR_TIMEOUT = 'e0'
ERR_BAD_RCON_PASSWORD = 'e1'
EVT_CHAT = 'ev0'
EVT_ELIM = 'ev1'
EVT_RESPAWN = 'ev2'
EVT_MAPCHANGE = 'ev3'
EVT_DATE = 'ev4'
EVT_ROUNDSTARTED = 'ev5'
EVT_NAMECHANGE = 'ev6'
#-----------------------------------------------------#
char_tab = ['\0','-', '-', '-', '_', '*', 't', '.', 'N', '-', '\n','#', '.', '>', '*', '*',
			'[', ']', '@', '@', '@', '@', '@', '@', '<', '>', '.', '-', '*', '-', '-', '-',
			' ', '!', '\"','#', '$', '%', '&', '\'','(', ')', '*', '+', ',', '-', '.', '/', 
			'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?',
			'@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
			'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\',']', '^', '_',
			'`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
			'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '<',
			'(', '=', ')', '^', '!', 'O', 'U', 'I', 'C', 'C', 'R', '#', '?', '>', '*', '*',
			'[', ']', '@', '@', '@', '@', '@', '@', '<', '>', '*', 'X', '*', '-', '-', '-',
			' ', '!', '\"','#', '$', '%', '&', '\'','(', ')', '*', '+', ',', '-', '.', '/',
			'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?',
			'@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
			'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\',']', '^', '_',
			'`', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
			'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '{', '|', '}', '~', '<']
def ListToDict(l):
	dictionary={}
	j=0
	for i in l:
		dictionary[j]=i
		j=j+1
	return dictionary

def CleanSpecialChars(text):
	cleaned_text = ""
	skip_next = False
	for i in text:
		char_ascii=ord(i)
		#134-underline, 135-italic, 136-color
		if char_ascii==134 or char_ascii==135 or char_ascii==136 or skip_next: # Remove underline, italic symbols                           
			if char_ascii==136:
				skip_next = True
			else:
				skip_next = False
		else:
			cleaned_text = cleaned_text+char_tab[char_ascii]
			skip_next = False
	return cleaned_text

def GetPlayerInfo(nameorid):
	nicks=[]
	try:
		dp_id=int(nameorid)
		res=urlopen('http://dplogin.com/index.php?action=viewmember&playerid={id}'.format(id=nameorid)).read()
		names=re.findall('\\<tr\\>\\<td\\>\\<b\\ class\\=\\"faqtitle\\"\\>Names?\\ registered\\:\\<\\/b\\>\\<\\/td\\>\\<td\\>(.*?)\\<\\/td\\>\\<\\/tr\\>', res)[0]
	except:
		response=urlopen('http://dplogin.com/index.php?action=displaymembers&search={name}'.format(name=nameorid)).read()
		matches=re.findall('\\<a\\ href\\=\\"\\/index\\.php\\?action\\=viewmember\\&playerid\\=(\d+)\\"\\>.*?\\<\\/a\\>', response)
		full_list=[]
		response_list=[]
		for i in matches:
			response=urlopen('http://dplogin.com/index.php?action=viewmember&playerid={id}'.format(id=i)).read()
			response_list.append(response)
			names=re.findall('\\<tr\\>\\<td\\>\\<b\\ class\\=\\"faqtitle\\"\\>Names?\\ registered\\:\\<\\/b\\>\\<\\/td\\>\\<td\\>(.*?)\\<\\/td\\>\\<\\/tr\\>', response)[0].split(', ')
			full_list.append([str(i), names])
			if nameorid.lower() in names:
				dp_id=str(i)
				res=response
			else:
				if matches.index(i)==len(matches)-1:
					names=full_list[0][1]
					dp_id=full_list[0][0]
					res=response_list[0]
	clan=re.findall('\\Active\\ (?:Clans)|(?:Clan)\\:\\<\\/b\\>\\<\\/td\\>\\<td\\>.*?\\<\\/td\\>\\<\\/tr\\>', res)
	for i in clan: #len(clan) is 0 or 1 propably
		clan=re.findall('\\<a\\ href\\=\\"\\/index.php\\?action\\=viewclan\\&clanid\\=\d+\\"\\>(.*?)\\<\\/a\\>', i)
	return {
			'clan': clan,
			'names': names,
			'id': dp_id 
			}
#-----------------------------------------------------#
class Server():
	def __init__(self, rcon_password, hostname, port, logfile=None):
		self.__rcon_password = rcon_password
		self.__hostname = hostname
		self.__port = port
		self.__logfile = logfile
		self.__alive=True
		if logfile != None:
			Thread(target=self.MainLoop).start()
		self._EVT_ACTIONS={
					EVT_ELIM: [],
					EVT_CHAT: [],
					EVT_RESPAWN: [],
					EVT_MAPCHANGE: [],
					EVT_DATE: [],
					EVT_ROUNDSTARTED: [],
					EVT_NAMECHANGE: []
					}
	def __del__(self):
		self.__alive=False

	def Bind(self, event, target):
		self._EVT_ACTIONS[event].append(target)

	def UnBind(self, event, target):
		self._EVT_ACTIONS[event].remove(target)
	#----------------------------------------------------
	def rcon(self, command=None):
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.connect((self.__hostname, self.__port))
		sock.settimeout(1)
		if command != None:
			sock.send("\xFF\xFF\xFF\xFFrcon %s %s\0" % (self.__rcon_password, command))
		else:
			sock.send("\xFF\xFF\xFF\xFFstatus\0")
		try:
			response = sock.recv(2048)
		except:
			raise Exception('UDP Connection timed out')
		if response == '\xff\xff\xff\xffprint\nBad rcon_password.\n':
			raise Exception('Bad rcon password.')
		return response[:-1]
	#----------------------------------------------------
	def SimplePlayerlist(self):
		dictionary=self.Status()
		players=dictionary['players']
		playerlist=[]
		for i in players:
			playerlist.append(i['name'])
		return playerlist

	def Status(self):
		dictionary = {}
		players = []
		response = self.rcon().split('\n')[1:]
		variables = response[0]
		players_ = (response[1:])
		for i in players_:
			temp_dict={}
			cleaned_name = CleanSpecialChars(i)
			separated = cleaned_name.split(' ')
			temp_dict['score'] = separated[0]
			temp_dict['ping'] = separated[1]
			temp_dict['name'] = cleaned_name.split("%s %s " % (separated[0], separated[1]))[1][1:-1]
			players.append(temp_dict)
		dictionary['players'] = players
		variables=variables.split('\\')[1:]
		for i in range(0, len(variables), 2):
			dictionary[variables[i]] = variables[i+1]
		return dictionary
	#-----------------------------------------------------
	def _Event(self, text):
		#--------Date [Added in 1.0]
		if text.find('^[********] Date: ')!=-1:
			self.basetime=self.basetime+86400 #24*60*60
			return

		#--------Elimination
		elim=re.findall('^\\[\d\d\\:\d\d\\:\d\d\\]\\ \\*(.*?)\\ \\((.*?)\\)\\ eliminated\\ \\*(.*?)\\ \\((.*?)\\).', text)
		#[18:54:24] *|ACEBot_1| (Spyder SE) eliminated *|herself| (Spyder SE).
		if len(elim)!=0:
			arg=[time.time()]
			arg.extend(list(elim[0]))
			arg=ListToDict(arg)
			arg['time']=arg[0]
			arg['player1']=arg[1]
			arg['gun1']=arg[2]
			arg['player2']=arg[3]
			arg['gun2']=arg[4]
			for function in self._EVT_ACTIONS[EVT_ELIM]:
				function(arg) #1 argument - dict: [time, player1, gun1, player2, gun2]
			return

		#--------Round started
		if re.match('^\\[\d\d\\:\d\d\\:\d\d\\]\\ Round\\ started\\.\\.\\.', text):
			arg={}
			arg[0]=time.time()
			arg['time']=arg[0]
			for function in self._EVT_ACTIONS[EVT_ROUNDSTARTED]:
				function(arg) #1 argument - list: [time (seconds)]

		#--------Respawn
		respawn=re.findall("^\\[\d\d\\:\d\d\\:\d\d\\]\\ \\*(.*?)\\'s\\ (.*?)\\ revived\\!", text)#[19:03:57] *Red's ACEBot_6 revived!
		if len(respawn)!=0:
			arg=[time.time()]
			arg.extend(list(respawn[0]))
			arg=ListToDict(arg)
			arg['time']=arg[0]
			arg['team']=arg[1]
			arg['player']=arg[2]
			for function in self._EVT_ACTIONS[EVT_RESPAWN]:
				function(arg) #1 argument - list: [time (seconds), player]
			return
		#--------Chat
		chat=re.findall("^\\[\d\d\\:\d\d\\:\d\d\\]\\ (.*?)\\: (.+)", text)
		#[19:54:18] hTml: test
		if len(chat)!=0:
			arg=[time.time()]
			arg.extend(list(chat[0]))
			arg=ListToDict(arg)
			if arg[1][:6]=='[OBS] ': #remove the "[OBS]" tag
				arg[1]=arg[1][6:]
			if arg[1][:7]=='[ELIM] ': #remove the "[ELIM]" tag
				arg[1]=arg[1][7:]
			arg['time']=arg[0]
			arg['player']=arg[1]
			arg['text']=arg[2]
			playerlist=self.SimplePlayerlist()
			if arg[1] in playerlist or arg[1] in ['newbie', 'noname']:
				for function in self._EVT_ACTIONS[EVT_CHAT]:
					function(arg) #1 argument - list: [time (seconds), player, text]
		#--------Name change
		namechange=re.findall('^\\[\d\d\\:\d\d\\:\d\d\\]\\ (.*?)\\ changed\\ name\\ to\\ (.*?)\\.', text)
		#[19:21:48] .sTone.hTml changed name to adcg.
		if len(namechange)!=0:
			arg=[time.time()]
			arg.extend(list(namechange[0]))
			arg=ListToDict(arg)
			arg['time']=arg[0]
			arg['name1']=arg[1]
			arg['name2']=arg[2]
			for function in self._EVT_ACTIONS[EVT_NAMECHANGE]:
				function(arg) #1 argument - list: [time (seconds), player, text]

		#--------Map change
		mapchange=re.findall("^\\[\d\d\\:\d\d\\:\d\d\\]\\ \\=\\=\\ Map Loaded\\:\\ (.*?)\\ \\=\\=", text)#[19:49:17] == Map Loaded: propaint1 ==
		if len(mapchange)!=0:
			arg=[time.time()]
			arg.extend(mapchange)
			arg=ListToDict(arg)
			arg['time']=arg[0]
			arg['map']=arg[1]
			for function in self._EVT_ACTIONS[EVT_MAPCHANGE]:
				function(arg) #1 argument - list: [time (seconds), new map]
			return

	def GetPlayersIP(self, name):
		response=self.rcon('sv listuserip')
		matches=re.findall('{name}\\ \\[(\d+\\.\d+\\.\d+\\.\d+)\\:(\d+)\\]'.format(name=name), response, re.MULTILINE)
		if len(matches)>0:
			return list(matches[0])
		return []
	#-----------------------------------------------------
	def Say(self, text):
		self.rcon('say %s' % text.format(C=chr(136), U=chr(134), I=chr(135)))
	def GetPlayersIngameID(self, name):
		for i in self.rcon_players():
			if name==i['name']:
				return i['id']
		return None

	def rcon_players(self):
		return_value=[]
		response=self.rcon('sv players')
		response=re.findall('(\d+) \\(?(.*?)\\)?\\]\\ \\*\\ (?:OP\\ \d+\\,\\ )?(.+)\\ \\((b\d+)\\)', response)
		for i in response:
			dictionary={}
			dictionary['id']=i[0]
			dictionary['dplogin']=i[1]
			dictionary['name']=i[2]
			dictionary['build']=i[3]
			return_value.append(dictionary)
		return return_value

	def rcon_listuserip(self):
		response=self.rcon('sv listuserip')
		matches=re.findall('admin\\ is\\ listing\\ IP\\ for\\ (.*?)\\ \\[(.*?)\\:(\d+)\\]', response, re.MULTILINE)
		names=[]
		ips=[]
		for i in matches:
			names.append(i[0])
			ips.append(i[1])
		return [names, ips]
	#-----------------------------------------------------
	def MainLoop(self):
		import time
		self.basetime=0
		log_file=open(self.__logfile, 'r')
		log_file.readlines()
		while self.__alive:
			i=log_file.readline()
			if i:
				self._Event(i)
			time.sleep(0.05)
#------------------------------------------------------
