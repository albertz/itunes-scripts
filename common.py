
# by Albert Zeyer, www.az2000.de
# code under GPLv3+

import sys
from better_exchook import better_exchook
sys.excepthook = better_exchook

import codecs # utf8
import os, os.path

libraryXmlFile = codecs.open(os.path.expanduser("~/Music/iTunes/iTunes Music Library.xml"), "r", "utf-8")



