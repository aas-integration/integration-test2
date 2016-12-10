# Tool name: Ontology Type Inference (OTI)

---

# General description

OTI supports other code analysis tools by propagating the ground truths about
ontic types in the corpus. For example, ontic types help to distinguish two
functions with the same Java types and control flow graphs. OTI takes a minimal
set of ground truths from other tools and then propagates them properly in the
corpus by type inference based on ontology type rules.


# Input and output of this tool

## Input

Ground truths about ontic types in the corpus.
A dictionary that contains:

1) mappings from Java types to an ontology concept, e.g.

    ```
    {
        "Sequence": [
            'TypeKind.ARRAY',
            'java.util.List'
        ]
    }
    ```

    This input tells OTI that Java `array` types and `java.util.List` are
    related to the ontology concept `Sequence`.

2) mappings from fields to an ontology concept, e.g.

    ```
    {
         "mappings": [
            {
             "fields":[
                "demo.package.Demo.externalVelocity",
             ],
             "label":[
                "velocity"
             ]
            },
            {
             "fields":[
                "demo.package.Demo.externalForce",
             ],
             "label":[
                "force"
             ]
            },
            ...
        ]
    }
    ```

    This input tells OTI that in package `demo.package`, there is a class `Demo`,
    whose field `externalVelocity` is related to ontology concept `velocity`,
    and field `externalForce` is related to ontology concept `force`.


## Output

The corpus annotated with `@Ontology` type annotations propagated from the ground
truths. For example, given the above mappings, the corpus would be annotated as
below:

Original file:

    ```java
    public class Demo {
        Vector externalVelocity;
        Vector externalForce;

        public void applyVelocity(Vector velocity) {
            externalVelocity.add(velocity);
        }

        public void applyForce(Vector force) {
            externalForce.add(force);
        }
    }
    ```

Annotated file:

    ```java
    import ontology.qual.Ontology;
    import ontology.qual.OntologyValue;

    public class Demo {
        @Ontology(OntologyValue.VELOCITY_3D) Vector externalVelocity;
        @Ontology(OntologyValue.FORCE_3D) Vector externalForce;

        public void applyVelocity(@Ontology(OntologyValue.VELOCITY_3D) Vector velocity) {
            ((@Ontology(OntologyValue.VELOCITY_3D) Vector) (externalVelocity.add(velocity)));
        }

        public void applyForce(@Ontology(OntologyValue.FORCE_3D) Vector force) {
            ((@Ontology(OntologyValue.FORCE_3D) Vector) (externalForce.add(force)));
        }
    }
    ```

Note how the input contained annotations for the two fields. These annotations
have been propagated to the method parameters and the polymorphic method
invocations.


Original file:

    ```java
    public static int [] sort(int [] unsorted) {
        int [] sorted = new int[unsorted.length];
        for (int i = 0; i < unsorted.length; i++) {
            sorted[i] = unsorted[i];
        }
        Arrays.sort(sorted);
        return sorted;
    }
    ```

Annotated file:

    ```java
    public static int @Ontology(OntologyValue.SEQUENCE) [] sort(int @Ontology(OntologyValue.SEQUENCE) [] unsorted) {
        int @Ontology(OntologyValue.SEQUENCE) [] sorted = new int[unsorted.length];
        for (int i = 0; i < unsorted.length; i++) {
            sorted[i] = unsorted[i];
        }
        Arrays.sort(sorted);
        return sorted;
    }
    ```

Note how the general rule for arrays applies in this example, resulting in
the `SEQUENCE` annotation on all array types.


# Process steps and data

- Steps

0. take a json file describing the mappings from Java types to ontology concepts
   and mappings from class fields to ontology concepts

1. update the OTI system
1.1 create new `OntologyValue` enum values in the `OntologyValue` class
1.2 insert mapping rules from Java types to ontolgoy values in
    the `OntologyUtils#determineOntologyValue()` method
1.3 re-compile OTI

2. create a .jaif file describing the annotation information on the class fields

3. insert ground truth type annotations into the corpus
   (Instead of performing steps 0-3, this can also be done manually by
   annotating fields with ground truths.)

4. run OTI on inserted corpus to further propagate type annotations


- Data: the corpus source code, before and after OTI.


- How to quantify the output:
  the number of ``@Ontology` annotations that have been inserted into the corpus.
  Before running OTI, the source code contains no `@Ontology` annotations.
  After running OTI, the source code contains `@Ontology` annotations marking
  the ontic types that occur in the application.


- Running the scripts for OTI

`mapping_2_annotation` module in `integration-test2` provides a command-line
interface for running OTI by giving mappings.

usage:

1. insert rules mapping Java types to ontology concepts, then annotating
the corpus based on these rules:

```bash
python map2annotation --type-mapping <type_mappings>.json
```

2. propagate annotations in the corpus by mappings from fields to an ontology
concept:

```bash
python map2annotation --field-mapping <field_mappings>.json
```

3. do both:

```bash
python map2annotation --type-mapping <type_mappings>.json --field-mapping <field_mappings>.json
```

Note: when called from the command line, `map2annotation` will clean the source
code of OTI before updating the type rules and Ontology values.

Note: for the json format of the mapping files, please refer to the examples in
`mapping_2_annotation/json_file_examples/`
