#!/usr/bin/python

# by Albert Zeyer, www.az2000.de
# code under GPLv3+

import common
import urllib
import re

for song in common.librarySongsIter:
	rating = song["Rating"]
	if rating is None: continue # print only songs with any rating set
	fn = song["Location"]
	fn = urllib.unquote(fn)
	fn = re.sub("^file://(localhost)?", "", fn)
	print rating, repr(fn)

