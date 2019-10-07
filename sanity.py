import os, json, re
import common

RESULTS_DIR = None

def project_dir(project):
  return os.path.join(RESULTS_DIR, 'dljc-out', project['name'])

def error(project, check, message):
  err = {'check': check, 'error': message}

  print('ERROR: [{proj}] - {check} - {msg}'.format(
    proj=project['name'],
    check=check,
    msg=message))

  return [err]

def check_daikon(project):
  # If dyntrace is enabled for this project
  if "dyntrace" in project['exclude']:
    return []
  # And there are some generated tests,
  # there should be invariants.gz in each test-classes folder
  # that corresponds to a test-src folder
  errors = []
  src_dirs = test_src_dirs(project)
  p_dir = project_dir(project)

  for d in src_dirs:
    m = re.match(r'test-src(\d+)', d)
    dirnum = m.group(1)
    inv_file = os.path.join(p_dir, 'test-classes{}'.format(dirnum), 'invariants.gz')
    if not os.path.exists(inv_file):
      errors.extend(error(project, 'daikon',
                          'No invariants found for generated tests #{}.'.format(dirnum)))

  return errors

def test_src_dirs(project):
  return [entry for entry in os.listdir(project_dir(project))
          if 'test-src' in entry]

def check_randoop_log(project):
  randoop_log = os.path.join(project_dir(project), 'randoop.log')
  errors = []

  lineno = 1

  with open(randoop_log) as f:
    for line in f.readlines():
      if "Randoop failed." in line:
        errors.extend(error(project, 'randoop', 'Randoop failed. See randoop.log:{}'.format(lineno)))
      lineno += 1

  return errors

def check_randoop(project):
  # If dyntrace is enabled for this project
  if "dyntrace" in project['exclude']:
    return []

  # There should be some generated tests
  # and no "randoop failed" in the randoop log
  errors = []

  errors.extend(check_randoop_log(project))
  if not test_src_dirs(project):
    errors.extend(error(project, 'randoop', 'No tests generated.'))

  return errors

def check_checker(project):
  # There should be an "Inference succeeded" in the checker framework log
  infer_log = os.path.join(project_dir(project), 'infer.log')
  successes = 0
  errors = []
  with open(infer_log) as f:
    lines = f.readlines()
    for line in lines:
      if "Inference succeeded" in line:
        successes += 1
      if "Inference failed" in line:
        errors.extend(error(project, 'checker', 'Inference failed.'))

  if successes == 0:
    errors.extend(error(project, 'checker', 'No successful inferences.'))

  return errors

def check_jars(project):
  # If there were jar instructions, there should be some generated jars
  if 'jar' not in project:
    return []

  jars_dir = os.path.join(RESULTS_DIR, 'jars', project['name'])
  jars = [f for f in os.listdir(jars_dir) if '.jar' in f]
  if not jars:
    return error(project, 'jars', 'Project has jar commmand, but no jars were built.')

  return []

def check_compiled(project):
  # There should be some DLJC results
  javac_json = os.path.join(project_dir(project), 'javac.json')
  with open(javac_json, 'r') as f:
    javac_results = json.load(f)

    if not javac_results:
      return error(project, 'compiled', 'No javac commands detected.')

    java_files = []

    for command in javac_results:
      java_files.extend(command['java_files'])

    if not java_files:
      return error(project, 'compiled', 'No java files compiled.')

  return []

# TODO - replace with annotation
ALL_CHECKS = [check_compiled, check_jars, check_checker, check_randoop, check_daikon]

def check_project(project):
  errors = []

  for check in ALL_CHECKS:
    # TODO - catch exceptions generated when checking
    errors.extend(check(project))

  return errors

def check_run(project_list, results_dir):
  global RESULTS_DIR
  RESULTS_DIR = results_dir

  errors = {}

  for project_name in project_list:
    project_info = common.project_info(project_name)
    errors[project_name] = {'project': project_info}
    errors[project_name]['errors'] = check_project(project_info)

  with open(os.path.join(results_dir, 'sanity.json'), 'w') as f:
    json.dump(errors, f)

  return errors
