import numpy
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import os, sys
import argparse
import common

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
	avg_score_lst = []
        dot_lst = []

	count = 0
	score = 0.0
        dot_name = None
	with open(result_file, "r") as fi:
		for line in fi:
			line = line.rstrip('\n')
                        if len(line)>0 and line[-1]==":":
                                dot_name = line[:-1]
                        else:
                                linarr = line.split(" , ")
                                if linarr[0][-3:]=="dot":
                                        count += 1
                                        score += float(linarr[1])
                                        if count==5:
                                                avg_score_lst.append(score/count)
                                                dot_lst.append(dot_name)
                                                count = 0
                                                score = 0.0
	return (dot_lst, avg_score_lst)

def show_improvement(avg_score_lst_nc, avg_score_lst_c, dot_lst, dot_method_map, topk=10):
	total = 0.0
        impr_lst = []
	assert len(avg_score_lst_nc)==len(avg_score_lst_c), "Should have the same number of methods with or without clustering."
	for i in range(len(avg_score_lst_nc)):
		#assert avg_score_lst_nc[i]<=avg_score_lst_c[i], "Clustering cannot degrade the performance of similar program identification."
                impr_lst.append(avg_score_lst_c[i] - avg_score_lst_nc[i])
		total += avg_score_lst_c[i] - avg_score_lst_nc[i]
        impr_pairs = list(zip(dot_lst, impr_lst))
        impr_pairs.sort(key=lambda x: x[1], reverse=True)
	print("Total similarity score improvement: {0}.".format(total))
	print("Average similarity score improvement per method: {0}.".format(total/len(avg_score_lst_c)))
        print("The top {0} most improved methods are:".format(topk))
        for i in range(topk):
                print(dot_method_map[impr_pairs[i][0]]+" : score improved by " + str(impr_pairs[i][1]))

def plot_hist(x, xlabel, y, ylabel, fig_file):
	bins = numpy.linspace(0.0, 2.0, 100)
	#pyplot.hist(x, bins, alpha=0.5, label=xlabel)
	#pyplot.hist(y, bins, alpha=0.5, label=ylabel)
	data = numpy.vstack([x, y]).T
	pyplot.hist(data, bins, alpha=0.7, label=[xlabel, ylabel])
	pyplot.legend(loc="upper right")
	#pyplot.show()
	pp = PdfPages(fig_file+".pdf")
	pyplot.savefig(pp, format='pdf')
	pp.close()

def get_dot_method_map(proj_lst):
	dot_method_map = {}
	for proj in proj_lst:
		output_dir = comon.DOT_DIR[proj]
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
	args = parser.parse_args()

    proj_lst = common.LIMITED_PROJECT_LIST
    common.mkdir(args.fig)

    dot_method_map = get_dot_method_map(proj_lst)

    for proj in proj_lst:
    	proj_result_file_name = proj + "_result.txt"
        (dot_lst1, score1) = parse_result_file(os.path.join(args.nocluster, proj_result_file_name))
       	(dot_lst2, score2) = parse_result_file(os.path.join(args.cluster, proj_result_file_name))
        plot_hist(score1, "no cluster", score2, "cluster", os.path.join(args.fig, proj))
        show_improvement(score1, score2, dot_lst1, dot_method_map)
        print()

if __name__ == "__main__":
	main()
