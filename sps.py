#------------------CONFIG------------------
SPAWNKILL_TIME_=2 #time in seconds
SPAWNKILL_LIMIT=3 #limit
SPAWNKILL_TIMES={				#Spawnkill times for specific maps, leave empty if you want it to be default
				'airtime': 3,
				'propaint1': 5
				}
ADMIN_IDS=[200335, 207997]
LOGFILE='qconsole27910.log' #replace with you server's logfile, propably 'qconsolePORT.log'
							#CHECK IF LOGGING IS ENABLED FIRST! IF NOT, SET sl_logging to 2

RCON_PASSWORD='1234' #replace with your server's rcon_password (set it at the end of your config)
HOSTNAME='127.0.0.1' #Server's IP,  propably you dont need to change it
PORT=27910 #Server's port
#That's a list of DPLogin ids of SPS admins.
#the admins will be able to:
# -disable SPS (!stop)
# -enable SPS (!start)
# -change SPAWNKILL_TIME (!time TIME)
# -change SPAWNKILL_LIMIT (!limit LIMIT)
#------------------------------------------
from pypb2lib import *
RUNNING=True
respawns={}
spawnkills={}
startonround=False
def OnMapchange(l):
	global startonround, RUNNING, SPAWNKILL_TIME, respawns, spawnkills
	if l['map'] in SPAWNKILL_TIMES:
		SPAWNKILL_TIME=SPAWNKILL_TIMES[l['map']]
	else:
		SPAWNKILL_TIME=SPAWNKILL_TIME_
	spawnkills={}
	startonround=True
	RUNNING=False

def Admin(cmd, l):
	global RUNNING, SPAWNKILL_TIME, SPAWNKILL_LIMIT, SPAWNKILL_TIME_
	for i in server1.rcon_players():
			if i['name']==l['player']:
				if not int(i['dplogin']) in ADMIN_IDS:
					server1.Say('{C}0[{C}QSPS{C}0]{C}9 Insufficient privileges.')
					return

	if cmd=='!start': RUNNING=True; server1.Say('{C}0[{C}QSPS{C}0]{C}9 Spawnkill protection {C}Jenabled{C}9.'); return
	if cmd=='!stop': RUNNING=False; server1.Say('{C}0[{C}QSPS{C}0]{C}9 Spawnkill protection {C}Adisabled{C}9.'); return
	if cmd=='!time':
		val=l['text'].split('!time ')
		if len(val)==2:
			try:
				val=int(val[-1])
			except:
				server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_TIME{I} must be an {I}INTEGER{I}.')
				return
			SPAWNKILL_TIME_=val
			server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_TIME{I} set to {I}%s{I}.' % SPAWNKILL_TIME_)
		else:
			server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_TIME{I} is {I}%s{I}.' % SPAWNKILL_TIME_)
		return
	if cmd=='!limit':
		val=l['text'].split('!limit ')
		if len(val)==2:
			try:
				val=int(val[-1])
			except:
				server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_LIMIT{I} must be an {I}INTEGER{I}.')
				return
			SPAWNKILL_LIMIT=val
			server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_LIMIT{I} set to {I}%s{I}.' % SPAWNKILL_LIMIT)
		else:
			server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_LIMIT{I} is {I}%s{I}.' % SPAWNKILL_LIMIT)
		return
	if cmd=='!maptime':
		mapname=server1.Status()['mapname']
		val=l['text'].split('!maptime ')
		if len(val)==2:
			try:
				val=int(val[-1])
			except:
				server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_TIME{I} must be an {I}INTEGER{I}.')
				return
			SPAWNKILL_TIME=val
			SPAWNKILL_TIMES[mapname]=val
			server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_TIME{I} for {I}%s{I} set to {I}%s{I}.' % (mapname, SPAWNKILL_TIMES[mapname]))
		else:
			if mapname in SPAWNKILL_TIMES:
				server1.Say('{C}0[{C}QSPS{C}0]{C}9 {I}SPAWNKILL_TIME{I} for {I}%s{I} is {I}%s{I}.' % (mapname, SPAWNKILL_TIMES[mapname]))
			else:
				server1.Say('{C}0[{C}QSPS{C}0]{C}9 No custom {I}SPAWNKILL_TIME{I} for {I}%s{I}.' % mapname)
		return
	if cmd=='!delmaptime':
		mapname=server1.Status()['mapname']
		if mapname in SPAWNKILL_TIMES:
			del SPAWNKILL_TIMES[mapname]
			server1.Say('{C}0[{C}QSPS{C}0]{C}9 Custom {I}SPAWNKILL_TIME{I} for {I}%s{I} deleted.' % mapname)
		else:
			server1.Say('{C}0[{C}QSPS{C}0]{C}9 No custom {I}SPAWNKILL_TIME{I} for {I}%s{I}.' % mapname)
		return

def OnChat(l):
	if len(l[2].split('!nicks '))==2:
			try:
				info=GetPlayerInfo(l[2].split('!nicks ')[-1])
				server1.Say('{C}QID{C}9: %s' % info['id'])
				server1.Say('{C}QName/s{C}9: %s' % ', '.join(info['names']))
				server1.Say('{C}QClan/s{C}9: %s' % ', '.join(info['clan']))
			except:
				server1.Say('{C}9This Name/ID is not registered.')
			return
	if l['text'].find('!start')==0: Admin('!start', l)
	if l['text'].find('!stop')==0: Admin('!stop', l)
	if l['text'].find('!time')==0: Admin('!time', l)
	if l['text'].find('!maptime')==0: Admin('!maptime', l)
	if l['text'].find('!limit')==0: Admin('!limit', l)
	if l['text'].find('!delmaptime')==0: Admin('!delmaptime', l)
	if l['text'].find('!help')==0: server1.Say('{C}0[{C}QSPS{C}0]{C}9 !help | !start | !stop | !time | !limit | !maptime | !delmaptime | !nicks') #TODO: help for a specified command.
	



def OnRound(l):
	global respawns, RUNNING, startonround
	for player in server1.rcon_players():
		respawns[player['name']]=l['time']
	if startonround:
		startonround=False
		RUNNING=True

def OnRespawn(l):
	global respawns
	respawns[l['player']]=l['time']

def OnElim(l):
	if not RUNNING: return
	global spawnkills
	restime=respawns[l['player2']]
	if l['time']-restime<SPAWNKILL_TIME:
		if l['player1'] in spawnkills:
			spawnkills[l['player1']][0]=spawnkills[l['player1']][0]+1
		else:
			spawnkills[l['player1']]=[1, l['time']]
		if spawnkills[l['player1']][0]==SPAWNKILL_LIMIT:
			server1.Say('{C}0[{C}QSPS{C}0]{C}A %s {C}9 CAN BE {C}A{U}KICKED{U}{C}9 FOR {C}ASPAWNKILLING{C}9!' % l['player1'])
			return
		if spawnkills[l['player1']][0]>SPAWNKILL_LIMIT:
			server1.Say('{C}0[{C}QSPS{C}0]{C}A %s {C}9 WILL BE {C}A{U}KICKED{U}{C}9 FOR {C}ASPAWNKILLING{C}9!' % l['player1'])
			server1.rcon('kick %s' % server1.GetPlayersIngameID(l['player1']))
			del spawnkills[l['player1']]
			return
		server1.Say('{C}0[{C}QSPS{C}0]{C}9 %s,{C}A STOP SPAWNKILLING!' % l['player1'])
	if l['time']-restime>30 and l['player1'] in spawnkills:
		del spawnkills[l['player1']]

def OnNamechange(l):
	global spawnkills
	global respawns
	if l['name1'] in spawnkills:
		spawnkills[l['name2']]=spawnkills[l['name1']]
		respawns[l['name2']]=respawns[l['name1']]
		del respawns[l['name1']]
		del spawnkills[l['name1']]
SPAWNKILL_TIME=SPAWNKILL_TIME_
server1=Server(hostname=HOSTNAME, logfile=LOGFILE, rcon_password=RCON_PASSWORD, port=PORT) #TODO: add support for multiple servers
server1.Bind(EVT_RESPAWN, OnRespawn)
server1.Bind(EVT_ROUNDSTARTED, OnRound)
server1.Bind(EVT_ELIM, OnElim)
server1.Bind(EVT_NAMECHANGE, OnNamechange)
server1.Bind(EVT_MAPCHANGE, OnMapchange)
server1.Bind(EVT_CHAT, OnChat)
OnRound({'time': 0})
server1.Say('{C}0[{C}QSPS{C}0]{C}9 Spawnkill protection {C}Jenabled{C}9.')
raw_input()
server1.__del__()
