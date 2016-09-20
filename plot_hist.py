import numpy
from matplotlib import pyplot
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
			if linarr[0][:-3]=="dot":
				count += 1
				score += float(linarr[1])
				if count==5:
					avg_score_vector.append(score/count)
					count = 0
					score = 0.0
	return avg_score_vector

def plot_hist(x, xlabel, y, ylabel):
	bins = numpy.linspace(0.0, 1.0, 100)
	pyplot.hist(x, bins, alpha=0.5, label=xlabel)
	pyplot.hist(y, bins, alpha=0.5, label=ylabel)
	pyplot.legend(loc="upper right")
	pyplot.show()

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("-r1", "--result1", required=true, type=str, help="path to the first result file")
	parser.add_argument("-r2", "--result2", required=true, type=str, help="path to the second result file")
	args = parser.parse_args()

	score1 = parse_result_file(args.result1)
	score2 = parse_result_file(args.result2)

	plot_hist(score1, "no_cluster", score2, "cluster")

if __name__ == "__main__":
	main()