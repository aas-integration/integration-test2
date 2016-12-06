from common import DLJC_OUTPUT_DIR, get_project_dir
import os

def find_dot_name(method_name, method_file):
  with open(method_file, "r") as fi:
    for line in fi:
      line = line.rstrip()
      arr = line.split('\t')
      method_sig = arr[0]
      dot_name = arr[1]
      if method_name in method_sig:
        return dot_name
  return None

def dot_dir(project_name):
  return os.path.join(get_project_dir(project_name),
                      DLJC_OUTPUT_DIR,
                      "dot")

def dot_dirs(project_name):
  dd = dot_dir(project_name)

  if os.path.exists(dd):
    return os.listdir(dd)
  else:
    return None

def get_dot_path(project_name, output_dir, dot_name):
  return os.path.join(dot_dir(project_name),
                      output_dir,
                      dot_name)

def get_kernel_path(project_name, output_dir):
  return os.path.join(dot_dir(project_name), output_dir, 'kernel.txt')

def get_method_path(project_name, output_dir):
  return os.path.join(dot_dir(project_name), output_dir, 'methods.txt')

# def get_method_summary_from_dot_path(dot_path):
#   arr = dot_path.split(os.sep)
#   dot_name = arr[-1]
#   dot_dir = arr[:-1]
#   proj_dir = arr[:-3]
#   method_arr = dot_dir + ["methods.txt"]
#   method_file = os.path.join("/", *method_arr)
#   sourceline_arr = dot_dir + ["sourcelines.txt"]
#   sourceline_file = os.path.join("/", *sourceline_arr)
#   mf = open(method_file, "r")
#   sf = open(sourceline_file, "r")
#   dot_to_method_dict = {}
#   method_to_source_dict = {}
#   for line in mf:
#     line = line.rstrip()
#     arr = line.split('\t')
#     method_sig = arr[0]
#     dot = arr[1]
#     dot_to_method_dict[dot] = method_sig
#   mf.close()
#   for line in sf:
#     line = line.rstrip()
#     arr = line.split('\t')
#     method_sig = arr[0]
#     source_file_name = arr[1]
#     method_to_source_dict[method_sig] = source_file_name
#   sf.close()

#   method_sig = dot_to_method_dict[dot_name]
#   source_file = method_to_source_dict[method_sig]
#   source_path = os.path.join("/", *(proj_dir + ["src/main", source_file]))
#   new_method_sig = method_sig[1:-1]
#   sig_arr = new_method_sig.split(' ')
#   return source_path+"::"+sig_arr[2]+"::"+sig_arr[1]
