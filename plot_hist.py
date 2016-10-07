import numpy
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import os, sys
import argparse

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
	avg_score_vector = []

	count = 0
	score = 0.0
	with open(result_file, "r") as fi:
		for line in fi:
			line = line.rstrip('\n')
			linarr = line.split(" , ")
			if linarr[0][-3:]=="dot":
				count += 1
				score += float(linarr[1])
				if count==5:
					avg_score_vector.append(score/count)
					count = 0
					score = 0.0
	return avg_score_vector

def show_improvement(avg_score_vector_nc, avg_score_vector_c):
	total = 0.0
	assert len(avg_score_vector_nc)==len(avg_score_vector_c), "Should have the same number of methods with or without clustering."
	for i in range(len(avg_score_vector_nc)):
		assert avg_score_vector_nc[i]<=avg_score_vector_c[i], "Clustering cannot degrade the performance of similar program identification."
		total += avg_score_vector_c[i] - avg_score_vector_nc[i]
	print("Total similarity score improvement: {0}.".format(total))
	print("Average similarity score improvement per method: {0}.".format(total/len(avg_score_vector_c)))

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

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("-nc", "--nocluster", required=True, type=str, help="path to the result file without relabeling")
	parser.add_argument("-c", "--cluster", required=True, type=str, help="path to the result file with relabeling")
	parser.add_argument("-f", "--file", required=True, type=str, help="name of the pdf figure (without the .pdf extension")
	args = parser.parse_args()

	score1 = parse_result_file(args.nocluster)
	score2 = parse_result_file(args.cluster)

	plot_hist(score1, "no cluster", score2, "cluster", args.file)

	show_improvement(score1, score2)

if __name__ == "__main__":
	main()
