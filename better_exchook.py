
# by Albert Zeyer, www.az2000.de
# code under GPLv3+
# 2011-04-15

# This is a simple replacement for the standard Python exception handler (sys.excepthook).
# In addition to what the standard handler does, it also prints all referenced variables
# (no matter if local, global or builtin) of the code line of each stack frame.
# See below for some examples and some example output.

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

def grep_full_py_identifiers(tokens):
	tokens = list(tokens)
	i = 0
	pykeywords = set(["for","in","while","print","continue","break","if","else","elif","yield","def","class","try","except","import","pass","lambda"])
	while i < len(tokens):
		tokentype, token = tokens[i]
		i += 1
		if tokentype != "id": continue
		while i+1 < len(tokens) and tokens[i] == ("op", ".") and tokens[i+1][0] == "id":
			token += "." + tokens[i+1][1]
			i += 2
		if token == "": continue
		if token in pykeywords: continue
		if token[0] in ".0123456789": continue
		yield token


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
		def _resolveIdentifier(namespace, id):
			id = id.split(".")
			obj = namespace[id[0]]
			for part in id[1:]:
				obj = getattr(obj, part)
			return obj
		def _trySet(old, func):
			if old is not None: return old
			try: return func()
			except: return old
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
				alreadyPrintedLocals = set()
				for token in grep_full_py_identifiers(parse_py_statement(line)):
					if token in alreadyPrintedLocals: continue
					print >>sys.stderr, '     ', token, "=",
					tokenvalue = None
					tokenvalue = _trySet(tokenvalue, lambda: "<local> " + repr(_resolveIdentifier(f.f_locals, token)))
					tokenvalue = _trySet(tokenvalue, lambda: "<global> " + repr(_resolveIdentifier(f.f_globals, token)))
					tokenvalue = _trySet(tokenvalue, lambda: "<builtin> " + repr(_resolveIdentifier(f.f_builtins, token)))
					tokenvalue = tokenvalue or "<not found>"
					print >>sys.stderr, tokenvalue
					alreadyPrintedLocals.add(token)
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

if __name__ == "__main__":
	# some examples
	# this code produces this output: https://gist.github.com/922622
	
	try:
		x = {1:2, "a":"b"}
		def f():
			y = "foo"
			x, 42, sys.stdin.__class__, sys.exc_info, y, z
		f()
	except:
		better_exchook(*sys.exc_info())

	try:
		f = lambda x: None
		f(x, y)
	except:
		better_exchook(*sys.exc_info())

	# use this to overwrite the global exception handler
	sys.excepthook = better_exchook
	# and fail
	finalfail(sys)
