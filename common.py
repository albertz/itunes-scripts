
# by Albert Zeyer, www.az2000.de
# code under GPLv3+

import sys
from better_exchook import better_exchook
sys.excepthook = better_exchook

import codecs # utf8
import os, os.path

libraryXmlFile = codecs.open(os.path.expanduser("~/Music/iTunes/iTunes Music Library.xml"), "r", "utf-8")

def parse_xml(stream):
	state = 0
	spaces = " \t\n"
	data = ""
	node = ""
	nodeprefix = ""
	nodepostfix = ""
	nodeargs = []
	while True:
		c = stream.read(1)
		if c == "": break

		oldstate = state
		if state == 0:
			if c in spaces: pass
			elif c == "<": state = 1
			else: data += c
		elif state == 1: # in node
			if c in spaces:
				if node == "": pass
				else: state = 2
			elif c in "!/?":
				if node == "": nodeprefix += c
				else: nodepostfix += c
			elif c == ">": state = 0
			elif c == "\"": state = 3
			else: node += c
		elif state == 2: # in nodeargs
			if c in spaces: pass
			elif c == ">": state = 0
			elif c == "\"": state = 3
			elif c == "/": nodepostfix += c
			else:
				nodeargs.append(c)
				state = 4
		elif state == 3: # in nodearg str
			if c == "\\": state = 5
			elif c == "\"": state = 2
			else: pass # we dont store it right now
		elif state == 4: # in nodearg
			if c in spaces: state = 2
			elif c == ">": state = 0
			elif c == "\"": state = 3
			elif c == "/": nodepostfix += c
			else: nodeargs[-1] += c
		elif state == 5: # in escaped nodearg str
			# we dont store it right now
			state = 3

		if oldstate > 0 and state == 0:
			yield nodeprefix + node + nodepostfix, nodeargs, data
			nodeprefix, node, nodepostfix = "", "", ""
			nodeargs = []
			data = ""


plistPrimitiveTypes = {"integer": int, "string": str, "date": str}

def parse_plist_content(xmlIter, prefix):
	for node, nodeargs, data in xmlIter:
		if node == "dict":
			for entry in parse_plist_dictContent(xmlIter, prefix): yield entry
		elif node in plistPrimitiveTypes:
			for entry in parse_plist_primitiveContent(xmlIter, prefix, node): yield entry
		elif node == "true/":
			yield prefix, True
		elif node == "false/":
			yield prefix, False
		else:
			print >>sys.stderr, "didnt expected node", repr(node), "in content in prefix", repr(prefix)
		break
		
def parse_plist_primitiveContent(xmlIter, prefix, contentType):
	for node, nodeargs, data in xmlIter:
		if node == "/" + contentType:
			yield prefix, plistPrimitiveTypes[contentType](data)
		else:
			print >>sys.stderr, "didnt expected node", repr(node), "in primitive content", repr(contentType), "in prefix", repr(prefix)
		break
		
# dict in plist is a list of key/value pairs
def parse_plist_dictContent(xmlIter, prefix):
	lastkey = None
	for node, nodeargs, data in xmlIter:
		if node == "key": pass
		elif node == "/key":
			if lastkey is not None: print >>sys.stderr, "expected value after key in dict content in prefix", repr(prefix)
			lastkey = data
			for entry in parse_plist_content(xmlIter, prefix + [lastkey]):
				yield entry
			lastkey = None
		elif node == "/dict": break
		else:
			print >>sys.stderr, "didn't expected node", repr(node), "in dict content in prefix", repr(prefix)
			
def parse_plist(xmlIter):
	for node, nodeargs, data in xmlIter:
		if node == "plist":
			for entry in parse_plist_content(xmlIter, []): yield entry

for entry in parse_plist(parse_xml(libraryXmlFile)):
	print entry
