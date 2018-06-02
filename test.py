import requests
import json
import matplotlib.pyplot as plt
import datetime

DATA = {}
"""
for year in [2015, 2016, 2017, 2018]:
	for month in range(1, 13):
		
		if year == 2018 and month > 4:
			continue
		
		if month < 10:
			month = '0{}'.format(month)
		

		result = requests.get("https://www.timeanddate.com/weather/sweden/uppsala/historic?month={}&year={}".format(month, year))

		rows = [e for e in result.content.split("\n") if e.startswith("var data=")]

		data = rows[0].replace('var data=', '')
		data = data.replace(';window.month={};window.year={};'.format(int(month), year), '')

		laoded = json.loads(data)
		
		key = '{}-{}'.format(year, month)
		
		print key
		
		DATA[key] = laoded
		

with open('data', 'w') as f:
	f.write(json.dumps(DATA))
"""

with open('data', 'r') as f:
	DATA = json.loads(f.read())

def date_parse(e):
	dt = datetime.datetime.fromtimestamp(int(e)/1000)
	return dt
	
	if dt.hour < 6 or dt.hour > 22:
		return dt
		
#t_w, t_m, t_e
sleeping_back = [
	#[-8, -15, -36] # Icefall 3
	[-3, -9, -28] # Icefall 2
	#[ 1, -4, -21] # Icefall 1
	#[ -7, -14, -35] # Serac 600
	#[ 2, -4, -21] # Serac 300
]

for _month in range(1, 13):
	
	_hour_data = {}
	_raw = []

	for key, value in DATA.items():
		print value.keys()
		
		data = [(date_parse(e['date']), e['temp']) for e in value['temp']]
		data = [e for e in data if e[0] is not None]
		
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
	
	t_w, t_m, t_e = sleeping_back[0]
	
	# Moving the extreme point between lowest and  extreme rating
	# t_e += (t_m - t_e) / 2

	_raw_t_w = [e for e in _raw if e[1] >= t_w]
	_raw_t_m = [e for e in _raw if t_w > e[1] >= t_m]
	_raw_t_e = [e for e in _raw if t_m > e[1] >= t_e]
	_raw_t_d = [e for e in _raw if t_e > e[1]]
	

	
	for _scatter, col in [(_raw_t_w, 'gx'), (_raw_t_m, 'yx'), (_raw_t_e, 'rx'), (_raw_t_d, 'kx')]:
		x = [e[0] for e in _scatter]
		y = [e[1] for e in _scatter]
		plt.plot(x, y, col)

	g = plt.boxplot(_temp_lists) #, whis=10)

	plt.xticks(range(1, 1+len(_temp_lists)), _hour_labels, rotation='vertical')
	plt.title(_month)
	plt.xlabel("Hours of the day (g=women, y=men, r=extrem, b=death)")
	plt.ylabel("Temperature boxpot")
	plt.savefig('./month_{}.png'.format(_month))

	#plt.show()

