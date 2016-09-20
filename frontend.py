import sys, os, shutil

import inv_check
import insert_jaif
import ontology_to_daikon
import pa2checker

import backend
import common
import argparse
sys.path.insert(0, 'simprog')
from similarity import Similarity

<<<<<<< HEAD
def main(corpus, result_file, ck_file="corpus_kernel", cluster_json=None):
=======
def check_similarity(project, result_file, cluster_json=None):
>>>>>>> f3e5112efbd8f47a3330292b44dad697ec9154e4
  """ SUMMARY: use case of the user-driven functionality of PASCALI.
  """
  dot_to_method_map = {}
  corpus_dot_to_method_map = {}
  corpora = common.LIMITED_PROJECT_LIST

  # fetch various method information from each project in the list
  output_dir = common.DOT_DIR[project]
  method_file = common.get_method_path(project, output_dir)
  with open(method_file, "r") as mf:
    content = mf.readlines()
    for line in content:
      line = line.rstrip()
      items = line.split('\t')
      method_name = items[0]
      method_dot = items[1]
      method_dot_path = common.get_dot_path(project, output_dir, method_dot)
      corpus_dot_to_method_map[method_dot_path] = method_name

  # check similarity
  sim = Similarity()
  sim.read_graph_kernels(os.path.join(common.WORKING_DIR, ck_file))
  top_k = 5 # top k most similar methods
  iter_num = 3 # number of iteration of the WL-Kernel method
  fo = open(result_file, 'w')
  for dot_file in corpus_dot_to_method_map.keys():
    result_program_list_with_score = sim.find_top_k_similar_graphs(dot_file, dot_file, top_k, iter_num, cluster_json)
    line = dot_file+":\n"
    for (dot, score) in result_program_list_with_score:
      line += dot+ " , " + str(score) + "\n"      
    line += "\n"
  fo.close()

def main():

  project_list = common.LIMITED_PROJECT_LIST

  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--cluster", type=str, help="path to the json file that contains clustering information")
  parser.add_argument("-d", "--dir", type=str, required=True, help="directory to store similarity results")
  args = parser.parse_args()

  common.mkdir(args.dir)

  for project in project_list:
    result_file = os.path.join(common.WORKING_DIR, args.dir, project, "_", "result.txt")
    check_similarity(project, result_file, args.cluster)
    
if __name__ == '__main__':
<<<<<<< HEAD
  #corpus = common.get_project_list()
  #corpus = ["dyn4j", "jreactphysics3d", "react", "jbox2d", "jmonkeyengine"]
  corpus = sys.argv[1]
  result_file = sys.argv[2]
  ck_file = sys.argv[3]
  cluster_json = None
  if len(sys.argv)==5:
    cluster_json = sys.argv[4]
  main(corpus, result_file, ck_file, cluster_json)
=======
  main()
>>>>>>> f3e5112efbd8f47a3330292b44dad697ec9154e4
