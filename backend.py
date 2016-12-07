import os, sys
import common
import dot
import argparse

def generate_graphs(project):
  """Run dljc
  Compile test sources
  Generate program graphs using prog2dfg
  Precompute graph kernels that are independent of ontology stuff
  """
  print("Generating graphs for {0}".format(project))
  common.run_dljc(project,
                  ['graphtool'],
                  ['--graph-jar', common.get_jar('prog2dfg.jar'),
                   '--cache'])

def generate_dtrace(project):
  #TODO: set the out file to common.get_dtrace_file_for_project(project)
  common.run_dljc(project,
                  ['dyntrace'], ['--cache'])  


def gather_kernels(projects, corpus_kernel_file):
  print("Gathering kernels from projects {0}".format(" and ".join(projects)))
  with open(corpus_kernel_file, "w") as corpus_kernel_file_handle:
    for project in projects:
      project_dir = common.get_project_dir(project)
      out_dir = dot.dot_dirs(project)[0]
      project_kernel_file_path = dot.get_kernel_path(project, out_dir)
      
      if os.path.isfile(project_kernel_file_path):
        with open(project_kernel_file_path, "r") as fi: 
            corpus_kernel_file_handle.write(fi.read())
      else:
        print ("No kernel file find for project {0}.\n   {1} is not a file.".format(
          project,
          project_kernel_file_path
          ))


def generate_project_kernel(project, cluster_json=None):
  """ run graph kernel computation """
  
  project_dir = common.get_project_dir(project)

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

def compute_clusters_for_classes(project_list, out_file_name, cf_map_file_name="./class_field_map.json", wf_map_file_name="./word_based_field_clusters.json"):
  class_dirs = list()
  for project in project_list:
    print common.get_class_dirs(project)
    class_dirs.extend(common.get_class_dirs(project))
  if len(class_dirs)<1:
    print("No class dirs found to cluster. Make sure you run dljc first.")
    return

  

  clusterer_cmd = ['java', '-jar', common.get_jar('clusterer.jar'),
                   '-cs', '3',
                   '-out', out_file_name,
                   '-cfm', cf_map_file_name,
                   '-wfm', wf_map_file_name,
                   '-dirs'
                  ]
  clusterer_cmd.extend(class_dirs)

  print (clusterer_cmd)

  common.run_cmd(clusterer_cmd, True) 

def run(project_list, args, kernel_dir):
  if os.path.isfile(common.CLUSTER_FILE) and not args.recompute_clusters:
    print ("Using clusters from: {0}".format(common.CLUSTER_FILE))
  else:
    #compute clusters. 
    # first compile everything using dljc to get the class dirs.
    for project in project_list:
      #TODO: If you don't clean stuff before, nothing
      #happens here. 
      common.clean_project(project)
      common.run_dljc(project, [], [])
    # now run clusterer.jar to get the json file containing the clusters.
    compute_clusters_for_classes(project_list, common.CLUSTER_FILE, common.CLASS2FIELDS_FILE)

  for project in project_list:
    if args.graph:
      #TODO: If you don't clean stuff before, nothing
      #happens here.
      #common.clean_project(project)
      generate_graphs(project)
      pass
    generate_project_kernel(project, common.CLUSTER_FILE)

  # gather kernels for one-against-all comparisons
  for project in project_list:
    pl = list(project_list) # create a copy
    pl.remove(project)
    gather_kernels(pl, os.path.join(common.WORKING_DIR, kernel_dir, project+"_kernel.txt"))

  for project in project_list:
    print ("Generate dtrace for {0}".format(project))
    #common.clean_project(project)
    generate_dtrace(project)
