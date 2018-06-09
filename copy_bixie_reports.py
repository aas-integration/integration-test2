import sys, os, traceback, itertools, tempfile
from os import walk
from shutil import copyfile

if __name__ == "__main__": 
  if len(sys.argv)<3:
    print "Requires input dir and ouput dir"
    sys.exit(0)
  html_names = []
  for dirpath, _ , filenames in os.walk(sys.argv[1]):
    for f in filenames:
      if f.endswith("index.html"):
        html_file = os.path.abspath(os.path.join(dirpath, f))
        if "bixie_report" in html_file:
          html_names += [html_file]
  for h in html_names:
    spath = h.split(os.sep)
    if len(spath)>4:
      copyfile(h, os.path.join(sys.argv[2], "{}.html".format(spath[-4])))
      print spath[-4]
