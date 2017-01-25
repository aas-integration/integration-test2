import shutil, os
import pa2checker
import common

def run_pa2checker(ontology_values):
  pa2checker.revert_checker_source()

  for ontology_value, classes in ontology_values.iteritems():
    pa2checker.insert_ontology_value(ontology_value)
    pa2checker.update_ontology_utils(ontology_value, classes)
  common.recompile_checker_framework()

def run_inference(project):
  common.setup_checker_framework_env()

  classpath = os.path.join(os.environ['JSR308'], 'generic-type-inference-solver', 'bin')
  classpath += ':' + os.path.join(os.environ['JSR308'], 'ontology', 'bin')
  if os.environ.get('CLASSPATH'):
    os.environ['CLASSPATH'] += ':' + classpath
  else:
    os.environ['CLASSPATH'] = classpath

  project_dir = common.get_project_dir(project)
  annotation_dir = os.path.join(project_dir, common.DLJC_OUTPUT_DIR, 'annotations')

  if os.path.isdir(annotation_dir):
    shutil.rmtree(annotation_dir)

  common.run_dljc(project,
                  ['inference'],
                  ['--solverArgs=backEndType=maxsatbackend.MaxSat',
                   '--checker', 'ontology.OntologyChecker',
                   '--solver', 'ontology.solvers.backend.OntologyConstraintSolver',
                   '-m', 'ROUNDTRIP',
                   '--cache',
                   '-afud', annotation_dir])


def run(project_list):
  ontology_values = { "Sequence": ['java.util.List', 'java.util.LinkedHashSet'] }

  run_pa2checker(ontology_values)

  for project in project_list:
    common.clean_project(project)
    run_inference(project)

if __name__ == "__main__":
  run(['Sort07', 'Sort09', 'Sort10'])
