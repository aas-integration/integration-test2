# integration-test2
2nd big integration test of all tools

## Dependencies and Requirements (Docker)

- Docker

## Dependencies and Requirements (manual)

Tested on Ubuntu 14.04.

- Programs to download tool dependencies and build corpus projects
  - `sudo apt-get install ant git gradle maven mercurial python2.7-dev python-pip graphviz libgraphviz-dev curl`
- Java 8 JDK
  - JAVA_HOME environment variable must be set to the location of your JDK install.
- Python 3.6 or later
  - install required packages with `sudo pip install -r requirements.txt`
     - if you don't have sudo privileges, install with `pip install --user -r requirements.txt`, or create a virtual environment

## Setup (manual)

    ./fetch_dependencies.sh

This downloads all the jars and dependencies, and compiles them. Only needs to be run once unless you need to update tools.

    python fetch_corpus.py [<projectset>]

This fetches the corpus to be processed. With no arguments, `fetch_corpus.py` will download all available projects. It can also be given a named subset of the corpus (as defined at the start of `corpus.json`) or a list of projects to download.

## Setup (Docker)

To prepare the environment, run:

    docker build -t pascali_integration .

Our docker image expects that a directory will be mounted to its /persist mount point containing the `corpus.json` file, and `corpus` and `result` directories for storing the downloaded corpus and any generated results. On a Mac, however, Docker's shared filesystems are very slow, and this is not recommended.

If you want to use the shared filesystem, run the Docker image with

    docker run -it -v /path/to/persist:/persist --name pascali_integration pascali_integration

Otherwise, run

    docker run -it --name pascali_integration pascali_integration

Inside the container, run

    rm -rf corpus results corpus.json
    mkdir corpus results

Then, from another terminal, run

    docker cp corpus.json pascali_integration:/integration-test2/corpus.json

Whether using the /persist directory or not, you can then run (inside Docker)

    python fetch_corpus.py

## Running

After you've setup your environment, run the tools using the `run_set.sh` script. For example

    ./run_set.sh sci

Which processes the projects from the scientific computing corpus. This invokes the following tools:

  - [Bixie](http://sri-csl.github.io/bixie/): a bug finding tool that reports inconsistencies.
  - [Randoop](https://randoop.github.io/randoop/): A tool that automatically generates unit tests.
    See the [Randoop tutorial](https://github.com/randoop/tutorial-examples).
  - [Daikon](https://plse.cs.washington.edu/daikon/): A tool to infer likely invariants from recorded execution data.
    See the [Daikon tutorial](https://github.com/aas-integration/daikon-tutorial).
  - [Clusterer](https://github.com/aas-integration/clusterer): A tool to cluster classes and fields that are likely to be similiar based on their naming scheme.
  - [Partitions](https://github.com/aas-integration/partitions): A tool to cluster projects that are likely to serve a similar purpose.
  - [Checker-Framework-Inference](https://github.com/typetools/checker-framework-inference): A tool to propagate and infer type annotations (provided by clusterer).
  - Simprog: A tool that computes method similarity across projects (uses input from clusterer).

  ## Which outputs to look for:

  Output is stored in `results/<projectset>`. For example, `run_set.sh sci` stores its output in `results/sci`.
  Project specific outputs are stored in the `dljc-out/[PROJECT]` folder under the results folder. Project specific outputs include:

### Per-project outputs:

    - `bixie_report`: a human readable report of inconsistencies.
    - `javac.json`, `jars.json`, `stats.json`: various information about the build process.
    - `dot`: flow-graphs for each public method including a `methods.txt` file that maps dot file name to fully qualified method name, and `sourcelines.txt` that maps method names to source code
   locations.
    - `dot/*/kernel.txt`: pre-computed Weisfeiler-Lehman graph kernels for all computed graphs (this includes global relabeling information).
    - `test-classes*/`: generated unit tests.
    - `test-classes*/RegressionTestDriver.dtrace.gz`: recorded execution data for the generated unit tests.
    - `test-classes*/invariants.gz`: Likely invariants per method.
    - `jars/*.jar`: For projects that can build a jar, the jar files produced, including Checker Framework annotations.

### Cross-project outputs:

    - `clusters.json`: clustering of all classes in the corpus based on name similarity.
    - `class_field_map.json`: clustering of class-fields based on their type.
    - `word_based_field_clusters.json`: sub-clustering of each cluster in `class_field_map.json` based on name similarity. This is used, for example, to distinguish `Integers` that store `height` or `weight` from integers that store `socialSecurityNamber`.

**Find more details on the tools in the [Wiki](https://github.com/aas-integration/integration-test2/wiki)**
