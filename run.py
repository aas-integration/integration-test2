import os,sys,common
import fetch

def main():
  if not os.path.exists(common.CORPUS_DIR) or not os.path.exists(common.LIBS_DIR):
    print "Please run python fetch.py first to fetch the corpus and/or necessary tools."
    sys.exit(1)
    return

  print "Running analysis on corpus."
  if '--with-daikon' in sys.argv:
    tools = ['dyntrace']
  else:
    tools = ['randoop']

  for project in common.get_project_list():
    print "Cleaning {}".format(project)
    common.clean_project(project)
    print "Analyzing {}".format(project)
    common.run_dljc(project, tools)

if __name__ == "__main__":
  main()
