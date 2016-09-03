import os, sys
import common

def add_project_to_corpus(project, corpus_kernel_file_handle, cluster_json=None):
  #print "STARTED CLEANING PROJECT"
  #common.clean_project(project)
  #print "FINISHED CLEANING PROJECT"

  """Run dljc
  Compile test sources
  Generate program graphs using prog2dfg
  Precompute graph kernels that are independent of ontology stuff
  """
  #common.run_dljc(project,
  #                ['graphtool'],
  #                ['--graph-jar', common.get_jar('prog2dfg.jar')])

  """ run graph kernel computation """
  
  project_dir = common.get_project_dir(project)

  for out_dir in common.DOT_DIR[project]:
    kernel_file_path = common.get_kernel_path(project, out_dir)

    if cluster_json:
      print "Using clustering output for node relabeling:"
      graph_kernel_cmd = ['python',
                          common.get_simprog('precompute_kernel.py'),
                          project_dir,
                          kernel_file_path,
                          cluster_json
                          ]
      output = common.run_cmd(graph_kernel_cmd)
      print output
    else:
      graph_kernel_cmd = ['python',
                          common.get_simprog('precompute_kernel.py'),
                          project_dir,
                          kernel_file_path
                          ]
      output = common.run_cmd(graph_kernel_cmd)
      print output
    print 'Generated kernel file for {0} in {1}.'.format(project, kernel_file_path)
    with open(kernel_file_path, "r") as fi: corpus_kernel_file_handle.write(fi.read())

def main():
  
  ck_file = sys.argv[1]  
  kf = open(ck_file, "w")

  to_remove = sys.argv[2]
  
  cluster_json = None
  if len(sys.argv)==4:
    cluster_json = sys.argv[3]
  
  project_list = ["dyn4j", "jreactphysics3d", "jbox2d", "react", "jmonkeyengine"]
  project_list.remove(to_remove)

  for project in project_list:
  #for project in common.get_project_list():
    print "Analyzing {}:".format(project)
    add_project_to_corpus(project, kf, cluster_json)
  kf.close()

if __name__ == '__main__':
  main()
