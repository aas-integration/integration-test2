import os, sys
import common
import inv_check


def add_project_to_corpus(project, corpus_kernel_file_handle, cluster_json=None):
  print "STARTED CLEANING PROJECT"
  common.clean_project(project)
  print "FINISHED CLEANING PROJECT"

  """Run dljc
  run randoop and daikon.
  """
  print "Starting Randoop+Daikon"
  common.run_dljc(project,
                  ['dyntrace'],
                  ['--dyntrace-libs', common.LIBS_DIR])

  inv_check.run_daikon_on_dtrace_file(get_dtrace_file_for_project(project))

def get_dtrace_file_for_project(project):
  if project == "TODO":
    return os.path.join(common.WORKING_DIR, 'inv_check/test.dtrace.gz')

  dtrace_path = os.path.join(common.CORPUS_DIR,
                             project,
                             common.DLJC_OUTPUT_DIR,
                             'RegressionTestDriver.dtrace.gz')
  if os.path.exists(dtrace_path):
    return dtrace_path
  else:
    return None


def main():
  cluster_json = None
  if len(sys.argv)==2:
    cluster_json = sys.argv[1]

  kf = open("corpus_kernel.txt", "w")
  for project in ["dyn4j", "jreactphysics3d"]:
  #for project in common.get_project_list():
    print "Analyzing {}:".format(project)
    add_project_to_corpus(project, kf)
  kf.close()

if __name__ == '__main__':
  main()
