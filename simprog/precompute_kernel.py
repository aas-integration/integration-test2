import sys, os, fnmatch
from kernel import GraphKernel

repo_dir = sys.argv[1]
kernel_file = sys.argv[2] # write to

num_iter = 3 # WL-Kernel iteration number

total_node_count = 0
total_relabel_count = 0

fo = open(kernel_file, 'w')
for r, ds, fs in os.walk(repo_dir):
	for f in fnmatch.filter(fs, '*.dot'):
		# build graph kerenel
		# print f
		gk = GraphKernel(f)
		gk.read_dot_graph(os.path.join(r, f))
		if len(sys.argv) == 4:			
			label_map = gk.read_cluster_info(sys.argv[3])
			relabel_count = gk.relabel_graph(label_map)
			total_node_count += gk.g.number_of_nodes()
			total_relabel_count += relabel_count
			print("Relabeled {0} out of {1} nodes in {2}.".format(relabel_count, gk.g.number_of_nodes(), gk.name))
		gk.init_wl_kernel()
		wls = gk.compute_wl_kernel(num_iter)
		wl_str = "###".join([";;;".join([",,,".join([str(x), str(y)]) for (x,y) in wl]) for wl in wls])
		fo.write(os.path.join(os.path.abspath(os.path.join(r, f)) +'\t' + wl_str + '\t' + str(gk.g.number_of_nodes()) + '\n'))
fo.close()

print("\n\nIn total, relabeled {0} nodes out of {1} nodes.\n".format(total_relabel_count, total_node_count))
