import time
import calendar
import json
import math

from os.path import join as pjoin


NS = ''
template = '$(document).ready(function(){{$.plot($("{query}"),{data},{config});}});'


def convert_path_to_fn(path):
	return "-".join(path.split('/')[:-1])


def get_date_in_ms(date, pattern="%Y%m%d"):
	return calendar.timegm(time.strptime(date[:8], pattern)) * 1000


def regression_graphs(root, dir, query):
	prefix = pjoin(dir, convert_path_to_fn(root.getchildren()[0].attrib['file']))

	print("Generating", prefix + '-bugs.js')
	f = open(prefix + '-bugs.js', 'w')
	f.write(generate_regression_bugs_stacked(root, False, query))
	f.close()
	
	print("Generating", prefix + '-bugs-percent.js')
	f = open(prefix + '-bugs-percent.js', 'w')
	f.write(generate_regression_bugs_stacked(root, True, query))
	f.close()

def goldstandard_graphs(root, dir, query):
	prefix = pjoin(dir, convert_path_to_fn(root.getchildren()[0].attrib['file']))

	print("Generating", prefix + '-general.js')
	f = open(prefix + '-general.js', 'w')
	f.write(generate_goldstandard_general(root, query))
	f.close()
	

def generate_goldstandard_general(root, query="#flotchart"):
	precision = {
		"data": [],
		"label": "Precision"
	}

	recall = {
		"data": [],
		"label": "Recall"
	}

	accuracy = {
		"data": [],
		"label": "Accuracy"
	}

	config = {
		"xaxis": {
			"mode": "time"
		},
		"yaxis": {
			"max": 100,
			"min": 0
		},
		"series": {
			"lines": {
				"show": True,
			}
		}
	}

	for test in root.getiterator(NS + 'test'):
		header = test.find("header")
		date = get_date_in_ms(header.find("date").text.split('-')[0])
		
		words = int(test.find(NS + "words").text)
		correct = int(test.find(NS + "correct").text)
		false_correct = int(test.find(NS + "false-correct").text)
		error = int(test.find(NS + "error").text)
		false_error = int(test.find(NS + "false-error").text)
	
		if error + false_error != 0:
			res = error / (error + false_error) * 100
			precision['data'].append((date, res))

		if error + false_correct != 0:
			res = error / (error + false_correct) * 100
			recall['data'].append((date, res))

		if words != 0:
			res = (error + correct) / words * 100
			accuracy['data'].append((date, res))
	

	precision['data'].sort()
	recall['data'].sort()
	accuracy['data'].sort()

	data = json.dumps([precision, recall, accuracy])
	config = json.dumps(config)

	return template.format(query=query, data=data, config=config)


def generate_regression_bugs_stacked(root, percentage=False, query="#flotchart"):
	solved = {
		"data": [],
		"color": "green",
		"label": "Solved"
	}
	unsolved = {
		"data": [],
		"color": "red",
		"label": "Unsolved"
	}

	config = {
		"xaxis": {
			"mode": "time"
		},
		"series": {
			"stack": True,
			"lines": {
				"show": True,
				"fill": True
			}
		}
	}

	if percentage:
		config['yaxis'] = {'max': 100}

	for test in root.getiterator(NS + 'test'):
		header = test.find("header")
		date = get_date_in_ms(header.find("date").text.split('-')[0])
		
		correct = int(test.find(NS + "correct").text)
		false_correct = int(test.find(NS + "false-correct").text)
		error = int(test.find(NS + "error").text)
		false_error = int(test.find(NS + "false-error").text)
	
		if percentage:
			total = correct + false_correct + error + false_error
			if total != 0:	
				correct = correct / total * 100
				false_correct = false_correct / total * 100
				error = error / total * 100
				false_error = false_error / total * 100

		solv = correct + error
		unsolv = false_correct + false_error
		
		if percentage:
			unsolv += 1 # make the line go away

		solved['data'].append((date, solv))
		unsolved['data'].append((date, unsolv))

	solved['data'].sort()
	unsolved['data'].sort()
	data = json.dumps([solved, unsolved])
	config = json.dumps(config)

	return template.format(query=query, data=data, config=config)


testtypes = {
	"regression": regression_graphs,
	"goldstandard": goldstandard_graphs
}
