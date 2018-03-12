import shutil, os, re
import xml.dom.minidom as md
import pa2checker
import common

def run_pa2checker(ontology_values):
  pa2checker.revert_checker_source()

  for ontology_value, classes in ontology_values.iteritems():
    pa2checker.insert_ontology_value(ontology_value)
    pa2checker.update_ontology_utils(ontology_value, classes)
  common.recompile_checker_framework()

def run_inference(project_name):
  common.setup_checker_framework_env()

  classpath = os.path.join(os.environ['JSR308'], 'generic-type-inference-solver', 'bin')
  classpath += ':' + os.path.join(os.environ['JSR308'], 'ontology', 'bin')
  if os.environ.get('CLASSPATH'):
    os.environ['CLASSPATH'] += ':' + classpath
  else:
    os.environ['CLASSPATH'] = classpath

  project_dir = common.get_project_dir(project_name)
  annotation_dir = os.path.join(project_dir, common.DLJC_OUTPUT_DIR, 'annotations')

  if os.path.isdir(annotation_dir):
    shutil.rmtree(annotation_dir)

  common.run_dljc(project_name,
                  ['inference'],
                  ['--solverArgs=backEndType=maxsatbackend.MaxSat',
                   '--checker', 'ontology.OntologyChecker',
                   '--solver', 'ontology.solvers.backend.OntologyConstraintSolver',
                   '-m', 'ROUNDTRIP',
                   '--cache',
                   '-afud', annotation_dir])

  print("Building annotated JAR for {}".format(project_name))
  build_jar(project_name)

def create_mvn_dep(tree):
  dep = tree.createElement('dependency')
  group = tree.createElement('groupId')
  group.appendChild(tree.createTextNode('pascaliUWat'))
  artifact = tree.createElement('artifactId')
  artifact.appendChild(tree.createTextNode('ontology'))
  version = tree.createElement('version')
  version.appendChild(tree.createTextNode('1.0'))
  dep.appendChild(group)
  dep.appendChild(artifact)
  dep.appendChild(version)
  return dep

def create_mvn_deps(tree):
  deps = tree.createElement('dependencies')
  deps.appendChild(create_mvn_dep(tree))
  return deps

def add_mvn_deps(project_dir):
  pom_file = os.path.join(project_dir, 'pom.xml')
  tree = md.parse(pom_file)
  project = tree.documentElement

  dependencies = project.getElementsByTagName('dependencies')
  if dependencies:
    dependencies[0].appendChild(create_mvn_dep(tree))
  else:
    project.appendChild(create_mvn_deps(tree))

  with open(pom_file, 'w') as f:
    xml = tree.toprettyxml()
    escaped_xml = xml.encode('ascii', 'xmlcharrefreplace')
    f.write(escaped_xml)

GRADLE_DEP_STRING = "\\1\n        implementation \"pascaliUWat:ontology:1.0\"\n"
GRADLE_SEARCH_PATTERN = r"(dependencies\s*{)"
GRADLE_SEARCH = re.compile(GRADLE_SEARCH_PATTERN, re.MULTILINE)

def add_gradle_deps(project_dir):
  gradle_file = os.path.join(project_dir, 'build.gradle')
  with open(gradle_file, 'r') as f:
    gradle_str = f.read()
  with open(gradle_file, 'w') as f:
    f.write(re.sub(GRADLE_SEARCH, GRADLE_DEP_STRING, gradle_str))

def build_jar(project_name):
  project = common.project_info(project_name)
  project_dir = common.get_project_dir(project_name)
  if 'jar' not in project:
    print('No jar command available, skipping {}.')
    return

  jar_cmd = project['jar'].strip().split()
  build_system = jar_cmd[0]

  if build_system == "mvn":
    add_mvn_deps(project_dir)
  elif build_system == "gradle":
    add_gradle_deps(project_dir)
  else:
    print("Don't know how to build jar file for {} projects".format(build_system))
    return

  with common.cd(project_dir):
    common.run_cmd(jar_cmd)

def run(project_list):
  ontology_values = { "Sequence": ['java.util.List', 'java.util.LinkedHashSet'] }

  run_pa2checker(ontology_values)

  for project_name in project_list:
    common.clean_project(project_name)
    run_inference(project_name)

if __name__ == "__main__":
  run(['Sort07', 'Sort09', 'Sort10'])
