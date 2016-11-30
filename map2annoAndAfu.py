import sys, os
import subprocess32 as subprocess
import json
import glob2 as glob
# assume pa2checker is under the same dir of this script
import common, pa2checker, frontend_pa_inference

MAP_WORKING_DIR = os.path.dirname(os.path.realpath(__file__))

JAIF_FILE_ONTOLOGY_HEADER ="\
package ontology.qual:\n\
  annotation @Ontology:\n\
    enum OntologyValue[] values\n"

def main():
    json_file = "<TBD>"
    
    with open(json_file) as data_file:
        data = json.load(data_file)

    mappings = data["mappings"]
    ontology_set = set()

    for mapping in mappings:
        ontology_set.add(mapping['label'][0])

    # convertToOntologyValue(ontology_set)

    # this is easy to extend to multiple projects
    Catalano_mappings = list()
    for mapping in mappings:
        # assume 'fields' at least has one element
        if (mapping['fields'][0].startswith('Catalano')):
            Catalano_mappings.append(mapping)

    createProjectJaifFile('catalano', Catalano_mappings)
    runInsertAnnoToProject('catalano')
    # frontend_pa_inference.run_inference('catalano')



def runInsertAnnoToProject(project):
    project_dir = common.get_project_dir(project)
    jaif_file = os.path.join(project_dir, "{}.jaif".format(project))
    with common.cd(project_dir):
        # clean project first for testing purpose, should think about whether should clean at this point
        # common.clean_project(project)
        common.setup_checker_framework_env()
        insert_cmd = ['insert-annotations-to-source', '-i', jaif_file]
        # using glob2.glob to recursive get java files under project dir
        java_files = glob.glob('{}/**/*.java'.format(project_dir))
        insert_cmd.extend(java_files)
        common.run_cmd(insert_cmd, print_output=True)

def createProjectJaifFile(project, mappings):
    """ create a {project_name}.jaif file under project_dir
        this jair file contains the insertted annotations info for this project
    """
    project_dir = common.get_project_dir(project)
    jaif_file = os.path.join(project_dir, "{}.jaif".format(project))

    print ("Writing project {} annotated info to file {}".format(project, jaif_file))

    with open(jaif_file, 'w') as out_file:
        # write ontology package info
        out_file.write(JAIF_FILE_ONTOLOGY_HEADER)
        jaif_dict = dict()
        for mapping in mappings:
            for qualified_field in mapping['fields']:
                (package, clazz, field) = parseField(qualified_field)
                if not package in jaif_dict:
                    jaif_dict[package] = dict()
                if not clazz in jaif_dict[package]:
                    jaif_dict[package][clazz] = dict()
                if not field in jaif_dict[package][clazz]:
                    jaif_dict[package][clazz][field] = set()

                # assume 'label' at least has one element
                jaif_dict[package][clazz][field].add(mapping['label'][0].upper())

        for package, classes in jaif_dict.items():
            out_file.write("\npackage {}:\n".format(package))
            for clazz, fields in classes.items():
                out_file.write("  class {}:\n".format(clazz))
                for field, value_set in fields.items():
                    out_file.write("    field {}:\n".format(field))
                    out_file.write("    @Ontology(values={{{value_name}}})\n".format(value_name=', '.join(value_set)))

def parseField(field):
    return tuple(field.rsplit('.', 2))

def convertToOntologyValue(ontology_set):
    """ 1. clean up the ontology source code back to unchanged git version
        2. takes the ontology_set, and insert elements into ontology source as new ontologies
        3. re-compile ontology to make sure the insertions doesn't break the compilation
    """
    pa2checker.revert_checker_source()
    for new_ontology in ontology_set:
        pa2checker.insert_ontology_value(new_ontology)
    pa2checker.recompile_checker_framework()

if __name__ == '__main__':
  main()