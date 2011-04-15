
# by Albert Zeyer, www.az2000.de
# code under GPLv3+

import sys

def parse_py_statement(line):
	state = 0
	curtoken = ""
	spaces = " \t\n"
	ops = ".,;:+-*/%&=(){}[]^<>"
	i = 0
	def _escape_char(c):
		if c == "n": return "\n"
		elif c == "t": return "\t"
		else: return c
	while i < len(line):
		c = line[i]
		i += 1
		if state == 0:
			if c in spaces: pass
			elif c in ops: yield ("op", c)
			elif c == "#": state = 6
			elif c == "\"": state = 1
			elif c == "'": state = 2
			else:
				curtoken = c
				state = 3
		elif state == 1: # string via "
			if c == "\\": state = 4
			elif c == "\"":
				yield ("str", curtoken)
				curtoken = ""
				state = 0
			else: curtoken += c
		elif state == 2: # string via '
			if c == "\\": state = 5
			elif c == "'":
				yield ("str", curtoken)
				curtoken = ""
				state = 0
			else: curtoken += c
		elif state == 3: # identifier
			if c in spaces + ops + "#\"'":
				yield ("id", curtoken)
				curtoken = ""
				state = 0
				i -= 1
			else: curtoken += c
		elif state == 4: # escape in "
			curtoken += _escape_char(c)
			state = 1
		elif state == 5: # escape in '
			curtoken += _escape_char(c)
			state = 2
		elif state == 6: # comment
			curtoken += c
	if state == 3: yield ("id", curtoken)
	elif state == 6: yield ("comment", curtoken)
	
def better_exchook(etype, value, tb):
	print >>sys.stderr, "EXCEPTION"
	print >>sys.stderr, 'Traceback (most recent call last):'
	try:
		import linecache
		limit = None
		if hasattr(sys, 'tracebacklimit'):
			limit = sys.tracebacklimit
		n = 0
		_tb = tb
		while _tb is not None and (limit is None or n < limit):
			f = _tb.tb_frame
			lineno = _tb.tb_lineno
			co = f.f_code
			filename = co.co_filename
			name = co.co_name
			print >>sys.stderr, '  File "%s", line %d, in %s' % (filename,lineno,name)
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			if line:
				line = line.strip()
				print >>sys.stderr, '    line:', line
				print >>sys.stderr, '    locals:'
				for tokentype, token in parse_py_statement(line):
					if tokentype != "id": continue
					print >>sys.stderr, '     ', token, "=",
					tokenvalue = "<not found>"
					if token in f.f_locals: tokenvalue = "<local> " + repr(f.f_locals[token])
					elif token in f.f_globals: tokenvalue = "<global> " + repr(f.f_globals[token])
					elif token in f.f_builtins: tokenvalue = "<builtin> " + repr(f.f_builtins[token])
					print >>sys.stderr, tokenvalue
			_tb = _tb.tb_next
			n += 1

	except Exception, e:
		print >>sys.stderr, "ERROR: cannot get more detailed exception info because:"
		import traceback
		for l in traceback.format_exc().split("\n"): print >>sys.stderr, "  ", l
		print >>sys.stderr, "simple traceback:"
		traceback.print_tb(tb)

	import types
	def _some_str(value):
		try: return str(value)
		except: return '<unprintable %s object>' % type(value).__name__
	def _format_final_exc_line(etype, value):
		valuestr = _some_str(value)
		if value is None or not valuestr:
			line = "%s" % etype
		else:
			line = "%s: %s" % (etype, valuestr)
		return line
	if (isinstance(etype, BaseException) or
		isinstance(etype, types.InstanceType) or
		etype is None or type(etype) is str):
		print >>sys.stderr, _format_final_exc_line(etype, value)
	else:
		print >>sys.stderr, _format_final_exc_line(etype.__name__, value)

	debug = False
	try:
		import os
		debug = int(os.environ["DEBUG"]) != 0
	except: pass
	if debug:
		from IPython.Shell import IPShellEmbed
		ipshell = IPShellEmbed()
		ipshell()

sys.excepthook = better_exchook

import codecs # utf8
import os, os.path

infilename = os.path.expanduser("~/Music/iTunes/iTunes Music Library.xml")
infile = codecs.open(infilename, "r", "utf-8")

foo
