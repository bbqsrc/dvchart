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


def get_state(expected, status):
	state = None
	if expected is None and status == "SplErr":
		state = "false-error"

	elif expected is None and status == "SplCor":
		state = "correct"

	elif expected is not None and status == "SplCor":
		state = "false-correct"

	elif expected is not None and status == "SplErr":
		state = "error"
	return state


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

	name = prefix + '-suggestions-percentage'
	print("Generating", name+'.js')
	f = open(name+'.js', 'w')
	f.write(generate_goldstandard_suggestions(name.split('/')[-1], root, percentage=True))
	f.close()

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


def typos_graphs(root, dir):
	prefix = pjoin(dir, convert_path_to_fn(root.getchildren()[0].attrib['file']))

	name = prefix + '-suggestions'
	print("Generating", name+'.js')
	f = open(name+'.js', 'w')
	f.write(generate_goldstandard_suggestions(name.split('/')[-1], root, True))
	f.close()
	
	name = prefix + '-suggestions-percentage'
	print("Generating", name+'.js')
	f = open(name+'.js', 'w')
	f.write(generate_goldstandard_suggestions(name.split('/')[-1], root, percentage=True))
	f.close()
	
	name = prefix + '-general'
	print("Generating", name+'.js')
	f = open(name+'.js', 'w')
	f.write(generate_goldstandard_general(name.split('/')[-1], root))
	f.close()


def generate_goldstandard_suggestions(name, root, typos=False, percentage=False):
	pairs = [
		("1", "#007700"),
		("2", "#009900"),
		("3", "#00BB00"),
		("4", "#00DD00"),
		("5", "#00FF00"),
		("lower-than-5", "yellow"),
		("no-suggestions", "orange"),
		("incorrect-only", "red")
	]
	
	if typos:
		pairs.append(("false-errors", "black"))
	
	config = {
		"legend": {
			"position": "nw"
		},
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

	out = defaultdict(set)
	for test in root.getiterator(NS + 'test'):
		header = test.find("header")
		date = get_date_in_ms(header.find("date").text.split('-')[0])
		
		positions = get_positions(test.find('edit-dists'))
		if not percentage:
			for k, v in positions.items():
				out[k].add((date, v))
		
			if typos:
				false_errors = test.find("false-error").text
				out['false-errors'].add((date, false_errors))
		else:
			total = 0
			for v in positions.values():
				total += int(v)
			
			for k, v in positions.items():
				out[k].add((date, "%.2f" % (int(v) / total * 100)))
			
			if typos:
				false_errors = test.find("false-error").text
				out['false-errors'].add((date, "%.2f" % (int(false_errors) / total * 100)))
				

	results = []
	for label, colour in pairs:
		o = OrderedDict()
		o['label'] = label
		o['color'] = colour
		o['data'] = sorted(list(out.get(label, [])))
		if len(o['data']) > 0:
			results.append(o)

	data = json.dumps(results)
	config = json.dumps(config)

	return templates['simple'].format(prop=name, data=data, config=config)


def generate_goldstandard_general(name, root):
	precision = {
		"data": set(),
		"label": "Precision"
	}

	recall = {
		"data": set(),
		"label": "Recall"
	}

	accuracy = {
		"data": set(),
		"label": "Accuracy"
	}

	config = {
		"legend": {
			"position": "nw"
		},
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
			precision['data'].add((date, res))

		if error + false_correct != 0:
			res = error / (error + false_correct) * 100
			recall['data'].add((date, res))

		if words != 0:
			res = (error + correct) / words * 100
			accuracy['data'].add((date, res))
	

	precision['data'] = sorted(list(precision['data']))
	recall['data'] = sorted(list(recall['data']))
	accuracy['data'] = sorted(list(accuracy['data']))

	data = json.dumps([precision, recall, accuracy])
	config = json.dumps(config)

	return templates['simple'].format(prop=name, data=data, config=config)


def generate_regression_bugs_stacked(name, root, percentage=False):
	solved = {
		"data": set(),
		"color": "green",
		"label": "Solved"
	}

	partly_solved = {
		"data": set(),
		"color": "orange",
		"label": "Partially Solved"
	}

	unsolved = {
		"data": set(),
		"color": "red",
		"label": "Unsolved"
	}

	config = {
		"legend": {
			"position": "nw"
		},
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
		
		'''
		correct = 0
		false_correct = 0
		error = 0
		false_error = 0
		'''
		bugs = Counter()

		for bug in test.find('bugs').getiterator(NS + "bug"):
			solved_node = bug.find("solved")
			if solved_node is not None:
				solved_node = int(solved_node.text)
			else:
				solved_node = 0
			
			unsolved_node = bug.find("unsolved")
			if unsolved_node is not None:
				unsolved_node = int(unsolved_node.text)
			else:
				unsolved_node = 0
			
			print(test.attrib['file'], bug.attrib['id'], solved_node, unsolved_node)
			total = solved_node + unsolved_node
			solved_pc = solved_node / total * 100
			unsolved_pc = unsolved_node / total * 100

			if solved_pc == 100:
				bugs['solved'] += 1

			elif solved_pc >= 80:
				bugs['partial'] += 1

			else:
				bugs['unsolved'] += 1
				
			'''
			correct += int(bug.find(NS + "correct").text)
			false_correct += int(bug.find(NS + "false-correct").text)
			error += int(bug.find(NS + "error").text)
			false_error += int(bug.find(NS + "false-error").text)
			'''
		
		print(list(bugs.values()))
		if sum(bugs.values()) == 0:
			continue

		if percentage:
			total = sum(bugs.values())
			bugs['solved'] = "%.2f" % (bugs['solved'] / total * 100)
			bugs['unsolved'] = "%.2f" % (bugs['unsolved'] / total * 100)
			bugs['partial'] = "%.2f" % (bugs['partial'] / total * 100)

			'''
			total = correct + false_correct + error + false_error
			if total != 0:	
				correct = correct / total * 100
				false_correct = false_correct / total * 100
				error = error / total * 100
				false_error = false_error / total * 100
			'''
	
		'''
		solv = correct + error
		unsolv = false_correct + false_error
		
		if percentage:
			unsolv += 1 # make the line go away
		'''

		solved['data'].add((date, bugs['solved']))
		unsolved['data'].add((date, bugs['unsolved']))
		partly_solved['data'].add((date, bugs['partial']))

	solved['data'] = sorted(list(solved['data']))
	unsolved['data'] = sorted(list(unsolved['data']))
	partly_solved['data'] = sorted(list(partly_solved['data']))
	
	data = json.dumps([solved, partly_solved, unsolved])
	config = json.dumps(config)

	return templates['simple'].format(prop=name, data=data, config=config)


flottypes = {
	"regression": regression_graphs,
	"goldstandard": goldstandard_graphs,
	"typos": typos_graphs
}



def RegressionDict(results):
	c = {}
	dists = {}
	
	for word in results.getiterator("word"):
		bug = word.find("bug")
		if bug is None:
			continue
		
		bug = bug.text
		#c[bug]['edit-dists'] = {}
		
		expected = word.find("expected")
		status = word.find("status")
		if status is not None:
			status = status.text
		
		'''
		edit_dist = word.find("edit_dist")
		if edit_dist is not None:
			edit_dist = edit_dist.text

		position = word.find("position")
		if position is not None:
			position = position.text
		
		suggestions = word.find("suggestions")
		if suggestions is not None:
			suggestions = int(suggestions.attrib.get("count"))
		'''

		state = get_state(expected, status)
		if state is None:
			continue
		
		c[bug] = Counter()

		if state.startswith("false"):
			c[bug]['unsolved'] += 1

		elif state in ("error", "correct"):
			c[bug]['solved'] += 1

		'''
		if state == "error":
			if edit_dist is not None:
				dist = edit_dist
			else:
				dist = '0'

			if not c[bug]['edit-dists'].get(dist):
				c[bug]['edit-dists'][dist] = Counter()
			c[bug]['edit-dists'][dist]['@count'] += 1

			pos = int(position)
			if pos == 0:
				if suggestions > 0:
					c[bug]['edit-dists'][dist]['incorrect-only'] += 1
				else:
					c[bug]['edit-dists'][dist]['no-suggestions'] += 1
			
			elif pos > 5:
				c[bug]['edit-dists'][dist]['lower-than-5'] += 1

			else:
				c[bug]['edit-dists'][dist][position] += 1

		if state is not None:
			c[bug][state] += 1
		c[bug]['words'] += 1
		'''
	return c


def GoldstandardDict(results):
	c = Counter()
	dists = {}
	
	for word in results.getiterator("word"):
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
		
		state = get_state(expected, status)
		
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

def RegressionElement(fn):
	root = etree.parse(fn).getroot()
	header = root.find("header")
	results = root.find("results")

	if header is None or results is None:
		return

	c = RegressionDict(results)
	stats_xml = Element("test", file=fn)
	stats_xml.append(deepcopy(header))
	
	bugs_element = SubElement(stats_xml, "bugs")
	for bug, v in c.items():
		# workaround a bug with the data itself (search 559)
		if v['solved'] == v['unsolved'] == 0:
			continue
		
		bug_element = SubElement(bugs_element, "bug", id=bug)
		SubElement(bug_element, "solved").text = str(v['solved'])
		SubElement(bug_element, "unsolved").text = str(v['unsolved'])
		#SubElement(bug_element, "words").text = str(v['words'])
		#SubElement(bug_element, "correct").text = str(v['correct'])
		#SubElement(bug_element, "false-correct").text = str(v['false-correct'])
		#SubElement(bug_element, "error").text = str(v['error'])
		#SubElement(bug_element, "false-error").text = str(v['false-error'])
		
		'''
		distkeys = sorted(v['edit-dists'].keys(), key=str)
		dists = SubElement(bug_element, "edit-dists")

		for key in distkeys:
			d = v['edit-dists'][key]
			el = SubElement(dists, "edit-dist", count=str(d['@count']), value=key)
	
			poskeys = sorted(d.keys(), key=str)
			poskeys.remove('@count')
			for pkey in poskeys:
				SubElement(el, 'position', value=str(pkey)).text = str(d[pkey])
		'''
	
	return stats_xml


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
	"regression": RegressionElement,
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

def generate_test_html(dir):
	tmpl = """<!DOCTYPE html>
<html>
<head>
<title>dvchart test page</title>

<style type="text/css">
.chart {
	height: 600px;
	width: 800px;
}
</style>

<script src="js/jquery-1.6.4.js" type="text/javascript"></script>
<script src="js/jquery.flot.min.js" type="text/javascript"></script>
<script src="js/jquery.flot.stack.min.js" type="text/javascript"></script>

%s

<script type="text/javascript">
$(document).ready(function() {
	for (var prop in dvchart) {
		$("<h1>"+prop+"</h1>").appendTo($("#container"));
		$("<div id='"+prop+"' class='chart'></div>").appendTo($("#container"));
		dvchart[prop]('#'+prop);
	}
});
</script>

</head>
<body>
<div id='container'></div>
</body>
</html>
"""
	flist = []
	for fn in os.listdir(dir):
		flist.append("<script src='%s'></script>" % fn)
	f = open(pjoin(dir, "index.html"), 'w')
	f.write(tmpl % "\n".join(flist))
	f.close()
	print("Generated index.html")
	

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
		if fn not in existlist and not 'latest' in fn\
		and not 'previous' in fn:
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
	

def cli():
	if len(sys.argv) >= 3:
		import datetime
		
		start = datetime.datetime.now()
		x = generate_output(sys.argv[1])
		end = datetime.datetime.now()
		print("Time elapsed:", (end - start).total_seconds())
		generate_js_from_xml(x, sys.argv[2])
		generate_test_html(sys.argv[2])
	else:
		print('Usage:', sys.argv[0], '[datadir]', '[jsdir]')


if __name__ == "__main__":
	cli()
