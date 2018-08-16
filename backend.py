import os, sys
import common
import dot

import map2annotation

def generate_graphs(project):
  """Run dljc
  Generate program graphs using prog2dfg
  Precompute graph kernels that are independent of ontology stuff
  """
  common.run_dljc(project,
                  ['graphtool'],
                  ['--graph-jar', common.get_jar('prog2dfg.jar'),
                   '--cache'])

def generate_dtrace(project):
  common.run_dljc(project,
                  ['dyntrace'], ['--cache', '--daikon-xml'])


def gather_kernels(projects, corpus_kernel_file):
  print("Gathering kernels from projects {0}".format(" and ".join(projects)))
  with open(corpus_kernel_file, "w") as corpus_kernel_file_handle:
    for project in projects:
      project_dir = common.get_project_dir(project)
      out_dir = dot.dot_dirs(project)[0] # only consider the first one
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
    graph_kernel_cmd = ['python',
                        common.get_simprog('precompute_kernel.py'),
                        project_dir,
                        kernel_file_path,
                        cluster_json
                        ]
    common.run_cmd(graph_kernel_cmd, 'graphkernel')
  else:
    graph_kernel_cmd = ['python',
                        common.get_simprog('precompute_kernel.py'),
                        project_dir,
                        kernel_file_path
                        ]
    common.run_cmd(graph_kernel_cmd, 'graphkernel')

def compute_clusters_for_classes(project_list, out_file_name, cf_map_file_name, wf_map_file_name):
  class_dirs = list()
  for project in project_list:
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

  common.run_cmd(clusterer_cmd, 'clusterer')

  # Check if the file exists and is not empty.
  if os.path.exists(wf_map_file_name) and os.path.getsize(wf_map_file_name) > 0:
    print ("Generate jaif file")
    map2annotation.field_mappings_to_annotation(project_list, wf_map_file_name)
    for project in project_list:
        map2annotation.run_anno_inference(project)
  else:
    print("Warning: Missing or empty {0} file.".format(wf_map_file_name))
    print("Warning: map2annotation won't be executed.")


def run(project_list, args, kernel_dir):
  cluster_file = os.path.join(args.dir, common.CLUSTER_FILE)
  c2f_file = os.path.join(args.dir, common.CLASS2FIELDS_FILE)
  wfc_file = os.path.join(args.dir, common.WORDCLUSTERS_FILE)

  if os.path.isfile(cluster_file) and not args.recompute_clusters:
    print ("Using clusters from: {0}".format(cluster_file))
  else:

    # first compile everything using dljc to get the class dirs.
    print("Building projects and populating dljc cache")
    for project in project_list:
      common.clean_project(project)
      common.run_dljc(project)

    for project in project_list:
      common.run_dljc(project, ['bixie'], ['--cache'])

    # now run clusterer.jar to get the json file containing the clusters.
    compute_clusters_for_classes(project_list, cluster_file, c2f_file, wfc_file)
    
  for project in project_list:
    if args.graph:
      generate_graphs(project)

    generate_project_kernel(project, cluster_file)

  # gather kernels for one-against-all comparisons
  for project in project_list:
    pl = list(project_list) # create a copy
    pl.remove(project)
    gather_kernels(pl, os.path.join(kernel_dir, project+"_kernel.txt"))

  for project in project_list:
    generate_dtrace(project)
