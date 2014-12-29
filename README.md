SPS
===

Spawnkill Protection System for Digital Paint: Paintball2

To run it on linux:
<ul>
<li>Clone the github repo:</li>
</ul>
```
git clone https://github.com/hTmlDP/SPS
```
To run it on linux:
<ul>
<li>Edit the config lines in sps.py with any text editor</li>
</ul>
```python
#------------------CONFIG------------------
SPAWNKILL_TIME_=1 #time in seconds
SPAWNKILL_LIMIT=5 #limit
SPAWNKILL_TIMES={				#Spawnkill times for specific maps, leave empty if you want it to be default
				'airtime': 3,
				'propaint1': 5
				}
ADMIN_IDS=[200335, 207997]
LOGFILE='qconsole27910.log' #replace with you server's logfile, propably 'qconsolePORT.log'
							#CHECK IF LOGGING IS ENABLED FIRST! IF NOT, SET sl_logging to 2

RCON_PASSWORD='1234' #replace with your server's rcon_password (set it at the end of your server's config)
HOSTNAME='127.0.0.1' #Server's IP,  propably you dont need to change it
PORT=27910 #Server's port
#That's a list of DPLogin ids of SPS admins.
#the admins will be able to:
# -disable SPS (!stop)
# -enable SPS (!start)
# -change SPAWNKILL_TIME (!time TIME)
# -change SPAWNKILL_LIMIT (!limit LIMIT)
# -change SPAWNKILL_TIMES[map] (!maptime TIME)
#------------------------------------------
```
<ul><li>Copy it to the /pball directory</li></ul>
<ul><li>Create a new screen (screen -S sps)</li></ul>
<ul><li>Go to the pball directory and run it ("python sps.py")</li></ul>
