import frontend, backend, common
import argparse, os

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

  common.mkdir(args.dir)
  kernel_dir = "kernel_directory"
  common.mkdir(kernel_dir)

  backend.run(project_list, args, kernel_dir)
  print("\n********* END OF BACKEND **********\n")
  frontend.run(project_list, args, kernel_dir)

if __name__ == '__main__':
  main()
