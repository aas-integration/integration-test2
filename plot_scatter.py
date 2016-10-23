import numpy
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import os, sys, re
from collections import defaultdict
import argparse
import common
from nltk.stem.snowball import *

"""Read the program similarity result files and plot text similarity vs. program similarity"""

def compute_method_text_similarity(m1_full_str, m2_full_str, name_re, camel_re):
    # (0) get just the name of the method
    # (1) remove all non-letter characters in the name
    # (2) split using camel case 
    # (3) stem all words
    # (4) count the number of matched stemmed words (including duplicates)
    # (5) score = len(all matched words)/len(all stemmed words)
    # (0):
    m1_method_name = get_method_name_only(m1_full_str, name_re)
    m2_method_name = get_method_name_only(m2_full_str, name_re)
    # (1):
    m1_method_clean = re.sub("[\d$_]", "", m1_method_name)
    m2_method_clean = re.sub("[\d$_]", "", m2_method_name)
    m1_remove_len = len(m1_method_name) - len(m1_method_clean)
    m2_remove_len = len(m2_method_name) - len(m2_method_clean)
    # (2):
    m1_word_lst = get_method_word_list(m1_method_clean, camel_re)
    m2_word_lst = get_method_word_list(m2_method_clean, camel_re)
    return #TODO

def get_method_word_list(method_str, camel_re):
    return #TODO

def compile_camel_case_re_pattern():
    return re.compile(r".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)")

def compile_method_re_pattern():
    return re.compile(r"<[\w\d_$\.]+\s*:\s+[\w\d_$]+\s+<*([\w\d_$]+)>*\([\w\d_$\,\s]*\)>")

def get_method_name_only(method_full_str, re_prog):
    #Example1: <org.dyn4j.dynamics.joint.RevoluteJoint: void setMotorEnabled(boolean)>
    #Example2: <com.flowpowered.react.math.Quaternion: float lengthSquare()>
    #Example3: <com.flowpowered.react.math.Quaternion: void <init>(float,float,float,float)>
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

def parse_result_file(result_file, dot_method_map):
    """
    file format: 
    path_to_dotA: 
    path_to_similar_dot1 , score
    ...
    path_to_similar_dot5 , score
    
    path_to_dotB:
    ...
    """

    method_dict = {} # method_dict[method] = [similar_method, prog_score, text_score]

    method_re_prog = compile_method_re_pattern()
    camel_case_re_prog = compile_camel_case_re_pattern()

    current_dot = None
    with open(result_file, "r") as fi:
        for line in fi:                        
            line = line.rstrip('\n')
            if len(line)>0 and line[-1]==":":
                current_dot = line[:-1]
                current_method = dot_method_map[current_dot]
                method_dict[current_method] = []
            else:                        
                linarr = line.split(" , ")
                if linarr[0][-3:]=="dot":
                    # consider most similar method only
                    if count == 0:
                        similar_method = dot_method_map[linarr[0]]
                        method_dict[current_method].append(similar_method)
                        
                    count += 1
                    elif count == 5:
                        count = 0
        return (dot_score_lst, dot_sim_result, match_count)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-nc", "--nocluster", required=True, type=str, help="path to the result folder without relabeling")
    parser.add_argument("-c", "--cluster", required=True, type=str, help="path to the result folder with relabeling")
    parser.add_argument("-f", "--fig", type=str, help="path to the figure folder")
    parser.add_argument("-s", "--strategy", required=True, type=str, help="name of the strategy")

    args = parser.parse_args()

    proj_lst = common.LIMITED_PROJECT_LIST

    fig_dir = args.strategy+"_scatter"
    if args.fig:
        fig_dir = args.fig
    common.mkdir(fig_dir)


if __name__ == "__main__":
    main()
