import os, sys
import common

def add_project_to_corpus(project):
  print "STARTED CLEANING PROJECT"
  common.clean_project(project)
  print "FINISHED CLEANING PROJECT"

  """Run dljc
  Compile test sources
  Generate program graphs using prog2dfg
  Precompute graph kernels that are independent of ontology stuff
  """
  common.run_dljc(project,
                  ['graphtool'],
                  ['--graph-jar', common.get_jar('prog2dfg.jar')])

def main():
  for project in ["dyn4j", "jreactphysics3d", "jbox2d", "react", "jmonkeyengine"]:
    print "Analyzing {}:".format(project)
    add_project_to_corpus(project)

if __name__ == '__main__':
  main()
