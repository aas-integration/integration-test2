import numpy
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import os, sys, re
from collections import defaultdict
import argparse
import common, dot
from nltk.stem.porter import *

"""Read the program similarity result files and plot histograms"""
        
def parse_result_file(result_file):
    """
    file format: 
    path_to_dotA: 
    path_to_similar_dot1 , score
    ...
    path_to_similar_dot5 , score
    
    path_to_dotB:
    ...
    """
    dot_score_lst = []
    dot_sim_result = {}
  
    proj_lst = common.LIMITED_PROJECT_LIST
    match_count = defaultdict(int)

    count = 0
    score = 0.0
    current_dot = None
    with open(result_file, "r") as fi:
        for line in fi:                        
            line = line.rstrip('\n')
            if len(line)>0 and line[-1]==":":
                current_dot = line[:-1]
                dot_sim_result[current_dot] = []
            else:                        
                linarr = line.split(" , ")
                if linarr[0][-3:]=="dot":
                    if count == 0:
                        match_name = linarr[0].split(os.path.sep)[6] # quick hack to get the proj name
                        match_count[match_name] += 1
                    count += 1
                    score += float(linarr[1])
                    dot_sim_result[current_dot].append((linarr[0],linarr[1]))
                    if count==5:                                
                        dot_score_lst.append((current_dot, score/count))
                        count = 0
                        score = 0.0
        return (dot_score_lst, dot_sim_result, match_count)

def show_improvement(proj, dot_score_lst_nc, dot_score_lst_c, dot_sim_res_nc, dot_sim_res_c, dot_method_map, topk):
	nc_total = 0.0
	c_total = 0.0
	largest_impr = 0.0
        method_num = len(dot_score_lst_nc)
	impr_lst = []
	assert len(dot_score_lst_nc)==len(dot_score_lst_c), "Should have the same number of methods with or without clustering."
	for i in range(len(dot_score_lst_nc)):
            assert dot_score_lst_nc[i][0]==dot_score_lst_c[i][0], "Should be comparing the same dot."
            nc_total += dot_score_lst_nc[i][1]
            c_total += dot_score_lst_c[i][1]
            impr = dot_score_lst_c[i][1] - dot_score_lst_nc[i][1]
            if impr > largest_impr:
                largest_impr = impr
		#assert impr_score+0.00001>=0.0, "Clustering should not degrade the performance of similar program identification."
            impr_lst.append((dot_score_lst_nc[i][0], impr))
        impr_lst.sort(key=lambda x: x[1], reverse=True)
        total_impr = c_total - nc_total
	print("\n***************************\n")
	print("{0}:".format(proj))        
	print("Average score improvement per method: {0}.".format(total_impr/len(dot_score_lst_nc)))
	print("Percentage score improvement: {0}.".format(total_impr*100/nc_total))
	print("Largest score improvement for a single method: {0}.\n".format(largest_impr))
	print("The top {0} most improved methods are:\n".format(topk))
	for i in range(topk):
            dot_name = impr_lst[i][0]
            print(dot_method_map[dot_name]+" : average similarity score improved by " + str(impr_lst[i][1]))
            print("Before clustering:")
            nc_lst = dot_sim_res_nc[dot_name]
            for j in range(len(nc_lst)):
                print(dot_method_map[nc_lst[j][0]]+" , "+nc_lst[j][1])
            print("After clustering:")
            c_lst = dot_sim_res_c[dot_name]
            for j in range(len(c_lst)):
                print(dot_method_map[c_lst[j][0]]+" , "+c_lst[j][1])
            print("\n")
	print("\n***************************\n")
	# output some stats
	return (c_total, nc_total, method_num, largest_impr)

def plot_hist(x, xlabel, y, ylabel, fig_file, title=""):
	bins = numpy.linspace(0.0, 4.0, 100)
	#pyplot.hist(x, bins, alpha=0.5, label=xlabel)
	#pyplot.hist(y, bins, alpha=0.5, label=ylabel)
	data = numpy.vstack([x, y]).T
        pyplot.figure()
	pyplot.hist(data, bins, alpha=0.7, color=["white", "black"], hatch="//", label=[xlabel, ylabel])
	pyplot.legend(loc="upper right")        
	#pyplot.show()
        pyplot.title(title)
        pyplot.ylabel("number of program segments")
        pyplot.xlabel("similarity score")
	pyplot.xlim(0.0, 1.0)
	pp = PdfPages(fig_file+".pdf")
	pyplot.savefig(pp, format='pdf')
	pp.close()

def get_dot_method_map(proj_lst):
	dot_method_map = {}
	for proj in proj_lst:
            output_dir_lst = dot.dot_dirs(proj)
            for output_dir in output_dir_lst:
                method_file = dot.get_method_path(proj, output_dir)
                with open(method_file, "r") as mf:
                    for line in mf:
                        line = line.rstrip()
                        items = line.split("\t")
                        method_name = items[0]
                        method_dot = items[1]
                        method_dot_path = dot.get_dot_path(proj, output_dir, method_dot)
                        dot_method_map[method_dot_path] = method_name
	return dot_method_map

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("-nc", "--nocluster", required=True, type=str, help="path to the result folder without relabeling")
	parser.add_argument("-c", "--cluster", required=True, type=str, help="path to the result folder with relabeling")
	parser.add_argument("-f", "--fig", type=str, help="path to the figure folder")
	parser.add_argument("-s", "--strategy", required=True, type=str, help="name of the strategy")
	parser.add_argument("-k", "--topk", type=int, help="top k most improved methods")
	#parser.add_argument("-a", "--all", action="store_true", help="set to merge results from all benchmark projects in a single histogram")
	args = parser.parse_args()

        strategy = "strategy"
        if args.strategy:
            strategy = args.strategy

	proj_lst = common.LIMITED_PROJECT_LIST

        fig_dir = strategy+"_hist"
        if args.fig:
            fig_dir = args.fig
	common.mkdir(fig_dir)

	dot_method_map = get_dot_method_map(proj_lst)

	topk = 10
	if args.topk:
            topk = args.topk

	all_score_lst_nc = []
	all_score_lst_c = []

        all_c_total = 0.0
        all_nc_total = 0.0
        all_largest_impr = 0.0
        all_method_num = 0
	for proj in proj_lst:
	    proj_result_file_name = proj + "_result.txt"
	    (dot_lst_nc, dot_res_nc, match_count_nc) = parse_result_file(os.path.join(args.nocluster, proj_result_file_name))
	    (dot_lst_c, dot_res_c, match_count_c) = parse_result_file(os.path.join(args.cluster, proj_result_file_name))
	    score_lst_nc = [x[1] for x in dot_lst_nc]
	    score_lst_c = [x[1] for x in dot_lst_c]            
            (c_total, nc_total, method_num, largest_impr) = show_improvement(proj, dot_lst_nc, dot_lst_c, dot_res_nc, dot_res_c, dot_method_map, topk)
            
            print("\n***************************\n")
            print("{0} after clustering:".format(proj))
            for match in list(match_count_c.keys()):
                print("Number of matched methods in {0}: {1}".format(match, match_count_c[match]))
            print("\n***************************\n")

            all_c_total += c_total
            all_nc_total += nc_total
            all_method_num += method_num
            if largest_impr > all_largest_impr:
                all_largest_impr = largest_impr
            all_score_lst_nc += score_lst_nc
            all_score_lst_c += score_lst_c
	    
            plot_hist(score_lst_nc, "w/o clustering", score_lst_c, strategy, os.path.join(fig_dir, proj), proj+" : "+strategy)
            print("\n")
	
        all_avg_impr = (all_c_total - all_nc_total)/all_method_num
        all_percent_impr = (all_c_total - all_nc_total)*100/all_nc_total
        plot_hist(all_score_lst_nc, "w/o clustering", all_score_lst_c, strategy, os.path.join(fig_dir, strategy), "all : "+strategy)
        print("Average score improvement across projects: {0}".format(all_avg_impr))
        print("Percentage score improvement across projects: {0}".format(all_percent_impr))
        print("Largest score improvement for a single method: {0}".format(all_largest_impr))

if __name__ == "__main__":
    main()
