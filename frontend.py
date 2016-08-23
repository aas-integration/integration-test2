import sys, os, shutil

import inv_check
import insert_jaif
import ontology_to_daikon
import pa2checker

import backend
import common
sys.path.insert(0, 'simprog')
from similarity import Similarity

def main(corpus):
  """ SUMMARY: use case of the user-driven functionality of PASCALI.
  """
  dot_to_method_map = {}
  for project in corpus:
    for output_dir in common.DOT_DIR[project]:
      method_file = common.get_method_path(project, output_dir)
      with open(method_file, "r") as mf:
        content = mf.readlines()
        for line in content:
          line = line.rstrip()
          items = line.split('\t')
          method_name = items[0]
          method_dot = items[1]
          method_dot_path = common.get_dot_path(project, output_dir, method_dot)
          dot_to_method_map[method_dot_path] = method_name
  sim = Similarity()
  sim.read_graph_kernels(os.path.join(common.WORKING_DIR, "corpus_kernel.txt"))
  top_k = 3
  iter_num = 3
  fo = open('corpus_similar_programs.txt', 'w')
  for dot_file in dot_to_method_map.keys():
    result_program_list_with_score = sim.find_top_k_similar_graphs(dot_file, 'g', top_k, iter_num)
    line = dot_to_method_map[dot_file]+":\n"
    #print dot_to_method_map[dot_file]+":"
    for (dot, score) in result_program_list_with_score:
      line += dot_to_method_map[dot]+ " , " + str(score) + "\n"
    line += "\n"
    fo.write(line)
    print line
  fo.close()

if __name__ == '__main__':
  #corpus = common.get_project_list()
  corpus = ["dyn4j", "jreactphysics3d"] 
  main(corpus)
