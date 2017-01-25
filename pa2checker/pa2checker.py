import sys, os
import shutil, tempfile
import common

SOLVER_SRC_DIR = os.path.join(common.TOOLS_DIR, 'ontology', 'src', 'ontology')

def revert_checker_source():
  with common.cd(SOLVER_SRC_DIR):
    common.run_cmd(['git', 'clean', '-f', '.'])
    common.run_cmd(['git', 'checkout', '.'])

def insert_ontology_value(value_name):
  """ insert ontology value to the file
  tools/ontology/src/ontology/qual/OntologyValue.java
  which is the enum class manages all the ontology values, annotaion would be gnereated
  in the form of @Ontology(values="{OntologyValue.ontology_value_name}")
  """
  ontology_qual_dir = os.path.join(SOLVER_SRC_DIR, 'qual')
  ontology_value_file = os.path.join(ontology_qual_dir, 'OntologyValue.java')

  capitial_value_name = value_name.upper()

  insert_enum = "    {}(\"{}\"),\n".format(capitial_value_name, value_name.lower())
  botttom_enum = "BOTTOM(\"BOTTOM\");"

  with tempfile.NamedTemporaryFile(mode='w', suffix='.java') as out_file:
    with open(ontology_value_file, 'r') as proto_file:

      already_existed = False

      for line in proto_file.readlines():
        if insert_enum in line:
          already_existed = True;

        if botttom_enum in line:
          if not already_existed:
            out_file.write(insert_enum)

        out_file.write(line)

      out_file.flush()
      shutil.copyfile(out_file.name, ontology_value_file)

def update_ontology_utils(value_name, java_type_names):
  """ updates the file
  tools/ontology/src/ontology/util/OntologyUtils.java
  which decides which java types get annotated with which annotation.
  """

  if len(java_type_names)==0:
    print ("Can't do empty mapping")
    return

  ontology_util_dir = os.path.join(SOLVER_SRC_DIR, 'util')
  ontology_util_file = os.path.join(ontology_util_dir, 'OntologyUtils.java')
  upper_value_name = value_name.upper()

  with tempfile.NamedTemporaryFile(mode='w', suffix='.java') as out_file:
    with open(ontology_util_file, 'r') as proto_file:
      for line in proto_file.readlines():
        out_file.write(line)

        if "public static OntologyValue determineOntologyValue(TypeMirror type) {" in line:
          # This is where we add the new mapping
          out_file.write("        if (")
          conds = []
          for java_type in java_type_names:
            if java_type == "[]":
              #special case for handling arrays.
              conds+=["type.getKind().equals(TypeKind.ARRAY))"]
            else:
              conds+=["TypesUtils.isDeclaredOfName(type, \"{}\")".format(java_type)]
          out_file.write(" || ".join(conds))
          out_file.write("){\n")
          out_file.write("            return OntologyValue.{};\n".format(upper_value_name))
          out_file.write("         }\n")

        out_file.flush()
        shutil.copyfile(out_file.name, ontology_util_file)

def main():
  annotation = "Disco"
  insert_ontology_value(annotation)
  update_ontology_utils(annotation, ["java.util.Collection", "java.util.LinkedList"])
  common.recompile_checker_framework()


if __name__ == '__main__':
  main()
