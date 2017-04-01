import frontend, backend, common
import argparse, os, shutil

def collect_stray_output(project_list, out_dir):
  dljc_out_dir = os.path.join(out_dir, common.DLJC_OUTPUT_DIR)
  common.mkdir(dljc_out_dir)

  jaif_out_dir = os.path.join(out_dir, "jaif")
  common.mkdir(jaif_out_dir)

  for project in project_list:
    dljc_in_dir = common.get_dljc_dir_for_project(project)
    shutil.move(dljc_in_dir, os.path.join(dljc_out_dir, project))

    shutil.move(os.path.join(common.get_project_dir(project), 'default.jaif'),
                os.path.join(jaif_out_dir, "{}.jaif".format(project)))

  shutil.move(os.path.join(common.CORPUS_DIR, 'corpus.jaif'),
              os.path.join(jaif_out_dir, 'corpus.jaif'))

def main():
  project_list = common.get_project_list()

  parser = argparse.ArgumentParser()

  
  parser.add_argument("-rc", "--recompute_clusters", action="store_true", help="recompute clustering for selected projects")
  parser.add_argument("-c", "--cluster", type=str, help="path to the json file that contains clustering information")
  parser.add_argument("-g", "--graph", action="store_true", help="set to regenerate graphs from the programs")
  parser.add_argument("-d", "--dir", type=str, required=True, help="The output directory")
  parser.add_argument("-p", "--projects", type=str, help="A comma separated list of projects to work with.")
  args = parser.parse_args()

  if args.projects:
    arg_projects = args.projects.split(',')
    project_list = [project for project in project_list if project in arg_projects]

  args.dir = os.path.abspath(os.path.join('results', args.dir))
  common.mkdir(args.dir)
  kernel_dir = os.path.join(args.dir, "kernel_directory")
  common.mkdir(kernel_dir)

  backend.run(project_list, args, kernel_dir)
  print("\n********* END OF BACKEND **********\n")
  frontend.run(project_list, args, kernel_dir)

  collect_stray_output(project_list, args.dir)

if __name__ == '__main__':
  main()
