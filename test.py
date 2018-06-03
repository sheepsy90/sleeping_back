import requests
import json
import matplotlib.pyplot as plt
import datetime
import os

import numpy as np

DATA = {}
GATHER = False
country = 'sweden'
city = 'kiruna'

PATH = os.path.join(country, city)
DATA_PATH = os.path.join(PATH, 'data')

if not os.path.exists(PATH):
    os.makedirs(PATH)

# If we do not have the data we gather it
if not os.path.exists(DATA_PATH):
	
	for year in [2013, 2014, 2015, 2016, 2017, 2018]:
		for month in range(1, 13):
			
			if year == 2018 and month > 4:
				continue
			
			if month < 10:
				month = '0{}'.format(month)
			

			result = requests.get("https://www.timeanddate.com/weather/{}/{}/historic?month={}&year={}".format(country, city, month, year))

			rows = [e for e in result.content.split("\n") if e.startswith("var data=")]

			data = rows[0].replace('var data=', '')
			data = data.replace(';window.month={};window.year={};'.format(int(month), year), '')

			laoded = json.loads(data)
			
			key = '{}-{}'.format(year, month)
			
			print key
			
			DATA[key] = laoded
			
	# WRITE it to file
	with open(DATA_PATH, 'w') as f:
		f.write(json.dumps(DATA))
else:
	with open(DATA_PATH, 'r') as f:
		DATA = json.loads(f.read())

def date_parse(e):
	dt = datetime.datetime.fromtimestamp(int(e)/1000)
	
	if dt.hour <= 8 or dt.hour >= 21:
		return dt
		
#t_w, t_m, t_e
sleeping_bags = {
	"Icefall 3": [-8, -15, -36],
	"Icefall 2": [-3, -9, -28],
	"Icefall 1": [ 1, -4, -21] ,
	"Serac 600": [ -7, -14, -35], 
	"Serac 300": [ 2, -4, -21]
}

bag_stats = {}

for name, stats in sleeping_bags.items():
	
	bag_stats[name] = {}

	for _month in range(1, 13):
		
		bag_stats[name][_month] = []
		
		_hour_data = {}
		_raw = []

		for key, value in DATA.items():		
			data = [(date_parse(e['date']), e.get('temp')) for e in value['temp']]
			data = [e for e in data if e[0] is not None and e[1] is not None]
			
			year, month = key.split("-")
			month = int(month)
			
			if month != _month:
				continue

			plt.title(_month)

			for element in data:
				_d, tmp = element
				
				if _d.hour not in _hour_data:
					_hour_data[_d.hour] = []
				
				_hour_data[_d.hour].append(tmp)
				_raw.append([_d.hour, tmp])
				


		_hour_data_list = _hour_data.items()
		_hour_labels = [e[0] for e in _hour_data_list]
		_temp_lists = [e[1] for e in _hour_data_list]
		
		plt.clf()
		
		t_w, t_m, t_e = stats
		
		
		# Moving the extreme point between lowest and  extreme rating
		# t_e += (t_m - t_e) / 2

		_raw_t_w = [e for e in _raw if e[1] >= t_w]
		_raw_t_m = [e for e in _raw if t_w > e[1] >= t_m]
		_raw_t_e = [e for e in _raw if t_m > e[1] >= t_e]
		_raw_t_d = [e for e in _raw if t_e > e[1]]
		
		bag_stats[name][_month] = [len(_raw_t_w), len(_raw_t_m), len(_raw_t_e), len(_raw_t_d)]

		
		for _scatter, col in [(_raw_t_w, 'gx'), (_raw_t_m, 'yx'), (_raw_t_e, 'rx'), (_raw_t_d, 'kx')]:
			x = [e[0] for e in _scatter]
			y = [e[1] for e in _scatter]
			plt.plot(x, y, col)

		result = plt.boxplot(_temp_lists) #, whis=10)
		
		plt.xticks(range(1, 1+len(_temp_lists)), _hour_labels, rotation='vertical')
		plt.title(_month)
		plt.xlabel("Hours of the day (g=women, y=men, r=extrem, b=death)")
		plt.ylabel("Temperature boxpot")
		plt.savefig(os.path.join(PATH, 'month_{}.png'.format(_month)))


plt.clf()

for idx, element in enumerate(bag_stats.items()):
	name, stats = element
	
	for month, data in stats.items():
		
		t_w, t_m, t_e, t_d = data
		
		_s = sum(data)
		
		t_wp = (t_w / float(_s))
		t_mp = (t_m / float(_s))
		t_ep = (t_e / float(_s))
		t_dp = (t_d / float(_s))
		
		print [t_wp, t_mp, t_ep, t_dp]
		
		if t_wp > 0.95:
			plt.plot(idx, month, 'go', markersize=10)
			
		if t_wp > 0.95:
			plt.plot(idx, month, 'yo', markersize=8)
			
		if t_ep > 0.05:
			plt.plot(idx, month, 'rs', markersize=4)

		if t_dp > 0:
			plt.plot(idx, month, 'kx', markersize=10)

plt.axis('equal')
plt.xticks(range(len(bag_stats)), bag_stats.keys(), rotation='vertical')
plt.title(PATH)

plt.xlabel("Different Sleeping bags ")
plt.ylabel("Month")

plt.savefig('{}_{}.png'.format(country, city))

plt.show()
print (bag_stats)
