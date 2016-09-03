import sys, os, shutil

import inv_check
import insert_jaif
import ontology_to_daikon
import pa2checker

import backend
import common
sys.path.insert(0, 'simprog')
from similarity import Similarity

def main(corpus, result_file, ck_file="corpus_kernel"):
  """ SUMMARY: use case of the user-driven functionality of PASCALI.
  """
  dot_to_method_map = {}
  corpus_dot_to_method_map = {}
  corpora = ["dyn4j", "jreactphysics3d", "react", "jbox2d", "jmonkeyengine"]
  for project in [corpus]:
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
          #if project==corpus:
          corpus_dot_to_method_map[method_dot_path] = method_name
            #dot_to_method_map[method_dot_path] = method_name
          #else:
          #  dot_to_method_map[method_dot_path] = method_name
  sim = Similarity()
  sim.read_graph_kernels(os.path.join(common.WORKING_DIR, ck_file))
  top_k = 5
  iter_num = 3
  total = 0
  found_similar = 0
  fo = open(result_file, 'w')
  for dot_file in corpus_dot_to_method_map.keys():
    result_program_list_with_score = sim.find_top_k_similar_graphs(dot_file, dot_file, top_k, iter_num)
    line = dot_file+":\n"
    count = 0
    total +=1
    for (dot, score) in result_program_list_with_score:
      # TODO: filter and don't check against programs in the same project esp. itself
      if dot!=dot_file and score>=0.5:
        count += 1        
        line += dot+ " , " + str(score) + "\n"      
    line += "\n"
    if count > 0:
      fo.write(line)
      print line
      found_similar += 1
  fo.write("\nTotal number of methods examined: {0}\n".format(total))
  fo.write("Number of methods with at least one similar method (with a score >= 0.5) in another project: {0}\n".format(found_similar))
  fo.close()

if __name__ == '__main__':
  #corpus = common.get_project_list()
  #corpus = ["dyn4j", "jreactphysics3d", "react", "jbox2d", "jmonkeyengine"]
  #corpus = ["dyn4j"]
  corpus = sys.argv[1]
  result_file = sys.argv[2]
  ck_file = sys.argv[3]
  main(corpus, result_file, ck_file)
