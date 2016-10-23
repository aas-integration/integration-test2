import numpy
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import os, sys, re
from collections import defaultdict
import argparse
import common
from nltk.stem.snowball import *

"""Read the program similarity result files and plot text similarity vs. program similarity"""

def compute_method_text_similarity(m1_full_str, m2_full_str, name_re, camel_re, stemmer):
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
    #m1_remove_len = len(m1_method_name) - len(m1_method_clean)
    #m2_remove_len = len(m2_method_name) - len(m2_method_clean)
    # (2):
    m1_word_lst = get_method_word_list(m1_method_clean, camel_re)
    m2_word_lst = get_method_word_list(m2_method_clean, camel_re)
    # (3):
    #m1_word_lst = [w.lower() for w in m1_word_lst]
    #m2_word_lst = [w.lower() for w in m2_word_lst]
    # (3):
    m1_stemmed_word_lst = [stemmer.stem(w) for w in m1_word_lst]
    m2_stemmed_word_lst = [stemmer.stem(w) for w in m2_word_lst]
    #m1_stem_len = sum([len(w) for w in m1_word_lst]) - sum([len(w) for w in m1_stemmed_word_lst])
    #m2_stem_len = sum([len(w) for w in m2_word_lst]) - sum([len(w) for w in m2_stemmed_word_lst])
    # (4):
    m1_word_dict = defaultdict(int)
    m2_word_dict = defaultdict(int)
    for w1 in m1_stemmed_word_lst:
        m1_word_dict[w1]+=1
    for w2 in m2_stemmed_word_lst:
        m2_word_dict[w2]+=1
    common_word_set = set(m1_stemmed_word_lst) & set(m2_stemmed_word_lst)
    common_word_len = 0
    for wd in common_word_set:
        common_word_len += len(wd)*2*min(m1_word_dict[wd], m2_word_dict[wd])
    # (5):
    score = float(common_word_len)/(sum([len(w) for w in m1_stemmed_word_lst]) + sum([len(w) for w in m2_stemmed_word_lst]))
    return score

def get_method_word_list(method_str, camel_re):
    word_lst = []
    for match in camel_re.finditer(method_str):
        word_lst.append(match.group(0))
    return word_lst

def compile_camel_case_re_pattern():
    return re.compile(r".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)")

def compile_method_re_pattern():
    return re.compile(r"<[\w\d_$\.]+\s*:\s+[\w\d_$.\[\]]+\s+<*([\w\d_$\']+)>*\([\[\].\w\d_$\,\s]*\)>")

def get_method_name_only(method_full_str, re_prog):
    #Example1: <org.dyn4j.dynamics.joint.RevoluteJoint: void setMotorEnabled(boolean)>
    #Example2: <com.flowpowered.react.math.Quaternion: float lengthSquare()>
    #Example3: <com.flowpowered.react.math.Quaternion: void <init>(float,float,float,float)>
    #Example4: <org.dyn4j.dynamics.joint.MotorJoint: java.lang.String toString()>
    #Example5: <org.dyn4j.dynamics.Body: java.util.List removeFixtures(org.dyn4j.geometry.Vector2)>
    #Example6: <com.jme3.material.plugins.ShaderNodeLoaderDelegate: com.jme3.shader.VariableMapping parseMapping(com.jme3.util.blockparser.Statement,boolean[])>
    #Example7: <org.dyn4j.geometry.Polygon: org.dyn4j.geometry.Vector2[] getAxes(org.dyn4j.geometry.Vector2[],org.dyn4j.geometry.Transform)>
    #Example8: <org.dyn4j.geometry.Vector3: org.dyn4j.geometry.Vector3 'to'(double,double,double)>
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

    stemmer = create_stemmer()
    name_re = compile_method_re_pattern()
    camel_re = compile_camel_case_re_pattern()

    count = 0
    current_dot = None
    with open(result_file, "r") as fi:
        for line in fi:                        
            line = line.rstrip('\n')
            if len(line)>0 and line[-1]==":":
                current_dot = line[:-1]
                current_method = dot_method_map[current_dot]
            else:                        
                linarr = line.split(" , ")
                if linarr[0][-3:]=="dot":
                    # consider most similar method only
                    if count == 0:
                        similar_method = dot_method_map[linarr[0]]
                        # compute word based similarity
                        prog_score = float(linarr[1])
                        text_score = compute_method_text_similarity(current_method, similar_method, name_re, camel_re, stemmer)
                        method_dict[current_method] = [similar_method, prog_score, text_score]
                    count += 1
                    if count == 5:
                        count = 0
        return method_dict

def plot_scatter(x, x_axis_label, y, y_axis_label, fig_file, title=""):
    pyplot.figure()
    pyplot.scatter(x, y)
    pyplot.title(title)
    pyplot.xlabel(x_axis_label)
    pyplot.ylabel(y_axis_label)
    pyplot.xlim(-0.05, 1.05)
    pyplot.ylim(-0.05, 1.05)
    pp = PdfPages(fig_file+".pdf")
    pyplot.savefig(pp, format="pdf")
    pp.close()

def main():

    parser = argparse.ArgumentParser()
    #parser.add_argument("-nc", "--nocluster", required=True, type=str, help="path to the result folder without relabeling")
    parser.add_argument("-c", "--cluster", required=True, type=str, help="path to the result folder with relabeling")
    parser.add_argument("-f", "--fig", type=str, help="path to the figure folder")
    parser.add_argument("-s", "--strategy", required=True, type=str, help="name of the strategy")

    args = parser.parse_args()

    proj_lst = common.LIMITED_PROJECT_LIST

    fig_dir = args.strategy+"_scatter"
    if args.fig:
        fig_dir = args.fig
    common.mkdir(fig_dir)
    
    dot_method_map = get_dot_method_map(proj_lst)

    for proj in proj_lst:
        proj_result_file_name = proj + "_result.txt"
        method_dict = parse_result_file(os.path.join(args.cluster, proj_result_file_name), dot_method_map)
        xs = []
        ys = []
        for m in method_dict.keys():
            xs.append(method_dict[m][1])
            ys.append(method_dict[m][2])
        plot_scatter(xs, "program similarity", ys, "word similarity", os.path.join(fig_dir, proj), proj+" : "+args.strategy)
        # correlation:
        print(proj+":")
        print(numpy.corrcoef(xs,ys))
        print("\n")

if __name__ == "__main__":
    main()
