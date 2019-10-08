import sys, os, time

from .similarity import Similarity
from .kernel import GraphKernel

def find_top_k_similar_program(repo_kernel_file, user_prog_graph_dot_file, graph_name, k, num_iter, cluster_json):
	sim = Similarity()
	sim.read_graph_kernels(repo_kernel_file)
	result_program_list_with_score = sim.find_top_k_similar_graphs(user_prog_graph_dot_file, graph_name, k, num_iter, cluster_json)
	return result_program_list_with_score

def main():
	repo_kernel_file = sys.argv[1]
	user_prog_graph_dot_file = sys.argv[2]
	top_k = int(sys.argv[3])
	cluster_json = None
	if len(sys.argv)==5:
		cluster_json = sys.argv[4]
	start = time.time()
	result_program_list = find_top_k_similar_program(repo_kernel_file, user_prog_graph_dot_file, user_prog_graph_dot_file, top_k, 3, cluster_json)
	end = time.time()
        print()
	for r in result_program_list:
		print(r)
	print("Time taken to find the similar dots: "+ str(end-start) + " seconds")

if __name__  == '__main__':
	main()
