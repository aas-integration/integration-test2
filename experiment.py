import frontend, backend, common
import argparse, os

def main():
  project_list = common.get_project_list()

  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--cluster", type=str, help="path to the json file that contains clustering information")
  parser.add_argument("-g", "--graph", action="store_true", help="set to regenerate graphs from the programs")
  parser.add_argument("-d", "--dir", type=str, required=True, help="directory to store precomputed kernels")
  parser.add_argument("-p", "--projects", type=str, help="A comma separated list of projects to work with.")
  args = parser.parse_args()

  if args.projects:
    arg_projects = args.projects.split(',')
    project_list = [project for project in project_list if project in arg_projects]

  common.mkdir(args.dir)
  backend.run(project_list, args)
  frontend.run(project_list, args)

if __name__ == '__main__':
  main()
