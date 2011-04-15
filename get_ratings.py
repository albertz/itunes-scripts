#!/usr/bin/python

# by Albert Zeyer, www.az2000.de
# code under GPLv3+

import common
import urllib

for song in common.librarySongsIter:
	rating = song["Rating"]
	if rating is None: continue # print only songs with any rating set
	fn = song["Location"]
	fn = urllib.unquote(fn)
	print repr(fn), rating

