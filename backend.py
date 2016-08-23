import os, sys
import common

def add_project_to_corpus(project, corpus_kernel_file_handle, cluster_json=None):
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

  """ run graph kernel computation """
  project_dir = common.get_project_dir(project)

  for out_dir in common.DOT_DIR[project]:
    kernel_file_path = common.get_kernel_path(project, out_dir)

    if cluster_json:
      graph_kernel_cmd = ['python',
                          common.get_simprog('precompute_kernel.py'),
                          project_dir,
                          kernel_file_path,
                          cluster_json
                          ]
      common.run_cmd(graph_kernel_cmd)
    else:
      graph_kernel_cmd = ['python',
                          common.get_simprog('precompute_kernel.py'),
                          project_dir,
                          kernel_file_path
                          ]
      common.run_cmd(graph_kernel_cmd)
    print 'Generated kernel file for {0} in {1}.'.format(project, kernel_file_path)
    with open(kernel_file_path, "r") as fi: corpus_kernel_file_handle.write(fi.read())

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
