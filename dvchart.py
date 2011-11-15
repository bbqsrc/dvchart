from collections import OrderedDict, Counter, defaultdict
from copy import deepcopy
from glob import glob
from multiprocessing import Process, Queue, cpu_count
from os.path import join as pjoin
from queue import Empty
from xml.etree.ElementTree import Element, SubElement

import argparse
import calendar
import json
import math
import os, os.path
import sys
import time
import xml.etree.ElementTree as etree

__version__ = "0.1"

NS = ''
#templates['simple'] = '$(document).ready(function(){{$.plot($("{query}"),{data},{config});}});'
templates = {
	"simple": 'var dvchart=dvchart||{{}};dvchart["{prop}"]=function(x){{$.plot($(x),{data},{config});}};'
}


def convert_path_to_fn(path):
	return "-".join(path.split('/')[:-1])


def get_date_in_ms(date, pattern="%Y%m%d"):
	return calendar.timegm(time.strptime(date[:8], pattern)) * 1000


def get_positions(edit_dists):
	c = Counter()
	for pos in edit_dists.getiterator("position"):
		c[pos.attrib['value']] += int(pos.text)
	return c


def regression_graphs(root, dir):
	prefix = pjoin(dir, convert_path_to_fn(root.getchildren()[0].attrib['file']))

	name = prefix + '-bugs'
	print("Generating", name+'.js')
	f = open(name+'.js', 'w')
	f.write(generate_regression_bugs_stacked(name.split('/')[-1], root, False))
	f.close()
	
	name = prefix + '-bugs-percent'
	print("Generating", name+'.js')
	f = open(name+'.js', 'w')
	f.write(generate_regression_bugs_stacked(name.split('/')[-1], root, True))
	f.close()


def goldstandard_graphs(root, dir):
	prefix = pjoin(dir, convert_path_to_fn(root.getchildren()[0].attrib['file']))

	name = prefix + '-suggestions'
	print("Generating", name+'.js')
	f = open(name+'.js', 'w')
	f.write(generate_goldstandard_suggestions(name.split('/')[-1], root))
	f.close()
	
	name = prefix + '-general'
	print("Generating", name+'.js')
	f = open(name+'.js', 'w')
	f.write(generate_goldstandard_general(name.split('/')[-1], root))
	f.close()
	

def generate_goldstandard_suggestions(name, root):
	pairs = (
		("1", "#00FF00"),
		("2", "#00DD00"),
		("3", "#00BB00"),
		("4", "#009900"),
		("5", "yellow"),
		("lower-than-5", "orange"),
		("incorrect-only", "red"),
		("no-suggestions", "pink")
	)

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

	out = defaultdict(list)
	for test in root.getiterator(NS + 'test'):
		header = test.find("header")
		date = get_date_in_ms(header.find("date").text.split('-')[0])
		
		positions = get_positions(test.find('edit-dists'))

		for k, v in positions.items():
			out[k].append((date, v))

	results = []
	for label, colour in pairs:
		o = OrderedDict()
		o['label'] = label
		o['color'] = colour
		o['data'] = sorted(out.get(label, []))
		results.append(o)

	data = json.dumps(results)
	config = json.dumps(config)

	return templates['simple'].format(prop=name, data=data, config=config)


def generate_goldstandard_general(name, root):
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

	return templates['simple'].format(prop=name, data=data, config=config)


def generate_regression_bugs_stacked(name, root, percentage=False):
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

	return templates['simple'].format(prop=name, data=data, config=config)


flottypes = {
	"regression": regression_graphs,
	"goldstandard": goldstandard_graphs
}



def GoldstandardDict(results):
	c = Counter()
	dists = {}
	
	for word in results.getiterator("word"):
		#print(word.getchildren())
		state = None
		
		expected = word.find("expected")
		status = word.find("status")
		if status is not None:
			status = status.text
		
		edit_dist = word.find("edit_dist")
		if edit_dist is not None:
			edit_dist = edit_dist.text

		position = word.find("position")
		if position is not None:
			position = position.text
		
		suggestions = word.find("suggestions")
		if suggestions is not None:
			suggestions = int(suggestions.attrib.get("count"))

		if expected is None and status == "SplErr":
			state = "false-error"

		elif expected is None and status == "SplCor":
			state = "correct"

		elif expected is not None and status == "SplCor":
			state = "false-correct"

		elif expected is not None and status == "SplErr":
			state = "error"
		
		if state == "error":
			if edit_dist is not None:
				dist = edit_dist
			else:
				dist = '0'

			if not dists.get(dist):
				dists[dist] = Counter()
			dists[dist]['@count'] += 1

			pos = int(position)
			if pos == 0:
				if suggestions > 0:
					dists[dist]['incorrect-only'] += 1
				else:
					dists[dist]['no-suggestions'] += 1
			
			elif pos > 5:
				dists[dist]['lower-than-5'] += 1

			else:
				dists[dist][position] += 1

		if state is not None:
			c[state] += 1
		c['words'] += 1
	
	c['edit-dists'] = dists

	return c

'''
testtypes = {
	"goldstandard": GoldstandardElement,
	"regression": RegressionElement,
	"typos": TypoElement
}
'''

def TestElement(fn):
	root = etree.parse(fn).getroot()
	header = root.find("header")
	results = root.find("results")

	if header is None or results is None:
		return

	c = GoldstandardDict(results)
	stats_xml = Element("test", file=fn)
	stats_xml.append(deepcopy(header))
	
	SubElement(stats_xml, "words").text = str(c['words'])
	SubElement(stats_xml, "correct").text = str(c['correct'])
	SubElement(stats_xml, "false-correct").text = str(c['false-correct'])
	SubElement(stats_xml, "error").text = str(c['error'])
	SubElement(stats_xml, "false-error").text = str(c['false-error'])
	
	distkeys = sorted(c['edit-dists'].keys(), key=str)
	dists = SubElement(stats_xml, "edit-dists")

	for key in distkeys:
		d = c['edit-dists'][key]
		el = SubElement(dists, "edit-dist", count=str(d['@count']), value=key)

		poskeys = sorted(d.keys(), key=str)
		poskeys.remove('@count')
		for pkey in poskeys:
			SubElement(el, 'position', value=str(pkey)).text = str(d[pkey])
	
	return stats_xml


testtypes = {
	"goldstandard": TestElement,
	"regression": TestElement,
	"typos": TestElement
}


def generator_worker(inq, outq):
	for arg in iter(inq.get, 'STOP'):
		#print(arg)
		lang, speller, testtype, fn = tuple(arg.split('/'))
		
		if testtype in testtypes:
			outq.put((arg, testtypes[testtype](arg)))
		else:
			outq.put((arg, None))


def generate_output(dir):
	olddir = os.getcwd()
	parent = os.path.abspath(dir)

	os.chdir(parent)
	
	inq = Queue()
	outq = Queue()

	filelist = glob("*/*/*/*.xml")
	#stats = {}
	if os.path.exists(pjoin(dir, 'aggregated.xml')):
		stats = etree.parse(pjoin(dir, 'aggregated.xml')).getroot()
		if stats.attrib.get("version") != __version__:
			stats = Element("statistics", version=__version__)
	else:
		stats = Element("statistics", version=__version__)
	
	existlist = []
	for test in stats.findall('language/speller/tests/test'):
		existlist.append(test.attrib['file'])

	items = 0
	for fn in filelist:
		if fn not in existlist and not fn.startswith('latest') \
		and not fn.startswith('previous'):
			inq.put(fn)
			items += 1
	
	threads = []
	for i in range(cpu_count()):
		t = Process(target=generator_worker, args=(inq, outq))
		t.start()
		threads.append(t)
		inq.put("STOP")
	
	for i in range(items):
		d, data = outq.get()
		lang, speller, testtype, fn = tuple(d.split('/'))
		
		langnode = stats.findall('language[@value="%s"]' % lang)
		if len(langnode) > 0:
			langnode = langnode[0]
		else:
			langnode = SubElement(stats, 'language', value=lang)
		
		spellernode = langnode.findall('speller[@value="%s"]' % speller)
		if len(spellernode) > 0:
			spellernode = spellernode[0]
		else:
			spellernode = SubElement(langnode, 'speller', value=speller)
		
		testnode = spellernode.findall('tests[@value="%s"]' % testtype)
		if len(testnode) > 0:
			testnode = testnode[0]
		else:
			testnode = SubElement(spellernode, 'tests', value=testtype)

		print('[%s/%s] %s' % (i+1, items, d))
		
		if data is not None:
			testnode.append(data)
		
	print("Done!")
	os.chdir(olddir)
	
	f = open(pjoin(dir, "aggregated.xml"), 'wb')
	f.write(etree.tostring(stats))
	f.close()

	return stats


def generate_js_from_xml(root, outdir):
	try: os.makedirs(outdir)
	except: pass

	for language in root.getchildren():
		for speller in language.getchildren():
			for tests in speller.getchildren():
				testtype = tests.attrib['value']
				if testtype in flottypes:
					flottypes[testtype](tests, outdir)


def test():
	import datetime
	start = datetime.datetime.now()
	x = generate_output("/Users/brendan/Temporal/sjur")
	end = datetime.datetime.now()
	print("Time elapsed:", (end - start).total_seconds())
	generate_js_from_xml(x, "/Users/brendan/git/spexml/jsout")


def cli():
	if len(sys.argv) >= 3:
		import datetime
		
		start = datetime.datetime.now()
		x = generate_output(sys.argv[1])
		end = datetime.datetime.now()
		print("Time elapsed:", (end - start).total_seconds())
		generate_js_from_xml(x, sys.argv[2])
	else:
		print('Usage:', sys.argv[0], '[datadir]', '[jsdir]')


if __name__ == "__main__":
	cli()
