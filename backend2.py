import os, sys
import common
import argparse
from simprog import Similarity

def generate_graphs(project):
  #print "STARTED CLEANING PROJECT"
  #common.clean_project(project)
  #print "FINISHED CLEANING PROJECT"

  """Run dljc
  Compile test sources
  Generate program graphs using prog2dfg
  Precompute graph kernels that are independent of ontology stuff
  """
  print("Generating graphs for {0}".format(project))
  common.run_dljc(project,
                  ['graphtool'],
                  ['--graph-jar', common.get_jar('prog2dfg.jar')])

def generate_project_kernel(project, cluster_json=None):
  """ run graph kernel computation """
  
  project_dir = common.get_project_dir(project)
  out_dir = common.DOT_DIR[project]
  kernel_file_path = common.get_kernel_path(project, out_dir)
  
  if cluster_json:
    print("Using clustering output for node relabeling:")
    graph_kernel_cmd = ['python',
                        common.get_simprog('precompute_kernel.py'),
                        project_dir,
                        kernel_file_path,
                        cluster_json
                        ]
    common.run_cmd(graph_kernel_cmd, True)
  else:
    graph_kernel_cmd = ['python',
                        common.get_simprog('precompute_kernel.py'),
                        project_dir,
                        kernel_file_path
                        ]
    common.run_cmd(graph_kernel_cmd, True)
    
  print("Generated kernel file for {0} in {1}.".format(project, kernel_file_path))

def compute_all_pairs_similarity(result_dir):
  #sim.graphs has all the method names
  #sim.ylabels has all the indices of the projects
  sim = Similarity()
  counter = 0
  for (yl,project) in enumerate(common.LIMITED_PROJECT_LIST):
    ind_file = os.path.join(result_dir, project+".txt")
    project_dir = common.get_project_dir(project)
    out_dir = common.DOT_DIR[project]
    project_kernel_file_path = common.get_kernel_path(project, out_dir)
    prog_count = sim.read_graph_kernels(project_kernel_file_path, yl)
    with open(ind_file, "w") as indf: 
        for i in range(counter, counter+prog_count):          
          indf.write(sim.graphs[i] + " " + str(i) + "\n")
    counter += counter + prog_count
  # pair-wise similarity matrix
  kernel_matrix = sim.compute_wl_kernel_matrix()
  score_file = os.path.join(result_dir, "score.txt")
  with open(score_file, "w") as scrf:
    for i in range(len(sim.graphs)):
      scrf.write(" ".join(kernel_matrix[i]))
      scrf.write("\n")

def main():
  
  project_list = common.LIMITED_PROJECT_LIST

  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--cluster", type=str, help="path to the json file that contains clustering information")
  parser.add_argument("-g", "--graph", action="store_true", help="set to regenerate graphs from the programs")
  parser.add_argument("-d", "--dir", type=str, required=True, help="directory to store the similarity results")
  args = parser.parse_args()

  for project in project_list:
    if args.graph:
      generate_graphs(project)
    generate_project_kernel(project, args.cluster)

  common.mkdir(args.dir)
  compute_all_pairs_similarity(args.dir)

if __name__ == '__main__':
  main()
