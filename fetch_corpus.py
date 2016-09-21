import os
from common import mkdir, run_cmd, cd, CORPUS_DIR, get_corpus_info

def git_update(project):
  if project['git-ref'] not in run_cmd(['git', 'rev-parse', 'HEAD']):
    print "Checking out git ref %s." % project['git-ref']
    run_cmd(['git', 'fetch'])
    run_cmd(['git', 'reset' '--hard'])
    run_cmd(['git', 'checkout', project['git-ref']])

def hg_update(project):
  if run_cmd(['hg' 'parent']) != project['hg-rev']:
    print "Checking out hg rev %s." % project['hg-rev']
    run_cmd(['hg', 'update', '-r', project['hg-rev'], '-C'])

def svn_update(project):
  if run_cmd(['svnversion']) != project['svn-rev']:
    print "Checking out svn rev %s." % project['svn-rev']
    run_cmd(['svn', 'update', '-r', project['svn-rev']])

def download_project(project):
  if not os.path.isdir(project['name']):
    print "Downloading %s" % project['name']
    if 'git-url' in project:
      run_cmd(['git', 'clone',
                project['git-url'],
                project['name']])
    elif 'hg-url' in project:
      run_cmd(['hg', 'clone',
                project['hg-url'],
                project['name']])
    elif 'svn-url' in project:
      run_cmd(['svn', 'checkout',
                '{}@{}'.format(project['svn-url'], project['svn-rev']),
                project['name']])
  else:
    print "Already downloaded %s." % (project['name'])

def update_project(project):
  with cd(project['name']):
    if 'git-url' in project:
      git_update(project)
    elif 'hg-url' in project:
      hg_update(project)
    elif 'svn-url' in project:
      svn_update(project)

def main():
  mkdir(CORPUS_DIR)
  with cd(CORPUS_DIR):
    for project in get_corpus_info()['projects'].values():
      download_project(project)
      update_project(project)

if __name__ == "__main__":
  main()
