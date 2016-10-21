import numpy
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import os, sys, re
import argparse
import common
from nltk.stem.porter import *

"""Read the program similarity result files and plot histograms"""

def compute_method_text_similarity(m1_full_str, m2_full_str, re_prog):	
    return 

def compile_camel_case_re_pattern():
	return re.compile(r".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)")

def compile_method_re_pattern():
	return re.compile(r"<[\w\d_$\.]+\s*:\s+[\w\d_$]+\s+([\w\d_$]+)\([\w\d_$\.\s]*\)>\s")

def get_method_name_only(method_full_str, re_prog):
	#Example: <org.dyn4j.dynamics.joint.RevoluteJoint: void setMotorEnabled(boolean)>
	m = re_prog.match(method_full_str)
	if m:
		return m.group(1)
	else:
		print("Should always find a method name. The fully qualitified method name was:")
		print(method_full_str)
		sys.exit(0)

def create_stemmer():
	return SnowballStemmer('english')

def stem_word_lst(stemmer, word_lst):
	return [stemmer.stem(w) for w in word_lst]

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
                                        count += 1
                                        score += float(linarr[1])
                                        dot_sim_result[current_dot].append((linarr[0],linarr[1]))
                                        if count==5:                                
                                                dot_score_lst.append((current_dot, score/count))
                                                count = 0
                                                score = 0.0
        return (dot_score_lst, dot_sim_result)

def show_improvement(proj, dot_score_lst_nc, dot_score_lst_c, dot_sim_res_nc, dot_sim_res_c, dot_method_map, topk):
	total = 0.0
	impr_lst = []
	assert len(dot_score_lst_nc)==len(dot_score_lst_c), "Should have the same number of methods with or without clustering."
	for i in range(len(dot_score_lst_nc)):
		assert dot_score_lst_nc[i][0]==dot_score_lst_c[i][0], "Should be comparing the same dot."
		impr_score = dot_score_lst_c[i][1] - dot_score_lst_nc[i][1]
		#assert impr_score+0.00001>=0.0, "Clustering should not degrade the performance of similar program identification."
		impr_lst.append((dot_score_lst_nc[i][0], impr_score))
		total += impr_score
        impr_lst.sort(key=lambda x: x[1], reverse=True)
	print("\n***************************\n")
	print("{0}:\n".format(proj))        
	print("Total similarity score improvement: {0}.".format(total))
	print("Average similarity score improvement per method: {0}.\n".format(total/len(dot_score_lst_nc)))
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


def plot_hist(x, xlabel, y, ylabel, fig_file, perf_stat_lst):
	bins = numpy.linspace(0.0, 2.0, 100)
	#pyplot.hist(x, bins, alpha=0.5, label=xlabel)
	#pyplot.hist(y, bins, alpha=0.5, label=ylabel)
	data = numpy.vstack([x, y]).T
	pyplot.hist(data, bins, alpha=0.7, label=[xlabel, ylabel]+perf_stat_lst)
	pyplot.legend(loc="upper right")
	#pyplot.show()
	pp = PdfPages(fig_file+".pdf")
	pyplot.savefig(pp, format='pdf')
	pp.close()

def get_dot_method_map(proj_lst):
	dot_method_map = {}
	for proj in proj_lst:
		output_dir_lst = common.ALL_DOT_DIR[proj]
		for output_dir in output_dir_lst:
			method_file = common.get_method_path(proj, output_dir)
			with open(method_file, "r") as mf:
				for line in mf:
					line = line.rstrip()
					items = line.split("\t")
					method_name = items[0]
					method_dot = items[1]
					method_dot_path = common.get_dot_path(proj, output_dir, method_dot)
					dot_method_map[method_dot_path] = method_name
	return dot_method_map

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("-nc", "--nocluster", required=True, type=str, help="path to the result folder without relabeling")
	parser.add_argument("-c", "--cluster", required=True, type=str, help="path to the result folder with relabeling")
	parser.add_argument("-f", "--fig", required=True, type=str, help="path to the figure folder")
	parser.add_argument("-s", "-strategy", required=True, type=str, help="name of the strategy")
	parser.add_argument("-k", "--topk", type=int, help="top k most improved methods")
	parser.add_argument("-a", "--all", action="store_true", help="set to merge results from all benchmark projects in a single histogram")
	args = parser.parse_args()

	proj_lst = common.LIMITED_PROJECT_LIST
	common.mkdir(args.fig)

	dot_method_map = get_dot_method_map(proj_lst)

	topk = 10
	if args.topk:
		topk = args.topk

	all_score_lst_nc = []
	all_score_lst_c = []

	for proj in proj_lst:
	    proj_result_file_name = proj + "_result.txt"
	    (dot_lst_nc, dot_res_nc) = parse_result_file(os.path.join(args.nocluster, proj_result_file_name))
	    (dot_lst_c, dot_res_c) = parse_result_file(os.path.join(args.cluster, proj_result_file_name))
	    score_lst_nc = [x[1] for x in dot_lst_nc]
	    score_lst_c = [x[1] for x in dot_lst_c]
	    if args.all:
	    	all_score_lst_nc += score_lst_nc
	    	all_score_lst_c += score_lst_c
	    else:
                plot_hist(score_lst_nc, "w/o clustering", score_lst_c, args.strategy, os.path.join(args.fig, proj))
                show_improvement(proj, dot_lst_nc, dot_lst_c, dot_res_nc, dot_res_c, dot_method_map, topk)
                print("\n")
        if args.all:
            plot_hist(all_score_lst_nc, "w/o clustering", all_score_lst_c, args.strategy, os.path.join(args.fig, "all"))		

if __name__ == "__main__":
    main()
