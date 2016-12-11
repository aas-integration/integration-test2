import sys, os
import json
import argparse
import glob2 as glob

MAP_WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(MAP_WORKING_DIR, '..')))

import common, pa2checker, frontend_pa_inference

JAIF_FILE_ONTOLOGY_HEADER ="\
package ontology.qual:\n\
  annotation @Ontology:\n\
    enum ontology.qual.OntologyValue[] values\n"

def field_mappings_to_annotation(json_file):
    with open(json_file) as data_file:
        data = json.load(data_file)

    mappings = data["mappings"]
    ontology_set = set()
    project_list = common.get_project_list()

    for mapping in mappings:
        ontology_set.add(mapping['label'][0])

    convert_2_ontology_value(ontology_set)

    corpus_jaif_file = create_corpus_jaif(mappings)

    for project in project_list:
        refactor_multi_decl(project)

    for project in project_list:
        insert_anno_to_project(project, corpus_jaif_file)

    for project in project_list:
        frontend_pa_inference.run_inference(project)

def refactor_multi_decl(project):
    project_dir = common.get_project_dir(project)
    refactor_script = os.path.join(MAP_WORKING_DIR, "multiDeclRefactor", "run-refactor.sh")
    refactor_cmd = [refactor_script, project_dir]
    common.run_cmd(refactor_cmd)

def init_multi_decl_refactor():
    FETCH_TOOL_SCRIPT = os.path.join(MAP_WORKING_DIR, "fetch_map2anno_tools.sh")
    common.run_cmd(FETCH_TOOL_SCRIPT)

def type_mappings_to_rules(json_file):
    with open(json_file) as data_file:
        data = json.load(data_file)

    for mapping in data["type_mappings"]:
        ontology_value = mapping["ontology_value"]
        java_types = mapping["java_types"]
        pa2checker.insert_ontology_value(ontology_value)
        pa2checker.update_ontology_utils(ontology_value, java_types)

    pa2checker.recompile_checker_framework()

def insert_anno_to_project(project, jaif_file):
    """ Insert annotation info in the ${jaif_file} to ${project}.
    """
    project_dir = common.get_project_dir(project)
    with common.cd(project_dir):
        common.setup_checker_framework_env()
        insert_cmd = ['insert-annotations-to-source', '-i', jaif_file]
        # using glob2.glob to recursive get java files under project dir
        java_files = glob.glob('{}/**/*.java'.format(project_dir))
        insert_cmd.extend(java_files)
        common.run_cmd(insert_cmd, print_output=True)

def create_corpus_jaif(mappings):
    return create_jaif_file("corpus", mappings)

def create_jaif_file(project, mappings):
    """ create a {project_name}.jaif file under project_dir
        this jair file contains the insertted annotations info for this project
        Note: if ${project} value is "corpus", then it will create a "corpus.jaif" under corpus dir
    """
    if project == "corpus":
        project_dir = common.CORPUS_DIR
    else:
        project_dir = common.get_project_dir(project)

    jaif_file = os.path.join(project_dir, "{}.jaif".format(project))

    print ("Writing project {} annotated info to file {}".format(project, jaif_file))

    with open(jaif_file, 'w') as out_file:
        # write ontology package info
        out_file.write(JAIF_FILE_ONTOLOGY_HEADER)
        jaif_dict = dict()
        for mapping in mappings:
            for qualified_field in mapping['fields']:
                (package, clazz, field) = parse_field(qualified_field)
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
    return jaif_file

def parse_field(qualified_field):
    """ given a ${qualified_field} which describes a full qualified path to a class field with value like
        "xxx.xxx.xxx.Class.field", parse it to a tuple of package path, class name, and field name as
        (xxx.xxx.xxx, Class, field)
    """
    return tuple(qualified_field.rsplit('.', 2))

def convert_2_ontology_value(ontology_set):
    """ 1. clean up the ontology source code back to unchanged git version
        2. takes the ontology_set, and insert elements into ontology source as new ontologies
        3. re-compile ontology to make sure the insertions doesn't break the compilation
    """
    pa2checker.revert_checker_source()
    for new_ontology in ontology_set:
        pa2checker.insert_ontology_value(new_ontology)
    pa2checker.recompile_checker_framework()

def main():
    parser = argparse.ArgumentParser(description='command line interface for map2annotation')
    parser.add_argument('--type-mapping',dest='type_mapping_file')
    parser.add_argument('--field-mapping', dest='field_mapping_file')
    args = parser.parse_args()
    if args.type_mapping_file is None and args.field_mapping_file is None:
        print "error, required at least one mapping file to be indicated."
        parser.print_help()
        sys.exit(1)

    pa2checker.revert_checker_source()
    
    if not args.type_mapping_file is None:
        type_mappings_to_rules(args.type_mapping_file)

    if not args.field_mapping_file is None:
        field_mappings_to_annotation(args.field_mapping_file)

    project_list = common.get_project_list()

    for project in project_list:
        frontend_pa_inference.run_inference(project)

if __name__ == '__main__':
    main()
