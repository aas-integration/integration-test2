import os, sys
import common
import dot
import argparse
import json
from simprog import Similarity

def generate_graphs(project):
  """Run dljc
  Compile test sources
  Generate program graphs using prog2dfg
  Precompute graph kernels that are independent of ontology stuff
  """
  print("Generating graphs for {0}...".format(project))
  common.run_dljc(project,
                  ['graphtool'],
                  ['--graph-jar', common.get_jar('prog2dfg.jar'),
                   '--cache'])

def generate_dtrace(project):
  #TODO: set the out file to common.get_dtrace_file_for_project(project)
  common.run_dljc(project,
                  ['dyntrace'], ['--cache'])  

def gather_kernels(projects, corpus_kernel_file):
  print("Gathering kernels from projects {0}".format(",".join(projects)))
  with open(corpus_kernel_file, "w") as corpus_kernel_file_handle:
    for project in projects:
      project_dir = common.get_project_dir(project)
      out_dir = dot.dot_dirs(project)[0] # only consider the first one
      project_kernel_file_path = dot.get_kernel_path(project, out_dir)
      
      if os.path.isfile(project_kernel_file_path):
        with open(project_kernel_file_path, "r") as fi: 
            corpus_kernel_file_handle.write(fi.read())
      else:
        print("No kernel file find for project {0}.\n   {1} is not a file.".format(
          project,
          project_kernel_file_path
          ))
        sys.exit(0)

def generate_project_kernel(project, cluster_json=None):
  """ run graph kernel computation """
  
  project_dir = common.get_project_dir(project)

  print project,dot.dot_dirs(project)
  if not dot.dot_dirs(project):
    sys.exit(1)
  
  out_dir = dot.dot_dirs(project)[0]
    
  kernel_file_path = dot.get_kernel_path(project, out_dir)
  
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

def get_method_map(project_list):
  dot_to_method_map = {}
  for project in project_list:
    for output_dir in dot.dot_dirs(project): # first folder only for now
      method_file = dot.get_method_path(project, output_dir)
      if not os.path.isfile(method_file):
        print ("Cannot find method file for project {0} at {1}".format(project, method_file))
        sys.exit(0)

      with open(method_file, "r") as mf:
        content = mf.readlines()
        for line in content:
          line = line.rstrip()
          items = line.split('\t')
          method_name = items[0]
          method_dot = items[1]
          method_dot_path = dot.get_dot_path(project, output_dir, method_dot)          
          dot_to_method_map[method_dot_path] = method_name
  return dot_to_method_map

def check_similarity(project, result_file, kernel_file, corpus_dot_to_method_map, output_json_file, cluster_json=None, top_k=5):
  """ SUMMARY: use case of the user-driven functionality of PASCALI.
  """

  # fetch various method information from each project in the list
  # output_dir = dot.dot_dirs(project)[0]
  # method_file = dot.get_method_path(project, output_dir)

  # check similarity
  json_result = {}
  sim = Similarity()
  sim.read_graph_kernels(kernel_file)
  iter_num = 3 # number of iteration of the WL-Kernel method
  this_method_map = get_method_map([project])
  with open(result_file, "w") as fo:
    for dot_file in this_method_map.keys():
      dot_method = corpus_dot_to_method_map[dot_file]
      json_result[dot_method] = []
      print("Computing similar programs for {0}.".format(dot_method))
      result_program_list_with_score = sim.find_top_k_similar_graphs(dot_file, dot_file, top_k, iter_num, cluster_json)
      line = dot_file+":\n"
      for (dt, score) in result_program_list_with_score:
        line += "{} , {}\n".format(dt, score)
        if dt not in corpus_dot_to_method_map:
          print("{0} does not exist.".format(dt))
          sys.exit(0)
        tmp_dict = {}
        tmp_dict[corpus_dot_to_method_map[dt]] = score
        json_result[dot_method].append(tmp_dict)
        line += "\n"
        fo.write(line)
  with open(output_json_file, "w") as jo:
    jo.write(json.dumps(json_result, indent=4))

def main():
	
  parser = argparse.ArgumentParser()

  parser.add_argument("-c", "--cluster", type=str, help="path to the input json file that contains the clustering information.")
  parser.add_argument("-d", "--dir", type=str, required=True, help="output folder.")
  parser.add_argument("-p", "--plist", type=str, help="a comma separated list of projects to work with.")
  parser.add_argument("-k", "--kernel", action="store_true", help="recompute kernel vectors.")
  parser.add_argument("-g", "--graph", action="store_true", help="regenerate graphs.")
  parser.add_argument("-s", "--sim", type=str, help="specify a specific project for finding similar programs in the list of projects.")

  args = parser.parse_args()

  common.mkdir(args.dir)

  # determine which projects to consider
  project_list = common.get_project_list()
  if args.plist:
    arg_projects = args.plist.split(',')
    project_list = [project for project in project_list if project in arg_projects]

  # determine if need to regerenate graphs
  if args.graph:
    for project in project_list:
      generate_graphs(project)
    print("\n***** Done with generating graphs. *****\n") 

  # determine if need to recompute the kernel vectors
  if args.kernel:
    for project in project_list:
      generate_project_kernel(project, args.cluster)
    print("\n***** Done with computing kernels. *****\n")

  # check similarity
  dot_method_map = get_method_map(project_list)
  if args.sim:
    if args.sim not in project_list:
      print("Need to specify a project that is in the list of projects.")
    else:
      project = args.sim
      pl = list(project_list) # create a copy
      pl.remove(project)
      gather_kernels(pl, os.path.join(common.WORKING_DIR, args.dir, project+"_kernel.txt"))
      print("Computing similar programs for {0}:".format(project))
      result_file = os.path.join(common.WORKING_DIR, args.dir, project+"_result.txt")
      kernel_file = os.path.join(common.WORKING_DIR, args.dir, project+"_kernel.txt")
      json_file = os.path.join(common.WORKING_DIR, args.dir, project+"_result.json") 
      check_similarity(project, result_file, kernel_file, dot_method_map, json_file, args.cluster, min(5,len(project_list)))
  else:
    for project in project_list:
      pl = list(project_list) # create a copy
      pl.remove(project)
      gather_kernels(pl, os.path.join(common.WORKING_DIR, args.dir, project+"_kernel.txt"))
      print("Computing similar programs for {0}:".format(project))
      result_file = os.path.join(common.WORKING_DIR, args.dir, project+"_result.txt")
      kernel_file = os.path.join(common.WORKING_DIR, args.dir, project+"_kernel.txt")
      json_file = os.path.join(common.WORKING_DIR, args.dir, project+"_result.json") 
      check_similarity(project, result_file, kernel_file, dot_method_map, json_file, args.cluster, min(5,len(project_list)))

if __name__ == "__main__":
	main()
